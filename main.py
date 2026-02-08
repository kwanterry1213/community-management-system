import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileWriterTool

# ==============================================
# 🔑 設定 OpenRouter API Key
# ==============================================
OPENROUTER_API_KEY = "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" # <--- 請填入你的 Key
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

# ==============================================
# 🧠 定義大腦
# ==============================================
# 1. 思考型 (PM 用)
llm_reasoning = LLM(
    model="openrouter/deepseek/deepseek-r1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.7
)

# 2. 實作型 (工程師 用)
llm_coding = LLM(
    model="openrouter/anthropic/claude-3.5-sonnet",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1
)

# 3. 審核型 (CTO 用)
llm_audit = LLM(
    model="openrouter/openai/o3-mini",
    api_key=OPENROUTER_API_KEY,
    temperature=0.2
)

file_write_tool = FileWriterTool()

# ==============================================
# 👥 定義角色
# ==============================================

# 1. PM
pm = Agent(
    role='Product Manager',
    goal='Define clear MVP requirements.',
    backstory="You are a pragmatic PM. You analyze the user's rough idea and list out the core features needed for an MVP.",
    verbose=True,
    llm=llm_reasoning
)

# 2. Designer
designer = Agent(
    role='UI/UX Designer',
    goal='Design Streamlit layout.',
    backstory="You design professional layouts for Streamlit apps based on requirements.",
    verbose=True,
    llm=llm_coding
)

# 3. Backend Dev
backend_dev = Agent(
    role='Backend Engineer',
    goal='Write app.py (FastAPI + SQLite).',
    backstory="You write monolithic FastAPI code. You always include all necessary imports and Pydantic models in one file.",
    verbose=True,
    llm=llm_coding
)

# 4. Frontend Dev
frontend_dev = Agent(
    role='Frontend Engineer',
    goal='Write ui.py (Streamlit).',
    backstory="You write Streamlit code that connects to the backend API.",
    verbose=True,
    llm=llm_coding
)

# 5. CTO
cto = Agent(
    role='CTO',
    goal='Review and Save files.',
    backstory="You review the code. If valid, you save `app.py` and `ui.py` using FileWriteTool.",
    verbose=True,
    tools=[file_write_tool],
    llm=llm_audit
)

# ==============================================
# 🏁 執行邏輯 (雙階段)
# ==============================================

if __name__ == "__main__":
    print("\n🚀 Himac AI 軟體工廠啟動中...")
    user_idea = input("老闆，請問今天要做什麼 App: ")

    # ---------------------------------------------------------
    # 第一階段：PM 提案 (Phase 1: Proposal)
    # ---------------------------------------------------------
    print("\n[Phase 1] PM 正在分析需求，請稍候...\n")
    
    task_draft_req = Task(
        description=f"Analyze the request: '{user_idea}'. List the Core MVP Features. Keep it simple.",
        expected_output="A list of features.",
        agent=pm
    )

    crew_phase1 = Crew(agents=[pm], tasks=[task_draft_req], verbose=True)
    initial_plan = crew_phase1.kickoff()

    # ---------------------------------------------------------
    # 🛑 老闆審核時間 (Human Review)
    # ---------------------------------------------------------
    print("\n\n========================================")
    print("📋 PM 建議的功能列表如下：")
    print("========================================")
    print(initial_plan)
    print("========================================")
    print("\n⚠️  審核時間：")
    print("1. 如果滿意，請直接按 [Enter] 繼續。")
    print("2. 如果要修改，請直接輸入新的要求 (例如：'刪除用戶登入功能，只需一個公開頁面')。")
    
    user_feedback = input("\n您的決定 > ")

    if user_feedback.strip():
        final_requirements = f"Original Idea: {user_idea}. \nUser's Adjusted Requirements: {user_feedback}. \n(Ignore previous PM suggestions if they conflict with User's Adjusted Requirements)."
        print("\n✅ 已更新需求，團隊將依照您的指示執行。")
    else:
        final_requirements = str(initial_plan)
        print("\n✅ 需求確認無誤，批准執行。")

    # ---------------------------------------------------------
    # 第二階段：開發與交付 (Phase 2: Execution)
    # ---------------------------------------------------------
    print("\n[Phase 2] 工程團隊進場，開始開發...\n")

    # 因為需求變更了，我們將「最終需求」直接注入到每個任務的描述中
    
    # Task 2: 設計
    task_design = Task(
        description=f"Based on these APPROVED requirements:\n{final_requirements}\n\nDesign the Streamlit layout.",
        expected_output="UI Layout Description",
        agent=designer
    )

    # Task 3: 後端
    task_backend = Task(
        description=f"Write `app.py` (FastAPI + SQLite) based on:\n{final_requirements}\n\nProtocol: Monolithic, Full Code.",
        expected_output="Python code for app.py",
        agent=backend_dev
    )

    # Task 4: 前端
    task_frontend = Task(
        description=f"Write `ui.py` (Streamlit) based on:\n{final_requirements}\n\nProtocol: Connect to Backend API.",
        expected_output="Python code for ui.py",
        agent=frontend_dev,
        context=[task_design] # 參考設計師的佈局
    )

    # Task 5: 存檔
    task_save = Task(
        description="Review `app.py` and `ui.py`. If correct, save them to disk using FileWriteTool.",
        expected_output="File save confirmation",
        agent=cto,
        context=[task_backend, task_frontend],
        tools=[file_write_tool]
    )

    crew_phase2 = Crew(
        agents=[designer, backend_dev, frontend_dev, cto],
        tasks=[task_design, task_backend, task_frontend, task_save],
        verbose=True,
        process=Process.sequential
    )

    crew_phase2.kickoff()
    
    print("\n\n################################################")
    print("## ✅ 專案開發完成！ ##")
    print("################################################")
    print("請執行以下指令啟動：")
    print("1. uvicorn app:app --reload")
    print("2. streamlit run ui.py")