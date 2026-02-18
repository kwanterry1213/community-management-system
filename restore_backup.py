import requests
import sys
import os

# 設定您的 Render 網址 (請修改這裡)
APP_URL = "https://your-app-name.onrender.com" 
# 設定密鑰 (需與 app.py 中的 ADMIN_SECRET 一致)
SECRET = "mvp_admin_secret_123"

def restore_database(backup_file_path):
    if not os.path.exists(backup_file_path):
        print(f"錯誤: 找不到檔案 {backup_file_path}")
        return

    print(f"正在將 {backup_file_path} 還原至 {APP_URL}...")
    
    try:
        url = f"{APP_URL}/api/debug/db"
        params = {"secret": SECRET}
        files = {'file': open(backup_file_path, 'rb')}
        
        response = requests.post(url, params=params, files=files)
        
        if response.status_code == 200:
            print("✅ 資料庫還原成功！")
        else:
            print(f"❌ 還原失敗: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 連線錯誤: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python restore_backup.py <備份檔案路徑>")
        print("例如: python restore_backup.py backups/backup_20260218_120000.db")
    else:
        restore_database(sys.argv[1])
