# 系統部署與遷移指南 (MacBook 專用版) 🍎

本指南將協助您將社群管理系統遷移至 MacBook 並順利運行。

## 1. 遷移前的準備 (在舊電腦上) 📦

為了讓檔案傳輸更快，建議先進行「瘦身」：

1.  **刪除多餘檔案**：進入 `h5-app` 資料夾，**刪除 `node_modules` 資料夾**。
    *   *原因*：這個資料夾通常有數百 MB，且包含 Windows 專用的格式，遷移到 Mac 後無法直接使用，刪除不影響系統運行。
2.  **打包專案**：複製整個 `community-management-system` 資料夾到隨身碟或雲端硬碟。
3.  **確認數據**：確保 `community_app.db` (會員資料庫) 在資料夾中，這是最重要的檔案。

## 2. MacBook 環境設定 ⚙️

在新的 Mac 上，您需要安裝 Python 來運行後端服務。

1.  **檢查 Python**：
    *   打開「終端機 (Terminal)」(按 `Cmd + Space` 搜尋 "Terminal")。
    *   輸入 `python3 --version`。如果不顯示版本號，請前往 [Python 官網](https://www.python.org/downloads/) 下載並安裝。
2.  **放置專案**：
    *   將專案資料夾複製到您的 Mac (例如放在「桌面」或「文件」)。

## 3. 安裝與啟動 🚀

### 步驟 A：進入專案目錄
1.  打開「終端機 (Terminal)」。
2.  輸入 `cd ` (注意 cd 後面有一個**空格**)。
3.  將專案資料夾從 Finder **直接拖入** 終端機視窗 (它會自動填入路徑)。
4.  按 **Enter** 鍵。

### 步驟 B：安裝依賴 (只需執行一次)
在終端機輸入以下指令並按 Enter：
```bash
pip3 install -r requirements.txt
```
*(如果出現權限錯誤，請嘗試 `pip3 install --user -r requirements.txt`)*

### 步驟 C：啟動伺服器
我們已經準備好了一個 Mac 專用的啟動腳本。

1.  **授權腳本** (只需做一次)：
    ```bash
    chmod +x start_server.sh
    ```
2.  **啟動系統**：
    ```bash
    ./start_server.sh
    ```
3.  **成功！**
    *   看到 `Server will be accessible at http://localhost:8000` 字樣即代表成功。
    *   現在打開 Safari 或 Chrome，訪問 [http://localhost:8000](http://localhost:8000) 即可使用系統。

## 4. 常見問題排除 🔧

*   **手機連不上？**
    *   請確保手機與 Mac 連接在**同一個 WiFi**。
    *   在 Mac 的「系統設定 -> 網路 -> Wi-Fi -> 詳細資訊」查看 Mac 的 IP (例如 `192.168.1.5`)。
    *   手機瀏覽器輸入 `http://192.168.1.5:8000`。
*   **指令找不到 (Command not found)？**
    *   如果是 `pip3` 找不到，試試看改用 `pip`。
    *   如果是 `./start_server.sh` 找不到，請確認您已經用 `cd` 進入了正確的資料夾。
