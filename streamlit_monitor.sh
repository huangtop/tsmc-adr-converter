#!/bin/bash

# Streamlit 自動重啟監控腳本
# 解決 Streamlit 需要手動重啟的問題

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
STREAMLIT_FILE="streamlit_app.py"
PID_FILE="$SCRIPT_DIR/.streamlit_pid"
LOG_FILE="$SCRIPT_DIR/streamlit_monitor.log"

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 檢查 Streamlit 是否運行
is_streamlit_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0  # 運行中
        fi
    fi
    return 1  # 未運行
}

# 啟動 Streamlit
start_streamlit() {
    log "🚀 啟動 Streamlit 應用..."
    cd "$FRONTEND_DIR"
    
    # 設定環境變數
    export API_BASE_URL=https://tsmc-adr-converter.onrender.com
    
    # 背景執行 Streamlit
    nohup streamlit run "$STREAMLIT_FILE" --server.port 8501 --server.address 0.0.0.0 > /dev/null 2>&1 &
    
    # 儲存 PID
    echo $! > "$PID_FILE"
    log "✅ Streamlit 已啟動，PID: $!"
}

# 停止 Streamlit
stop_streamlit() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log "⏹️  停止 Streamlit，PID: $PID"
            kill $PID
        fi
        rm -f "$PID_FILE"
    fi
}

# 重啟 Streamlit
restart_streamlit() {
    log "🔄 重啟 Streamlit..."
    stop_streamlit
    sleep 2
    start_streamlit
}

# 監控循環
monitor_streamlit() {
    log "👀 開始監控 Streamlit 服務..."
    
    while true; do
        if ! is_streamlit_running; then
            log "⚠️  Streamlit 未運行，自動啟動..."
            start_streamlit
        fi
        
        # 每 30 秒檢查一次
        sleep 30
    done
}

# 主程序
case "$1" in
    start)
        if is_streamlit_running; then
            log "ℹ️  Streamlit 已在運行"
        else
            start_streamlit
        fi
        ;;
    stop)
        stop_streamlit
        ;;
    restart)
        restart_streamlit
        ;;
    status)
        if is_streamlit_running; then
            log "✅ Streamlit 正在運行"
        else
            log "❌ Streamlit 未運行"
        fi
        ;;
    monitor)
        monitor_streamlit
        ;;
    *)
        echo "使用方式: $0 {start|stop|restart|status|monitor}"
        echo ""
        echo "命令說明："
        echo "  start   - 啟動 Streamlit"
        echo "  stop    - 停止 Streamlit"
        echo "  restart - 重啟 Streamlit"
        echo "  status  - 檢查狀態"
        echo "  monitor - 開始自動監控（推薦）"
        echo ""
        echo "推薦使用："
        echo "  ./streamlit_monitor.sh monitor"
        exit 1
        ;;
esac
