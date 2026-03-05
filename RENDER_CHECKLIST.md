# Render 部署檢查清單 ✅

## 📋 部署前檢查

### 1. 環境變數配置

在 Render Dashboard > Environment 頁籤中，確認已設置以下環境變數：

#### 🔑 必需環境變數
- [ ] `OPENROUTER_API_KEY` - OpenRouter API Key（智能搜索功能必需）
  - 獲取方式：https://openrouter.ai/keys
  - 格式：`sk-or-v1-...`

#### 🔐 建議環境變數（可選但推薦）
- [ ] `SECRET_KEY` - JWT 加密密鑰（如果未設置，會使用預設值，不夠安全）
  - 生成方式：`python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - 長度建議：至少 32 字符

- [ ] `ALLOWED_ORIGINS` - CORS 允許的來源（生產環境建議設置）
  - 格式：`https://your-app.onrender.com,https://www.your-domain.com`
  - 多個域名用逗號分隔
  - 如果未設置，預設允許所有來源（`*`）

### 2. 文件檢查

確認以下文件存在且正確：

- [ ] `render.yaml` - Render 配置文件
- [ ] `render-build.sh` - 構建腳本（需要有執行權限）
- [ ] `requirements.txt` - Python 依賴列表
- [ ] `h5-app/package.json` - 前端依賴配置
- [ ] `.env.example` - 環境變數範例（可選）

### 3. 代碼檢查

- [ ] 確認 `app.py` 中沒有硬編碼的敏感信息
- [ ] 確認 `.gitignore` 包含 `.env` 文件
- [ ] 確認沒有將 API Key 寫在 `render.yaml` 中

### 4. 構建腳本檢查

確認 `render-build.sh` 包含：
- [ ] Python 依賴安裝：`pip install -r requirements.txt`
- [ ] 前端依賴安裝：`cd h5-app && npm install`
- [ ] 前端構建：`npm run build`
- [ ] 創建必要目錄：`mkdir -p uploads backups`

## 🚀 部署步驟

### 步驟 1：連接 Git 倉庫
1. 在 Render Dashboard 中創建新服務
2. 選擇 "Web Service"
3. 連接你的 Git 倉庫（GitHub/GitLab/Bitbucket）

### 步驟 2：配置服務設置
- **Name**: `community-management-system`（或你喜歡的名稱）
- **Environment**: `Python 3`
- **Build Command**: `./render-build.sh`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 步驟 3：設置環境變數
1. 進入服務詳情頁
2. 點擊 "Environment" 頁籤
3. 添加以下環境變數：
   ```
   OPENROUTER_API_KEY = your-actual-api-key-here
   SECRET_KEY = your-secret-key-here (可選但推薦)
   ALLOWED_ORIGINS = https://your-app.onrender.com (可選)
   ```

### 步驟 4：部署
1. 點擊 "Manual Deploy" > "Deploy latest commit"
2. 等待構建完成（通常需要 3-5 分鐘）
3. 查看 Logs 確認沒有錯誤

## 🔍 部署後驗證

### 1. 檢查服務狀態
- [ ] 服務狀態顯示為 "Live"
- [ ] 訪問服務 URL 可以看到前端頁面
- [ ] API 文檔可以訪問：`https://your-app.onrender.com/docs`

### 2. 測試 API
- [ ] 測試登入 API：`POST /api/auth/login`
- [ ] 測試智能搜索 API：`POST /api/smart-search`（需要 JWT token）

### 3. 檢查日誌
在 Render Dashboard > Logs 頁籤中檢查：
- [ ] 沒有 `OPENROUTER_API_KEY 未設置` 的錯誤
- [ ] 沒有 Python 導入錯誤
- [ ] 沒有前端構建錯誤
- [ ] 服務正常啟動：`Application startup complete`

### 4. 測試前端功能
- [ ] 可以正常登入
- [ ] 可以訪問智能搜索頁面
- [ ] 浮動搜索按鈕正常顯示
- [ ] AI 搜索功能正常工作

## 🐛 常見問題排查

### 問題 1：構建失敗
**症狀**：構建過程中斷，顯示錯誤

**解決方法**：
1. 檢查 `render-build.sh` 是否有執行權限
2. 檢查 `requirements.txt` 中的依賴是否正確
3. 檢查 Node.js 版本是否匹配（render.yaml 中設置為 22.13.0）

### 問題 2：前端無法訪問
**症狀**：訪問服務 URL 顯示錯誤或空白頁

**解決方法**：
1. 檢查 Logs 確認 `h5-app/dist` 目錄是否存在
2. 確認前端構建成功（查看構建日誌）
3. 檢查 `app.py` 中的靜態文件服務配置

### 問題 3：API 返回 500 錯誤
**症狀**：API 請求返回內部服務器錯誤

**解決方法**：
1. 檢查 Logs 查看具體錯誤訊息
2. 確認環境變數已正確設置
3. 確認數據庫文件權限正確

### 問題 4：智能搜索功能無法使用
**症狀**：搜索時沒有結果或報錯

**解決方法**：
1. 確認 `OPENROUTER_API_KEY` 已正確設置
2. 檢查 Logs 確認沒有 API Key 相關錯誤
3. 測試 OpenRouter API Key 是否有效
4. 確認請求包含有效的 JWT token

### 問題 5：CORS 錯誤
**症狀**：瀏覽器控制台顯示 CORS 錯誤

**解決方法**：
1. 設置 `ALLOWED_ORIGINS` 環境變數
2. 確認前端請求的域名在允許列表中
3. 檢查 `app.py` 中的 CORS 配置

## 📝 環境變數參考

### 完整環境變數列表

```env
# 必需
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# 推薦
SECRET_KEY=your-secret-key-at-least-32-chars-long
ALLOWED_ORIGINS=https://your-app.onrender.com

# 可選
PYTHON_VERSION=3.10.0
NODE_VERSION=22.13.0
```

## 🔒 安全建議

1. ✅ **永遠不要**將 API Key 寫在代碼中
2. ✅ **永遠不要**將 `.env` 文件提交到 Git
3. ✅ **使用** Render Dashboard 的環境變數功能
4. ✅ **設置**強壯的 `SECRET_KEY`（至少 32 字符）
5. ✅ **限制** CORS 來源（生產環境）
6. ✅ **定期**輪換 API Key 和密鑰

## 📞 需要幫助？

如果遇到問題：
1. 查看 Render Dashboard 的 Logs
2. 檢查本文檔的「常見問題排查」部分
3. 查看 `RENDER_SETUP.md` 獲取詳細設置指南
