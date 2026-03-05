#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔨 開始構建 Community Management System..."

# 安裝 Python 依賴
echo "📦 安裝 Python 依賴..."
pip install -r requirements.txt

# 進入前端目錄並安裝依賴
echo "📦 安裝前端依賴..."
cd h5-app
npm install

# 建置前端 (產出 dist 資料夾)
echo "🏗️  構建前端應用..."
npm run build

# 回到根目錄
cd ..

# 確保必要的目錄存在
echo "📁 創建必要的目錄..."
mkdir -p uploads
mkdir -p backups

echo "✅ 構建完成！"
