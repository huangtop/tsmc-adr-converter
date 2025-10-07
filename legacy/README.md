# 台積電 ADR ↔ 台股換算工具

一個簡單的台積電 ADR 與台股價格換算計算機，包含歷史價差圖表分析。

## 功能特色

- 💰 ADR 與台股價格即時換算
- 📈 歷史價差趨勢圖表
- 📊 統計分析（平均價差、溢價/折價）
- 🔄 自動資料更新

## 換算公式

- **1 張台積電台股 = 5 股 TSM ADR**
- **台股價格 = ADR價格 ÷ 5 × USD/TWD匯率**

## 快速開始

### 本地執行

#### 後端服務
```bash
cd backend
pip install -r requirements.txt
export ALPHA_VANTAGE_API_KEY="your_api_key"
uvicorn api_server:app --reload --port 8000
```

#### 前端應用
```bash
cd frontend
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run streamlit_app.py
```

## 系統需求

- Python 3.8+
- Alpha Vantage API Key (免費註冊)

## 技術架構

- 後端：FastAPI
- 前端：Streamlit
- 圖表：Plotly
- 資料源：Alpha Vantage、台灣銀行、證交所

## 部署

支援多種部署方式：
- 本地開發環境
- 雲端服務（Streamlit Cloud、Railway 等）
- Docker 容器

詳細部署說明請參考 [架構文件](README_ARCHITECTURE.md)。

## 免責聲明

本工具僅供學習研究用途，所有資料僅供參考，不構成投資建議。

## 授權

MIT License

---

Made with ❤️ for Taiwan investors
