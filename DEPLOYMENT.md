# 快速部署指南 (Render.com) - 方案二：定時備份版

這是最快捷的 MVP 部署方式，使用 Render.com 免費層級，並搭配本地腳本解決資料庫重置問題。

## 部署步驟

1. **註冊 Render**
   - 前往 [dashboard.render.com](https://dashboard.render.com/) 註冊帳號。

2. **推送程式碼到 GitHub**
   - 確保您的程式碼已推送到 GitHub Repository。
   - `git add .`
   - `git commit -m "Prepare for Render deployment"`
   - `git push`

3. **在 Render 建立服務**
   - 點擊 "New +" -> "Web Service"。
   - 選擇 "Build and deploy from a Git repository"。
   - 連結您的 GitHub 帳號並選擇此專案的 Repository。

4. **設定 (自動)**
   - Render 應該會自動偵測到 `render.yaml` 檔案。
   - 如果偵測到，直接點擊 "Create Web Service"。

5. **取得網址**
   - 部署完成後，您會獲得一個網址 (例如 `https://community-app.onrender.com`)。

## 資料庫備份與還原 (重要！)

由於 Render 免費版會重置資料庫，請務必設定自動備份。

### 1. 設定備份腳本
打開 `auto_backup.py` 和 `restore_backup.py`，修改 `APP_URL` 為您的 Render 網址：
```python
APP_URL = "https://您的專案名稱.onrender.com"
```

### 2. 開始自動備份
在您的**本地電腦** (不是 Render 上) 執行：
```bash
# 安裝 requests 庫 (如果尚未安裝)
pip install requests

# 啟動自動備份 (建議保持此視窗開啟)
python auto_backup.py
```
這會每小時下載一份資料庫到 `backups/` 資料夾。

### 3. 如何還原資料
當 Render 重新部署導致資料消失時，您可以使用還原腳本將最新的備份推回去：

```bash
# 還原指定的備份檔案
python restore_backup.py backups/backup_2026xxxx_xxxxxx.db
```

## 安全性提醒
目前的 `ADMIN_SECRET` 設定為 `"mvp_admin_secret_123"`。
在正式公開前，建議您修改 `app.py`、`auto_backup.py` 和 `restore_backup.py` 中的這個密鑰，以避免他人惡意下載或覆蓋您的資料庫。
