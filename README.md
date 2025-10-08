# 台積電 ADR ↔ 台股換算工具

台積電 ADR 與台股價格換算計算機，包含歷史價差分析。

## 功能

- ADR 與台股價格換算
- 歷史價差趨勢圖表  
- 統計分析（平均價差、溢價/折價）
- 自動資料更新

## 換算公式

- 1 張台積電台股 = 5 股 TSM ADR
- 台股價格 = ADR價格 ÷ 5 × USD/TWD匯率

## 使用方式

自動重啟模式（推薦）：
```bash
./streamlit_monitor.sh monitor
```

手動啟動：
```bash
./streamlit_monitor.sh start
```

開啟瀏覽器前往：`http://localhost:8501`

### 本地開發（完整環境）

如需本地開發或測試：

#### 後端服務
```bash
cd backend
pip install -r requirements.txt
export ALPHA_VANTAGE_API_KEY="your_api_key"
uvicorn api_server:app --reload --port 8000
```

#### 前端應用（另一個終端）
```bash
cd frontend
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run streamlit_app.py
```

## 系統需求

- Python 3.8+
- 網路連線

## 管理命令

```bash
# 檢查狀態
./streamlit_monitor.sh status

# 重啟服務  
./streamlit_monitor.sh restart

# 停止服務
./streamlit_monitor.sh stop
```

## 免責聲明

本工具僅供參考，不構成投資建議。