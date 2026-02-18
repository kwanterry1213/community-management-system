#!/usr/bin/env bash
# exit on error
set -o errexit

# 安裝 Python 依賴
pip install -r requirements.txt

# 進入前端目錄並安裝依賴
cd h5-app
npm install

# 建置前端 (產出 dist 資料夾)
npm run build

# 回到根目錄
cd ..

# 確保 static 資料夾存在 (如果 app.py 需要)
# mkdir -p static
