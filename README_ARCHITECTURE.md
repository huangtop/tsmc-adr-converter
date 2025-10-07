# 台積電 ADR 換算計算機 - 前後端分離架構

## 🏗️ 架構概覽

```
tsmc-adr-converter/
├── backend/                 # 後端 API 服務
│   ├── api_server.py       # FastAPI 應用
│   └── requirements.txt    # 後端依賴
├── frontend/               # 前端 Streamlit 應用
│   ├── streamlit_app.py    # Streamlit 應用
│   └── requirements.txt    # 前端依賴
├── tsmc_adr_converter.py   # 原始整合版本
├── requirements.txt        # 原始依賴檔案
└── README.md              # 專案說明
```

## 🔒 安全架構優勢

### 1. **邏輯與展示分離**
- **後端**：處理所有核心業務邏輯、API Key、資料抓取
- **前端**：純展示層，只負責用戶介面和 API 呼叫

### 2. **API Key 保護**
- API Key 只存在後端服務中
- 前端完全不接觸敏感資料
- 可透過環境變數或雲端密鑰管理

### 3. **可擴展性**
- 後端 API 可服務多個前端應用
- 容易增加新功能和 API 端點
- 支援負載平衡和水平擴展

## 🚀 部署方案

### 方案 A：本地開發環境

#### 1. 啟動後端服務
```bash
cd backend
pip install -r requirements.txt
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 啟動前端應用
```bash
cd frontend
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run streamlit_app.py
```

### 方案 B：雲端部署

#### 後端部署 (推薦 Railway/Render/AWS Lambda)

**Railway 部署：**
```bash
# 1. 安裝 Railway CLI
npm install -g @railway/cli

# 2. 登入並部署
cd backend
railway login
railway init
railway add
railway deploy
```

**環境變數設定：**
```env
ALPHA_VANTAGE_API_KEY=your_actual_api_key
PORT=8000
```

#### 前端部署 (Streamlit Cloud)

**streamlit_app.py 設定：**
```python
# 改為你的後端 API URL
API_BASE_URL = os.getenv('API_BASE_URL', 'https://your-backend-domain.railway.app')
```

### 方案 C：容器化部署

#### Docker Compose 設定
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
    
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
```

## 📊 API 端點說明

### 後端 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | API 服務資訊 |
| `/api/health` | GET | 健康檢查 |
| `/api/prices` | GET | 取得當前價格資料 |
| `/api/convert` | POST | ADR 換算計算 |
| `/api/historical` | GET | 歷史價差資料 |

### API 使用範例

**取得當前價格：**
```bash
curl http://localhost:8000/api/prices
```

**進行換算計算：**
```bash
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"adr_price": 150.0, "usd_twd": 32.0}'
```

## 🔧 開發與測試

### 後端 API 測試
```bash
cd backend
uvicorn api_server:app --reload

# 訪問 API 文檔
open http://localhost:8000/docs
```

### 前端測試
```bash
cd frontend
export API_BASE_URL=http://localhost:8000
streamlit run streamlit_app.py

# 訪問前端應用
open http://localhost:8501
```

## 🛡️ 安全考量

### 1. **環境變數管理**
```bash
# .env 檔案 (不要提交到 Git)
ALPHA_VANTAGE_API_KEY=your_secret_key
API_BASE_URL=https://your-backend-domain.com
```

### 2. **CORS 設定**
後端已設定 CORS 允許前端跨域請求：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. **API Rate Limiting** (建議)
```python
# 可加入 slowapi 進行速率限制
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/prices")
@limiter.limit("10/minute")  # 每分鐘最多 10 次請求
async def get_current_prices(request: Request):
    # ... 實作
```

## 📈 監控與日誌

### 後端監控
```python
import logging
logging.basicConfig(level=logging.INFO)

# 在 API 端點中加入日誌
@app.get("/api/prices")
async def get_current_prices():
    logging.info("Price data requested")
    # ... 實作
```

### 前端用戶分析
```python
# 在 Streamlit 中加入用戶追蹤
if st.button("計算換算"):
    # Google Analytics 或其他追蹤碼
    st.write("<!-- 追蹤碼 -->", unsafe_allow_html=True)
```

這個架構完全符合你的需求：核心邏輯在後端保護，前端只負責展示，安全且可擴展！
