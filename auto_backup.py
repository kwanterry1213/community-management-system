import requests
import os
import datetime
import glob

# Configuration
APP_URL = "https://community-management-system-v0gq.onrender.com"
SECRET = "mvp_admin_secret_123"
# Windows 目標資料夾（請依需要自行修改）
DEST_FOLDER = r"C:\Users\Terry\Documents\Google Sync Folder"


def backup_database():
    """從雲端下載最新資料庫，存成 timestamp 檔案，然後執行「每天僅保留一份」清理策略。"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.db"

    print(f"[{datetime.datetime.now()}] 開始從 Render 備份資料庫...")

    try:
        if not os.path.exists(DEST_FOLDER):
            try:
                os.makedirs(DEST_FOLDER)
                print(f"已建立備份資料夾: {DEST_FOLDER}")
            except OSError as e:
                print(f"❌ 無法建立資料夾: {e}")
                return

        url = f"{APP_URL}/api/debug/db"
        response = requests.get(url, params={"secret": SECRET})

        if response.status_code == 200:
            filepath = os.path.join(DEST_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ 備份成功！已儲存為: {filepath}")

            clean_old_backups()
        else:
            print(f"❌ 備份下載失敗: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ 連線或寫入錯誤: {e}")


def clean_old_backups():
    """清理備份：每一天只保留「最新的一份」備份檔。"""
    print("正在執行備份清理策略（每天保留一份備份）...")

    search_pattern = os.path.join(DEST_FOLDER, "backup_*.db")
    files = glob.glob(search_pattern)

    if not files:
        print("沒有找到任何備份檔案。")
        return

    # 依修改時間新到舊排序
    files.sort(key=os.path.getmtime, reverse=True)

    daily_kept = {}  # key: 'YYYY-MM-DD', value: filepath
    deleted_count = 0

    for file_path in files:
        try:
            file_mod_time = os.path.getmtime(file_path)
            file_date = datetime.datetime.fromtimestamp(file_mod_time).strftime("%Y-%m-%d")

            if file_date not in daily_kept:
                daily_kept[file_date] = file_path
                continue

            os.remove(file_path)
            print(f"🗑️ 刪除多餘備份: {os.path.basename(file_path)} ({file_date})")
            deleted_count += 1
        except Exception as e:
            print(f"處理檔案 {file_path} 時發生錯誤: {e}")

    print(f"清理完成。共刪除 {deleted_count} 個檔案，保留 {len(daily_kept)} 天的備份。")


if __name__ == "__main__":
    print("=== 自動備份工具啟動 (Render -> 本機每日備份) ===")
    print(f"目標網址: {APP_URL}")
    print(f"儲存位置: {DEST_FOLDER}")
    print("提示：此腳本設計為由 Windows 工作排程『每天執行一次』。")
    backup_database()
