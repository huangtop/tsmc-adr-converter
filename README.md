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

### 推薦方式：使用雲端後端 ⭐

只需啟動前端，後端已部署至雲端：

```bash
./start_frontend.sh
```

或手動執行：
```bash
cd frontend
streamlit run streamlit_app.py
```

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
- Alpha Vantage API Key (免費註冊)

## 技術架構

- 後端：FastAPI
- 前端：Streamlit
- 圖表：Plotly
- 資料源：Alpha Vantage、台灣銀行、證交所

## 雲端部署

後端可部署至免費雲端服務，解決本地必須執行服務的問題：

- ✅ **Railway**（推薦）：自動檢測，簡單部署
- ✅ **Render**：穩定可靠，免費方案充足  
- ✅ **Streamlit Cloud**：專為 Streamlit 優化

詳細部署說明請參考 [部署指南](DEPLOY.md)。

## 架構特色

- 🔄 **前後端分離**：靈活部署，便於擴展
- 🌐 **雲端優先**：無需本地服務，隨處可用
- 🛡️ **容錯設計**：多端點備援，提高可用性
- 💾 **智慧快取**：一日限制2次API，高效節約
- 🔒 **安全防護**：環境變數管理，程式碼不含敏感資訊

## 免責聲明

本工具僅供學習研究用途，所有資料僅供參考，不構成投資建議。

## 授權

MIT License

---

Made with ❤️ for Taiwan investors
