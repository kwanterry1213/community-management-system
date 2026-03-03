import requests
import time
import os
import datetime
import glob

# Configuration
APP_URL = "https://community-management-system-v0gq.onrender.com" 
SECRET = "mvp_admin_secret_123"
# Using raw string for Windows path
DEST_FOLDER = r"C:\Users\Terry\Documents\Google Sync Folder"
INTERVAL = 3600  # Backup every hour
RETENTION_HOURS = 24

def backup_database():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.db"
    
    print(f"[{datetime.datetime.now()}] 開始從 Render 備份資料庫...")
    
    try:
        # 1. Ensure destination folder exists
        if not os.path.exists(DEST_FOLDER):
            try:
                os.makedirs(DEST_FOLDER)
                print(f"已建立備份資料夾: {DEST_FOLDER}")
            except OSError as e:
                print(f"❌ 無法建立資料夾: {e}")
                return

        # 2. Download from Render
        url = f"{APP_URL}/api/debug/db"
        response = requests.get(url, params={"secret": SECRET})
        
        if response.status_code == 200:
            filepath = os.path.join(DEST_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ 備份成功！已儲存為: {filepath}")
            
            # 3. Clean old backups
            clean_old_backups()
        else:
            print(f"❌ 備份下載失敗: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 連線或寫入錯誤: {e}")

def clean_old_backups():
    print(f"正在執行備份清理策略...")
    current_time = time.time()
    
    # Search for backup files in the destination folder
    search_pattern = os.path.join(DEST_FOLDER, "backup_*.db")
    files = glob.glob(search_pattern)
    
    # Sort files by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    
    daily_backups = {} # Key: Date string, Value: File path
    deleted_count = 0
    kept_count = 0
    
    for file_path in files:
        try:
            file_mod_time = os.path.getmtime(file_path)
            file_age_seconds = current_time - file_mod_time
            file_age_hours = file_age_seconds / 3600
            
            # Policy 1: Keep all backups within RETENTION_HOURS (24h)
            if file_age_hours <= RETENTION_HOURS:
                kept_count += 1
                continue
                
            # Policy 2: For older backups, keep one per day
            file_date = datetime.datetime.fromtimestamp(file_mod_time).strftime('%Y-%m-%d')
            
            if file_date not in daily_backups:
                daily_backups[file_date] = file_path
                kept_count += 1
                # print(f"保留每日備份: {os.path.basename(file_path)} ({file_date})")
            else:
                # Delete duplicate daily backup
                os.remove(file_path)
                print(f"🗑️ 刪除多餘備份: {os.path.basename(file_path)} ({file_date})")
                deleted_count += 1
                
        except Exception as e:
            print(f"處理檔案 {file_path} 時發生錯誤: {e}")

    print(f"清理完成。共刪除 {deleted_count} 個檔案，保留 {kept_count} 個備份。")

if __name__ == "__main__":
    print("=== 自動備份工具啟動 (Render -> Google Sync) ===")
    print(f"目標網址: {APP_URL}")
    print(f"儲存位置: {DEST_FOLDER}")
    print(f"備份間隔: {INTERVAL} 秒")
    print(f"保留時間: {RETENTION_HOURS} 小時")
    
    # Run immediately on start
    backup_database()
    
    while True:
        time.sleep(INTERVAL)
        backup_database()
