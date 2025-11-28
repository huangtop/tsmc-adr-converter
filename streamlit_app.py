import streamlit as st
import sys
import os

# 直接從 frontend 目錄導入應用
sys.path.insert(0, os.path.dirname(__file__))

try:
    # 嘗試從 frontend 導入（本地開發）
    from frontend.streamlit_app import *
except ImportError:
    # 如果 frontend 目錄不存在（Streamlit Cloud），從 Secrets 讀取 Base64
    import base64
    
    try:
        app_code_b64 = st.secrets.get("APP_CODE_B64")
    except:
        app_code_b64 = os.getenv("APP_CODE_B64")
    
    if app_code_b64:
        try:
            app_code = base64.b64decode(app_code_b64).decode('utf-8')
            namespace = {
                '__name__': '__main__',
                '__builtins__': __builtins__,
                'st': st,
                'sys': sys
            }
            exec(app_code, namespace)
        except Exception as e:
            st.error(f"❌ 代碼執行失敗: {e}")
            st.info(f"詳細錯誤: {type(e).__name__}")
    else:
        st.error("❌ APP_CODE_B64 未在 Secrets 中找到")
