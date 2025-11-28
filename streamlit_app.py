import streamlit as st
import base64

app_code_b64 = st.secrets.get("APP_CODE_B64")
if app_code_b64:
    try:
        app_code = base64.b64decode(app_code_b64).decode('utf-8')
        exec(app_code)
    except Exception as e:
        st.error(f"Failed to decode APP_CODE: {e}")
else:
    st.error("APP_CODE_B64 not found in secrets. Please check .streamlit/secrets.toml")
