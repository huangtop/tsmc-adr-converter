# 台積電 ADR 換算工具 - 完整使用指南

## 🎯 完美解決方案特色

### ✅ 已解決的問題：
- **雲端作業**：後端部署在 Render 免費服務
- **共享快取**：所有用戶看到相同的每日資料，節約 API 呼叫
- **API 保護**：一天最多 2 次 Alpha Vantage API 呼叫
- **自動重啟**：Streamlit 服務自動監控和重啟
- **代碼保護**：核心邏輯安全保存，不暴露於公開 repo
- **合法合規**：使用官方 API，不進行爬蟲

## 🚀 快速開始

### 方法一：自動監控（推薦）
```bash
cd tsmc-adr-converter
./streamlit_monitor.sh monitor
```
這會啟動自動監控，Streamlit 崩潰時會自動重啟。

### 方法二：手動啟動
```bash
cd tsmc-adr-converter
./streamlit_monitor.sh start
```

## 📊 系統架構

```
用戶瀏覽器 → localhost:8501 → Render 後端 → 快取系統
     ↑              ↑              ↑         ↑
   Streamlit    自動重啟機制    API 限制保護  共享資料
```

### 🔄 資料流程：
1. **首次請求**：從 Alpha Vantage 抓取資料 → 存入雲端快取
2. **後續請求**：直接從快取讀取 → 所有用戶看到相同資料
3. **隔夜更新**：快取過期後自動更新（受 API 限制保護）

## 🛡️ 安全機制

### API 使用保護：
- ✅ 一天最多 2 次 Alpha Vantage API 呼叫
- ✅ 股價資訊一天一次更新
- ✅ 所有用戶共享同一份快取資料
- ✅ API Key 安全存放於 Render 環境變數

### 代碼保護：
- ✅ 核心邏輯保存在 `backend/` 和 `frontend/` 目錄
- ✅ GitHub 上的程式碼包含 .gitignore 保護敏感資料
- ✅ 快取文件和日誌不會被提交到版本控制

## 📱 用戶存取方式

### 本地存取：
- 開啟瀏覽器前往 `http://localhost:8501`
- 自動連接到 Render 雲端後端
- 享受穩定的雲端化服務

### 網頁分享（如需要）：
可使用 ngrok 建立公開隧道：
```bash
# 另開終端
ngrok http 8501
```
然後分享 ngrok 提供的 URL。

## 🔧 管理命令

```bash
# 檢查服務狀態
./streamlit_monitor.sh status

# 重啟服務
./streamlit_monitor.sh restart

# 停止服務
./streamlit_monitor.sh stop

# 查看日誌
tail -f streamlit_monitor.log
```

## 📈 系統監控

### 後端狀態：
- 健康檢查：`https://tsmc-adr-converter.onrender.com/api/health`
- API 文檔：`https://tsmc-adr-converter.onrender.com/docs`

### 前端狀態：
- 應用介面：`http://localhost:8501`
- 監控日誌：`streamlit_monitor.log`

## 💡 最佳實踐

1. **推薦使用監控模式**：
   ```bash
   ./streamlit_monitor.sh monitor
   ```

2. **定期檢查系統狀態**：
   ```bash
   ./streamlit_monitor.sh status
   ```

3. **查看 API 使用情況**：
   前端會顯示當日 API 使用次數和快取狀態

4. **遇到問題時重啟**：
   ```bash
   ./streamlit_monitor.sh restart
   ```

## 🎊 完成！

現在你擁有一個：
- 🌐 **完全雲端化**的台積電 ADR 換算工具
- 🔒 **代碼安全保護**，不會暴露核心邏輯
- 💰 **免費運行**，使用 Render 免費服務
- 🛡️ **API 保護**，遵守使用限制
- 🔄 **自動重啟**，解決 Streamlit 穩定性問題
- 📊 **共享快取**，所有用戶看到一致資料

享受你的專業級台積電 ADR 換算工具！ 🚀
