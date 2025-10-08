#!/bin/bash

# 台積電 ADR 換算工具 - 前端啟動腳本

echo "🚀 啟動台積電 ADR 換算工具"
echo ""

# 檢查是否在正確的目錄
if [ ! -f "frontend/streamlit_app.py" ]; then
    echo "❌ 錯誤：請在 tsmc-adr-converter 根目錄中執行此腳本"
    exit 1
fi

# 檢查環境變數
if [ -z "$API_BASE_URL" ]; then
    echo "⚠️  注意：未設定 API_BASE_URL 環境變數"
    echo "   將使用預設的雲端服務端點"
    echo "   如需使用本地後端，請設定："
    echo "   export API_BASE_URL=http://localhost:8000"
    echo ""
fi

# 安裝前端依賴
echo "📦 檢查前端依賴套件..."
cd frontend

if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "   正在安裝 Streamlit 相關套件..."
    pip3 install -r requirements.txt
fi

# 啟動前端
echo "🌐 啟動 Streamlit 前端..."
echo "   瀏覽器將自動開啟 http://localhost:8501"
echo "   按 Ctrl+C 停止服務"
echo ""

streamlit run streamlit_app.py
