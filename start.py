#!/usr/bin/env python3
"""
Render 啟動腳本：解碼 Base64 編碼的 API 代碼並運行
"""
import base64
import os
import sys
import subprocess

def main():
    # 從環境變數讀取 Base64 編碼的代碼
    api_code_b64 = os.getenv('API_CODE_B64')
    
    if not api_code_b64:
        print("❌ 錯誤：未找到 API_CODE_B64 環境變數")
        sys.exit(1)
    
    try:
        # 解碼代碼
        api_code = base64.b64decode(api_code_b64).decode('utf-8')
        print("✅ API 代碼解碼成功")
        
        # 創建 backend 目錄（如果不存在）
        os.makedirs('backend', exist_ok=True)
        
        # 寫入 api_server.py
        with open('backend/api_server.py', 'w', encoding='utf-8') as f:
            f.write(api_code)
        print("✅ api_server.py 已創建")
        
        # 執行 API 代碼（用 subprocess 來避免上下文問題）
        print("🚀 啟動 API 服務器...")
        os.chdir('backend')
        result = subprocess.run([sys.executable, 'api_server.py'], check=True)
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
