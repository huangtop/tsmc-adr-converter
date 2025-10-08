# 台積電 ADR ↔ 台股換算工具

台積電 ADR 與台股價格換算計算機，支援即時價格查詢與歷史趨勢分析。

## 功能特色

- 💰 ADR 與台股價格即時換算
- 📈 歷史價差趨勢分析  
- 📊 價格統計與圖表展示
- 🔄 資料快取機制

## 換算公式

- **1 張台積電台股 = 5 股 TSM ADR**
- **台股價格 = ADR價格 ÷ 5 × USD/TWD匯率**

## 系統需求

- Python 3.8+
- Alpha Vantage API Key

## 資料來源

- ADR 價格：Alpha Vantage API
- 匯率：台灣銀行
- 台股價格：證交所

## 免責聲明

本工具僅供學習研究用途，所有資料僅供參考，不構成投資建議。

## 授權

MIT License

---

Made for Taiwan investors
