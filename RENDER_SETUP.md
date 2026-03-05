# Render 部署配置指南

## 🔑 如何在 Render 上配置 API Key

### 方法一：通過 Render Dashboard（推薦）

1. **登入 Render Dashboard**
   - 訪問 https://dashboard.render.com/
   - 登入你的帳號

2. **選擇你的服務**
   - 在 Dashboard 中找到 `community-management-system` 服務
   - 點擊進入服務詳情頁

3. **進入環境變數設置**
   - 在左側導航欄找到 **"Environment"** 頁籤
   - 點擊進入環境變數設置頁面

4. **添加環境變數**
   - 點擊 **"Add Environment Variable"** 按鈕
   - 在 **Key** 欄位輸入：`OPENROUTER_API_KEY`
   - 在 **Value** 欄位輸入：你的實際 API Key（例如：`sk-or-v1-...`）
   - 點擊 **"Save Changes"**

5. **重新部署**
   - 環境變數設置後，Render 會自動觸發重新部署
   - 或者你可以手動點擊 **"Manual Deploy"** > **"Deploy latest commit"**

### 方法二：通過 Render CLI（可選）

如果你使用 Render CLI，可以在項目根目錄執行：

```bash
render env:set OPENROUTER_API_KEY=your-api-key-here
```

### 驗證配置

部署完成後，檢查日誌確認 API Key 是否正確加載：

1. 在 Render Dashboard 中進入你的服務
2. 點擊 **"Logs"** 頁籤
3. 查看啟動日誌，確認沒有 `OPENROUTER_API_KEY 未設置` 的錯誤訊息

### 獲取 OpenRouter API Key

1. 訪問 https://openrouter.ai/
2. 註冊/登入帳號
3. 前往 **API Keys** 頁面
4. 點擊 **"Create Key"** 創建新的 API Key
5. 複製 API Key（格式：`sk-or-v1-...`）

### 安全提示

✅ **推薦做法：**
- 在 Render Dashboard 中設置環境變數（不會出現在代碼中）
- 不要將 API Key 寫在 `render.yaml` 中
- 不要將 API Key 提交到 Git 倉庫

❌ **避免：**
- 在代碼中硬編碼 API Key
- 將 `.env` 文件提交到 Git
- 在公開的配置文件中暴露 API Key

## 📝 其他環境變數（可選）

如果需要配置其他環境變數，也可以在 Render Dashboard 中添加：

- `SECRET_KEY` - JWT 加密密鑰（如果未設置，會使用預設值）
- `DATABASE_URL` - 數據庫連接字串（如果使用外部數據庫）

## 🔍 故障排除

### 問題：智能搜索功能無法使用

**檢查步驟：**
1. 確認環境變數已正確設置（Dashboard > Environment）
2. 確認服務已重新部署
3. 查看日誌確認沒有錯誤訊息
4. 測試 API：`POST /api/smart-search`（需要 JWT 認證）

### 問題：環境變數未生效

**解決方法：**
1. 確認變數名稱完全正確：`OPENROUTER_API_KEY`（大小寫敏感）
2. 確認已保存並重新部署
3. 清除瀏覽器緩存後重試
