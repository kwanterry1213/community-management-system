# 未來街坊圈 - 商務社團管理系統

一個功能完整的 H5 商務社團管理系統，支援會員管理、活動發布、相冊分享等功能。

## ✨ 主要功能

### 會員功能
- 👤 用戶註冊/登入
- 🔐 密碼加密存儲
- 📱 微信 SSO 登入（模擬/正式）
- 👥 會員資料管理
- 🎭 角色權限系統（遊客/會員/工作人員）

### 社團功能
- 📢 活動公告（支援置頂）
- 🎉 活動管理與報名
- 📸 活動相冊與照片管理
- 🏢 固定社團模式（未來街坊圈）

### 後台管理
- 👨‍💼 會員管理
- 📝 公告管理
- 📅 活動管理
- 🖼️ 相冊管理

## 🛠️ 技術架構

### 後端
- **框架**: FastAPI
- **數據庫**: SQLite
- **認證**: OAuth2 + JWT (模擬)
- **密碼加密**: Passlib (pbkdf2_sha256)

### 前端
- **框架**: Streamlit
- **UI 設計**: 精美的卡片式設計，漸變色主題
- **響應式**: 支援多種設備尺寸

## 📦 安裝與運行

### 1. 安裝依賴

```bash
# 創建虛擬環境（推薦 Python 3.11）
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安裝依賴
pip install fastapi uvicorn streamlit passlib pydantic requests
```

### 2. 啟動後端 API

```bash
cd /path/to/H5會員系統
uvicorn app:app --reload --port 8000
```

後端 API 將運行在 `http://localhost:8000`

### 3. 啟動前端 UI

在另一個終端：

```bash
cd /path/to/H5會員系統
streamlit run ui.py
```

前端將運行在 `http://localhost:8501`

## 📚 API 文檔

啟動後端後，訪問 `http://localhost:8000/docs` 查看自動生成的 API 文檔。

### 主要 API 端點

#### 認證
- `POST /api/auth/register` - 用戶註冊
- `POST /api/auth/login` - 用戶登入
- `POST /api/auth/wechat_sso` - 微信 SSO 登入
- `POST /api/wechat/mock_exchange` - 模擬微信 OAuth

#### 社團
- `GET /api/communities` - 獲取社團列表
- `GET /api/communities/by-name` - 按名稱獲取社團
- `POST /api/communities` - 創建社團

#### 會員
- `GET /api/memberships` - 獲取會員列表
- `POST /api/memberships` - 創建會員關係

#### 公告
- `GET /api/announcements` - 獲取公告列表
- `POST /api/announcements` - 發布公告
- `PUT /api/announcements/{id}` - 更新公告
- `DELETE /api/announcements/{id}` - 刪除公告

#### 活動
- `GET /api/events` - 獲取活動列表
- `POST /api/events` - 創建活動
- `POST /api/events/{id}/register` - 報名活動

#### 相冊
- `GET /api/albums` - 獲取相冊列表
- `POST /api/albums` - 創建相冊
- `GET /api/albums/{id}/photos` - 獲取相冊照片
- `POST /api/photos` - 上傳照片

## 🎨 界面特色

- 🏷️ 商標位置預留（可自定義）
- 🎯 首頁展示最新活動與活動花絮
- 💎 精美的漸變色卡片設計
- 🎨 統一的藍色主題風格
- 📱 響應式布局
- 🔒 角色權限控制

## 🗄️ 數據庫結構

系統使用 SQLite 數據庫，包含以下表：

- `users` - 用戶表
- `communities` - 社團表
- `memberships` - 會員關係表
- `announcements` - 公告表
- `events` - 活動表
- `event_registrations` - 活動報名表
- `albums` - 相冊表
- `photos` - 照片表

## 🔐 安全性

- 密碼使用 pbkdf2_sha256 加密
- 支援微信 SSO 集成
- 基於角色的權限控制
- API 端點保護

## 📝 預設數據

系統初始化時會自動創建：
- 管理員帳戶：`admin@test.com` / `admin123`
- 固定社團：未來街坊圈
- 示例公告、活動和相冊

## 🚀 未來規劃

- [ ] 正式微信 OAuth 集成
- [ ] 圖片上傳至雲端儲存
- [ ] 更細緻的權限控制
- [ ] 分享功能
- [ ] 通知系統
- [ ] 數據統計與報表
- [ ] 會員積分系統

## 📄 授權

此項目為私人專案。

## 👨‍💻 開發者

Himac AI Studio

---

© 2026 未來街坊圈 | 商務社團管理系統
