# Streamlit Community Cloud 部署指南

## 🌐 將前端部署到 Streamlit Cloud

### 為什麼需要這樣做？
- 目前前端在本地 (`localhost:8501`)，用戶無法存取
- Streamlit Community Cloud 提供免費的前端託管
- 完全雲端化：前端 + 後端都在雲端

### 步驟 1: 準備 Streamlit Cloud 部署

1. **前往 Streamlit Community Cloud**:
   - 開啟 [share.streamlit.io](https://share.streamlit.io)
   - 使用 GitHub 帳號登入

2. **部署新應用**:
   - 點擊 "New app"
   - Repository: `huangtop/tsmc-adr-converter`
   - Branch: `main`
   - Main file path: `frontend/streamlit_app.py`
   - App URL: `tsmc-adr-converter` (或你喜歡的名稱)

3. **設定 Secrets**:
   ```toml
   # 在 Streamlit Cloud 的 Secrets 管理中添加
   API_BASE_URL = "https://tsmc-adr-converter.onrender.com"
   ```

### 步驟 2: 修改前端以支援 Streamlit Secrets

我們需要修改前端代碼以支援 Streamlit Cloud 的 secrets 管理。

### 步驟 3: 部署結果

完成後你會得到：
- **前端 URL**: `https://tsmc-adr-converter.streamlit.app`
- **後端 URL**: `https://tsmc-adr-converter.onrender.com`

### 用戶使用方式

用戶直接訪問: `https://tsmc-adr-converter.streamlit.app`
- 無需本地安裝
- 無需重啟服務
- 24/7 可用

## 🔄 自動重啟機制

Streamlit Community Cloud 有自動重啟機制：
- 應用閒置後會休眠
- 有用戶訪問時自動喚醒
- 無需手動重啟

## 📊 部署架構比較

| 架構 | 前端 | 後端 | 用戶體驗 |
|------|------|------|----------|
| **目前** | 本地 localhost | Render 雲端 | ❌ 用戶無法存取 |
| **升級後** | Streamlit Cloud | Render 雲端 | ✅ 完全雲端化 |
