#!/bin/bash

# Render 啟動腳本
# 確保使用正確的格式啟動 uvicorn

echo "🚀 Starting TSMC ADR Converter API on Render..."
echo "Port: $PORT"
echo "Host: 0.0.0.0"

# 使用絕對路徑和正確的參數格式
exec uvicorn backend.api_server:app \
    --host=0.0.0.0 \
    --port=$PORT \
    --workers=1 \
    --timeout-keep-alive=30
