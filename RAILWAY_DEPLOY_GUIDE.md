# Railway 部署詳細步驟指南

## 🚀 Railway 部署完整流程

### 步驟 1：準備 GitHub Repository

1. **確認檔案安全**：
   ```bash
   # 檢查是否有敏感資訊
   grep -r "your_actual_api" .
   grep -r "ALPHA.*=" . | grep -v "YOUR_API_KEY_HERE"
   ```
   
2. **提交到 GitHub**：
   ```bash
   git add .
   git commit -m "準備 Railway 部署：後端雲端化配置"
   git push origin main
   ```

### 步驟 2：Railway 部署

1. **登入 Railway**：
   - 前往 [railway.app](https://railway.app)
   - 使用 GitHub 帳號登入

2. **建立新專案**：
   - 點擊 "New Project"
   - 選擇 "Deploy from GitHub repo"
   - 選擇你的 `tsmc-adr-converter` repository

3. **Railway 自動部署**：
   - Railway 會自動檢測到 `railway.json` 配置檔
   - 開始自動建置和部署過程
   - 等待部署完成（通常 2-3 分鐘）

### 步驟 3：設定環境變數 🔒

1. **進入專案設定**：
   - 在 Railway 控制台，點擊你的專案
   - 點擊 "Variables" 標籤

2. **新增環境變數**：
   ```
   變數名稱: ALPHA_VANTAGE_API_KEY
   變數值: [你的實際 API Key]
   ```
   
   ⚠️ **重要**：確保 API Key 只在 Railway 設定，絕不 commit 到 GitHub

3. **儲存設定**：
   - 點擊 "Add" 新增變數
   - Railway 會自動重新部署以套用新的環境變數

### 步驟 4：取得部署 URL

1. **找到服務 URL**：
   - 在 Railway 專案頁面，點擊 "Deployments"
   - 複製提供的 URL，格式類似：
   ```
   https://tsmc-adr-converter-production-xxxx.up.railway.app
   ```

2. **測試後端 API**：
   - 開啟瀏覽器，前往：`{你的URL}/docs`
   - 應該會看到 FastAPI 自動產生的 API 文檔
   - 測試 `/api/health` 端點確認服務正常

### 步驟 5：配置前端連線

有兩種方式配置前端：

#### 方式 A：環境變數（推薦）
```bash
export API_BASE_URL=https://your-actual-railway-url.up.railway.app
./start_frontend.sh
```

#### 方式 B：直接修改程式碼（臨時使用）
編輯 `frontend/streamlit_app.py`：
```python
API_BASE_URL = os.getenv('API_BASE_URL', 'https://your-actual-railway-url.up.railway.app')
```

### 步驟 6：測試完整功能

1. **啟動前端**：
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```

2. **驗證功能**：
   - ✅ 檢查後端服務連線狀態
   - ✅ 測試價格資料載入
   - ✅ 測試 ADR 換算功能
   - ✅ 確認快取機制運作

## 🔧 常見問題排除

### 問題 1：部署失敗
**解決方案**：
- 檢查 `requirements.txt` 是否正確
- 確認 `railway.json` 格式無誤
- 查看 Railway 部署日誌

### 問題 2：API Key 錯誤
**解決方案**：
- 確認在 Railway Variables 中正確設定 `ALPHA_VANTAGE_API_KEY`
- 重新部署以套用變數變更

### 問題 3：前端無法連線
**解決方案**：
- 確認 Railway URL 正確
- 檢查 CORS 設定
- 測試後端 `/api/health` 端點

### 問題 4：API 呼叫超限
**解決方案**：
- 確認每日只呼叫 2 次 Alpha Vantage API
- 檢查快取檔案是否正常運作
- 重置快取：刪除 Railway 專案中的 cache 檔案

## 📊 部署後的檔案結構

```
tsmc-adr-converter/
├── backend/              # 部署到 Railway
├── frontend/             # 本地執行，連接 Railway 後端
├── railway.json          # Railway 部署配置
├── requirements.txt      # Railway 依賴清單
└── DEPLOY.md            # 本指南
```

## 🎯 最佳實踐

1. **安全第一**：API Key 只存在於 Railway 環境變數
2. **版本控制**：定期 commit 程式碼變更到 GitHub
3. **監控使用**：留意 Alpha Vantage API 使用量
4. **備份策略**：保留本地開發環境作為備援

完成這些步驟後，你就擁有一個完全雲端化的 tsmc-adr-converter 應用，無需本地執行後端服務！
