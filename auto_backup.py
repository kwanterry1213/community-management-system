import requests
import time
import os
import datetime

# 設定您的 Render 網址
APP_URL = "https://community-management-system-v0gq.onrender.com" 
# 設定密鑰 (需與 app.py 中的 ADMIN_SECRET 一致)
SECRET = "mvp_admin_secret_123"
# 備份間隔 (秒)
INTERVAL = 3600  # 每小時備份一次

def backup_database():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.db"
    
    print(f"[{datetime.datetime.now()}] 開始備份資料庫...")
    
    try:
        url = f"{APP_URL}/api/debug/db"
        response = requests.get(url, params={"secret": SECRET})
        
        if response.status_code == 200:
            # 確保 backups 資料夾存在
            if not os.path.exists("backups"):
                os.makedirs("backups")
                
            filepath = os.path.join("backups", filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ 備份成功！已儲存為: {filepath}")
            
            # 保留最新的 5 個備份，刪除舊的
            clean_old_backups()
        else:
            print(f"❌ 備份失敗: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 連線錯誤: {e}")

def clean_old_backups():
    try:
        files = [os.path.join("backups", f) for f in os.listdir("backups") if f.endswith(".db")]
        files.sort(key=os.path.getmtime)
        
        # 如果超過 5 個，刪除最舊的
        while len(files) > 5:
            oldest = files.pop(0)
            os.remove(oldest)
            print(f"🗑️ 已刪除舊備份: {oldest}")
    except Exception as e:
        print(f"清理舊備份時發生錯誤: {e}")

if __name__ == "__main__":
    print("=== 自動備份工具啟動 ===")
    print(f"目標網址: {APP_URL}")
    print(f"備份間隔: {INTERVAL} 秒")
    print("請確保您已將 APP_URL 修改為您 Render 部署後的實際網址！")
    
    # 首次執行先備份一次
    backup_database()
    
    while True:
        time.sleep(INTERVAL)
        backup_database()
