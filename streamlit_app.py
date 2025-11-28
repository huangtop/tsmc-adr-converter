import streamlit as st
import base64
import sys

# 從 Secrets 或環境變數讀取 Base64 編碼的代碼
try:
    app_code_b64 = st.secrets.get("APP_CODE_B64")
except:
    import os
    app_code_b64 = os.getenv("APP_CODE_B64")

if app_code_b64:
    try:
        # 解碼 Base64 代碼
        app_code = base64.b64decode(app_code_b64).decode('utf-8')
        
        # 使用正確的命名空間執行代碼
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
