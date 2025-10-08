# 雲端部署指南

這個文檔說明如何將後端部署到免費的雲端服務，解決本地必須運行服務的問題。

## 方案一：Railway 部署（推薦）

### 1. 準備工作
1. 註冊 [Railway](https://railway.app) 帳號
2. 取得 [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key)

### 2. 部署步驟
1. 登入 Railway 控制台
2. 點擊 "New Project" → "Deploy from GitHub repo"
3. 選擇你的 tsmc-adr-converter 專案
4. Railway 會自動檢測並部署

### 3. 環境變數設定
在 Railway 專案設定中添加：
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 4. 取得部署 URL
部署完成後，Railway 會提供一個 URL，例如：
```
https://your-app-name.railway.app
```

### 5. 更新前端設定
將前端的 `API_BASE_URL` 環境變數設為 Railway URL：
```bash
export API_BASE_URL=https://your-app-name.railway.app
```

## 方案二：Render 部署

### 1. 準備工作
1. 註冊 [Render](https://render.com) 帳號
2. 連接你的 GitHub 帳號

### 2. 部署步驟
1. 在 Render 控制台點擊 "New" → "Web Service"
2. 選擇你的 GitHub 專案
3. 設定：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.api_server:app --host 0.0.0.0 --port $PORT`

### 3. 環境變數設定
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## 方案三：Streamlit Community Cloud（僅前端）

如果你只想部署前端，可以使用 Streamlit Community Cloud：

1. 註冊 [Streamlit Community Cloud](https://streamlit.io/cloud)
2. 連接 GitHub 專案
3. 選擇 `frontend/streamlit_app.py` 作為主文件
4. 設定環境變數指向已部署的後端

## 本地開發

本地開發時仍可使用原來的方式：

```bash
# 後端
cd backend
uvicorn api_server:app --reload --port 8000

# 前端（另一個終端）
cd frontend
export API_BASE_URL=http://localhost:8000
streamlit run streamlit_app.py
```

## 快取策略

- 雲端部署的服務會自動實施一天最多2次 API 呼叫限制
- 使用本地快取避免重複呼叫
- 快取檔案會在雲端服務的暫存儲存中

## 安全考量

- API Key 透過環境變數安全傳遞
- 不會在程式碼中暴露敏感資訊
- CORS 設定允許跨域存取

## 常見問題

### Q: 為什麼選擇前後端分離？
A: 保持程式架構的靈活性，方便後續擴展功能，並且可以獨立部署和擴展。

### Q: 免費服務的限制？
A: Railway 和 Render 免費方案有一定的使用限制，但對於這個應用足夠使用。

### Q: 如何確保服務穩定？
A: 前端設計了多個備用端點，如果主要服務不可用會自動切換到備用服務。
