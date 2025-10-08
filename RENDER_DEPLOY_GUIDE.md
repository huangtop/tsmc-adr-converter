# Render 免費部署指南

## 🆓 使用 Render 免費部署後端

Render 提供真正的免費方案，非常適合我們的需求！

### 步驟 1：註冊 Render

1. **前往 Render**：
   - 開啟 [render.com](https://render.com)
   - 使用 GitHub 帳號註冊/登入

### 步驟 2：建立 Web Service

1. **建立新服務**：
   - 點擊控制台右上角 "New +"
   - 選擇 "Web Service"

2. **連接 GitHub**：
   - 選擇 "Build and deploy from a Git repository"
   - 點擊 "Connect" 連接你的 GitHub
   - 選擇 `tsmc-adr-converter` repository

3. **配置服務設定**：
   ```
   Name: tsmc-adr-converter
   Region: Oregon (US West) - 最接近亞洲
   Branch: main
   Root Directory: (留空)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: ./start_render.sh
   ```
   
   **或者使用直接命令**：
   ```
   Start Command: uvicorn backend.api_server:app --host=0.0.0.0 --port=$PORT
   ```

4. **選擇免費方案**：
   - Plan Type: 選擇 "Free" (每月 750 小時)

### 步驟 3：設定環境變數

在 "Environment" 區域新增：
```
ALPHA_VANTAGE_API_KEY = [你的實際 API Key]
```

### 步驟 4：部署

1. 點擊 "Create Web Service" 開始部署
2. 等待 3-5 分鐘部署完成
3. 取得你的服務 URL，格式：
   ```
   https://tsmc-adr-converter.onrender.com
   ```

### 步驟 5：配置前端

更新前端設定來使用 Render URL：

```bash
export API_BASE_URL=https://your-app-name.onrender.com
./start_frontend.sh
```

## ⚡ Render 免費方案特色

- ✅ **真正免費**：每月 750 小時（足夠個人使用）
- ✅ **自動 SSL**：免費 HTTPS 憑證
- ✅ **GitHub 整合**：自動部署推送的變更
- ✅ **全球 CDN**：快速載入
- ⚠️ **限制**：閒置 15 分鐘後會休眠，首次喚醒需 30 秒

## 🔄 休眠機制說明

Render 免費方案會在閒置 15 分鐘後讓服務休眠：
- 第一次訪問可能需要等待 30 秒喚醒
- 我們的快取機制可以減少 API 呼叫頻率
- 對於個人使用完全足夠

## 🚀 快速開始

1. 將專案推送到 GitHub ✅（已完成）
2. 在 Render 建立 Web Service
3. 設定環境變數（API Key）
4. 取得 Render URL 並配置前端
5. 享受免費的雲端服務！

## 💡 成本比較

| 服務 | 免費方案 | 限制 |
|------|----------|------|
| **Render** | 750小時/月 | 閒置休眠 |
| Railway | ❌ 付費 | $5/月起 |
| Heroku | ❌ 付費 | $7/月起 |
| Vercel | 函數限制 | 不適合我們的需求 |

**結論**：Render 是目前最佳的免費選擇！
