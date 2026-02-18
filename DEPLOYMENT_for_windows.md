# 系統部署與遷移指南 (Windows 專用版) 🪟

本指南將協助您將社群管理系統遷移至另一台 Windows 電腦並順利運行。

## 1. 遷移前的準備 (在舊電腦上) 📦

為了讓檔案傳輸更快，建議先進行「瘦身」：

1.  **刪除多餘檔案**：進入 `h5-app` 資料夾，**刪除 `node_modules` 資料夾**。
    *   *原因*：這個資料夾通常有數百 MB，且包含舊電腦的專用格式。新電腦若只是要「運行」系統，並不需要它。
2.  **打包專案**：複製整個 `community-management-system` 資料夾到隨身碟或雲端硬碟。
3.  **確認數據**：確保 `community_app.db` (會員資料庫) 在資料夾中，這是最重要的檔案。

## 2. 新電腦環境設定 ⚙️

在新的 Windows 電腦上，您唯一需要安裝的是 Python。

1.  **下載 Python**：
    *   前往 [Python 官網](https://www.python.org/downloads/) 下載最新版 (建議 Python 3.10 以上)。
2.  **安裝關鍵步驟 (⚠️非常重要)**：
    *   在安裝畫面的最下方，**務必勾選 "Add Python to PATH"** (將 Python 加入環境變數)。
    *   然後點擊 "Install Now"。

## 3. 安裝與啟動 🚀

### 步驟 A：放置專案
1.  將專案資料夾複製到您的新電腦 (例如 `D:\community-system` 或桌面)。

### 步驟 B：安裝依賴 (只需執行一次)
1.  進入專案資料夾。
2.  在資料夾視窗的「網址列」輸入 `cmd` 並按 **Enter**，這會打開黑色命令視窗。
3.  輸入以下指令並按 Enter：
    ```cmd
    pip install -r requirements.txt
    ```
    *(看到 Successfully installed... 代表成功)*

### 步驟 C：啟動伺服器
我們已經準備好了一個 Windows 專用的啟動腳本。

1.  在資料夾中找到 **`start_server.bat`**。
2.  **雙擊執行** 它。
3.  **成功！**
    *   看到黑視窗顯示 `Server will be accessible at http://localhost:8000` 字樣即代表成功。
    *   現在打開 Edge 或 Chrome，訪問 [http://localhost:8000](http://localhost:8000) 即可使用系統。

## 4. 常見問題排除 🔧

*   **雙擊 `start_server.bat` 後視窗閃退？**
    1.  這通常代表環境還沒設定好 (例如 Python 沒裝好)。
    2.  請對 `start_server.bat` 按右鍵 -> 編輯。
    3.  在最後一行加上 `pause`，存檔。
    4.  再次執行，它會停住並顯示錯誤訊息，您可以截圖給我看。

*   **手機連不上？**
    *   請確保手機與電腦連在**同一個 WiFi**。
    *   查看電腦 IP：打開 cmd 輸入 `ipconfig`，找到 "IPv4 位址" (例如 `192.168.1.5`)。
    *   手機瀏覽器輸入 `http://192.168.1.5:8000`。
    *   *注意*：如果連不上，可能是 Windows 防火牆檔住了，請暫時關閉防火牆或允許 Python 通過防火牆。
