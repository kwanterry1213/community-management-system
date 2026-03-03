import os
from crewai import Agent, Task, Crew, Process, LLM
# ✅ 這是新版寫法，必須安裝 crewai-tools
from crewai_tools import FileReadTool

# date utilities for billing job
from datetime import datetime, timedelta
from app import get_db


def run_due_payment_job(community_id: int = None):
    db = get_db()
    cursor = db.cursor()
    cutoff = datetime.utcnow() + timedelta(days=30)
    cond = "WHERE expires_at IS NOT NULL AND status = 'active'"
    params = []
    if community_id is not None:
        cond += " AND community_id = ?"
        params.append(community_id)
    cursor.execute(f"SELECT * FROM memberships {cond}", params)
    memberships = cursor.fetchall()
    created = 0
    for m in memberships:
        expires = m['expires_at']
        if not expires:
            continue
        exp_dt = datetime.fromisoformat(expires)
        if exp_dt <= cutoff:
            cursor.execute(
                "SELECT 1 FROM payments WHERE related_type='membership' AND related_id=? AND status='pending'",
                (m['id'],),
            )
            if cursor.fetchone():
                continue
            cursor.execute(
                "INSERT INTO payments (user_id, community_id, description, amount, status, related_type, related_id, due_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    m['user_id'],
                    m['community_id'],
                    "會籍續費",
                    0.0,
                    "pending",
                    "membership",
                    m['id'],
                    expires,
                ),
            )
            created += 1
    db.commit()
    db.close()
    print(f"自動建立待繳帳單：{created}筆")

# ==============================================
# 🔑 設定 OpenRouter API Key (請填入你的 Key)
# ==============================================
OPENROUTER_API_KEY = "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" # <--- 請在此處貼上你的 API Key
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

# 定義大腦 (使用 DeepSeek)
himac_llm = LLM(
    model="openrouter/deepseek/deepseek-chat", 
    api_key=OPENROUTER_API_KEY
)

# ==============================================
# 🛠️ 定義工具：讓 AI 有眼睛看檔案
# ==============================================
# 這個工具讓 AI 可以讀取你電腦裡的 app.py, ui.py 等檔案
file_read_tool = FileReadTool()

# ==============================================
# 1. 定義角色：維護團隊
# ==============================================

# 角色：技術總監 (負責理解你的報錯，並檢查現有代碼)
tech_lead = Agent(
    role='Himac 技術總監 (Tech Lead)',
    goal='分析用戶反饋與現有代碼，制定精確的修改計劃',
    backstory="""你是經驗豐富的 Python 技術管理者。
    你的專長是 Debugging (除錯) 和 Code Review (代碼審查)。
    你非常謹慎，在修改代碼前，一定會先閱讀現有的檔案內容，
    確保不會破壞原本正常運作的功能。
    """,
    verbose=True,
    allow_delegation=True,
    tools=[file_read_tool], # 賦予讀檔權限
    llm=himac_llm
)

# 角色：維護工程師 (負責動手改)
maintenance_engineer = Agent(
    role='資深維護工程師 (Maintenance Engineer)',
    goal='根據總監的指示，重寫並輸出完整的代碼檔案',
    backstory="""你是執行力極強的工程師。
    你的工作是根據修改計畫，輸出「可直接執行」的完整 Python 代碼。
    你嚴格遵守以下原則：
    1. 輸出完整的檔案內容，不要只給片段。
    2. 確保修復了 Bug 或完成了新功能。
    3. 保持代碼整潔，加上必要的註解。
    """,
    verbose=True,
    allow_delegation=False,
    tools=[file_read_tool],
    llm=himac_llm
)

# ==============================================
# 2. 定義任務流程
# ==============================================
def create_fix_tasks(feedback, target_file):
    
    # 任務 1: 診斷 (由 Tech Lead 執行)
    task_diagnose = Task(
        description=f"""
        老闆 (用戶) 針對檔案 '{target_file}' 提出了以下反饋：
        "{feedback}"
        
        你的工作：
        1. 使用 FileReadTool 讀取 '{target_file}' 的完整內容。
        2. 分析代碼邏輯，找出問題所在。
        3. 如果是新增功能，思考應該插在哪個位置最合適。
        4. 如果是刪除功能，確認是否有相依性需要一併清理。
        
        請產出一份「修改計畫」，明確指出要改哪幾行、邏輯如何變更。
        """,
        expected_output='一份詳細的代碼修改計畫 (Step-by-step plan).',
        agent=tech_lead,
        tools=[file_read_tool]
    )

    # 任務 2: 修復 (由 Engineer 執行)
    task_fix = Task(
        description=f"""
        根據技術總監的修改計畫，重寫 '{target_file}'。
        
        ⚠️ 非常重要：
        1. 你必須輸出該檔案的 **完整原始碼 (Full Source Code)**。
        2. 請用 Markdown Code Block 包裹代碼 (例如 ```python ... ```)。
        3. 不要使用省略號 (...)，老闆需要直接複製貼上。
        """,
        expected_output=f'修改後完整的 {target_file} 代碼。',
        agent=maintenance_engineer,
        context=[task_diagnose] # 參考上一個任務的結果
    )
    
    return [task_diagnose, task_fix]

# ==============================================
# 3. 啟動維護總部
# ==============================================
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ("due", "generate_due", "auto_billing"):
        cid = int(sys.argv[2]) if len(sys.argv) > 2 else None
        run_due_payment_job(cid)
        sys.exit(0)
    print("\n================================================")
    print("🚑 Himac AI 維護團隊 (Bug Fix & Refactor) 已就位")
    print("================================================\n")
    
    # 1. 問老闆要改哪個檔案
    target_file = input("老闆，請問要修改哪個檔案 (例如 app.py 或 ui.py): ")
    
    # 2. 問老闆哪裡壞了
    print(f"\n請描述對 {target_file} 的修改需求 (例如: '修復加班計算錯誤' 或 '刪除某個按鈕'):")
    user_feedback = input("> ")
    
    # 建立團隊與流程
    crew = Crew(
        agents=[tech_lead, maintenance_engineer],
        tasks=create_fix_tasks(user_feedback, target_file),
        process=Process.sequential,
        verbose=True
    )

    print(f"\n⚙️ 團隊正在分析 {target_file}，請稍候...\n")
    result = crew.kickoff()
    
    print("\n\n################################################")
    print("## ✅ 維護完成！請複製下方代碼更新檔案 ##")
    print("################################################\n")
    print(result)