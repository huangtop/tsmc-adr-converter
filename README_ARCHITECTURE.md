# 系統架構

## 專案結構

```
tsmc-adr-converter/
├── backend/                    # 後端 API 服務
│   ├── api_server.py          # FastAPI 應用
│   └── requirements.txt       # 後端依賴
├── frontend/                  # 前端應用  
│   ├── streamlit_app.py       # Streamlit 主程式
│   └── requirements.txt       # 前端依賴
├── legacy/                    # 舊版備份
├── streamlit_monitor.sh       # 自動重啟腳本
├── start_frontend.sh          # 前端啟動腳本
├── requirements.txt           # 部署依賴
└── USER_GUIDE.md             # 使用說明
```

## 系統設計

- 後端：FastAPI 服務，處理資料和快取
- 前端：Streamlit 介面，用戶互動
- 快取：共享快取系統，減少 API 呼叫
- 監控：自動重啟機制

## API 端點

- `/api/health` - 系統健康檢查
- `/api/prices` - 取得價格資料
- `/api/convert` - ADR 價格換算
- `/api/historical` - 歷史資料

## 快取機制

- 價格資料每日更新一次
- 所有用戶共享相同快取
- API 呼叫次數限制保護

## 換算公式

台股價格 = ADR價格 ÷ 5 × USD/TWD匯率

### 資料流程
1. 前端接收用戶請求
2. 呼叫後端 API 端點
3. 後端檢查快取有效性
4. 必要時從外部 API 抓取資料
5. 更新快取並回傳結果
6. 前端顯示計算結果

## 部署配置

### 本地開發
```bash
# 後端服務
cd backend
uvicorn api_server:app --reload --port 8000

# 前端應用
cd frontend  
streamlit run streamlit_app.py
```

### 雲端部署
後端已部署至 Render 免費服務，前端使用自動重啟監控腳本：

```bash
# 使用自動監控啟動
./streamlit_monitor.sh monitor

# 手動啟動
./streamlit_monitor.sh start
```

### 環境變數
```env
# 後端 (Render 環境變數)
ALPHA_VANTAGE_API_KEY=your_api_key

# 前端 (本地環境變數)  
API_BASE_URL=https://tsmc-adr-converter.onrender.com
```

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 服務狀態 |
| `/api/health` | GET | 系統健康檢查 |
| `/api/prices` | GET | 當前價格資料 |
| `/api/convert` | POST | ADR 換算計算 |
| `/api/historical` | GET | 歷史資料 |

## 開發測試

### 後端測試
```bash
cd backend
uvicorn api_server:app --reload
# API 文檔: http://localhost:8000/docs
```

### 前端測試  
```bash
cd frontend
streamlit run streamlit_app.py
# 應用介面: http://localhost:8501
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
