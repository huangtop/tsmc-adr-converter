"""
台積電 ADR 換算 API 服務
負責處理所有核心邏輯，包括資料抓取、快取管理、計算等
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import datetime
import json
import os
from typing import Optional, Dict, Any
import pandas as pd
from contextlib import asynccontextmanager

# 環境變數設定
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YOUR_API_KEY_HERE')
CACHE_FILE = "daily_prices_cache.json"
HISTORY_CACHE_FILE = "price_history_cache.json"
API_USAGE_FILE = "api_usage_log.json"

# API 使用限制設定
MAX_API_CALLS_PER_DAY = 2
MAX_CACHE_HOURS = 24

app = FastAPI(
    title="台積電 ADR 換算 API",
    description="提供台積電 ADR 與台股換算功能的後端 API 服務",
    version="1.0.0"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 資料模型
# ===============================
class ConversionRequest(BaseModel):
    adr_price: float
    usd_twd: float

class ConversionResponse(BaseModel):
    converted_price: float
    formula_explanation: str
    compared_to_tw_price: Optional[Dict[str, Any]] = None

class PriceData(BaseModel):
    adr_price: Optional[float]
    tw_price: Optional[float]
    usd_twd: Optional[float]
    last_updated: Optional[str]
    cache_date: Optional[str]

# ===============================
# 快取管理函數
# ===============================
def load_cache():
    """讀取本地快取的每日價格資料"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(data):
    """儲存每日價格資料到本地快取"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"無法儲存快取: {e}")

def load_history_cache():
    """讀取歷史價格資料"""
    if os.path.exists(HISTORY_CACHE_FILE):
        try:
            with open(HISTORY_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history_cache(data):
    """儲存歷史價格資料"""
    try:
        with open(HISTORY_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"無法儲存歷史快取: {e}")

def is_cache_valid(cache_data):
    """檢查快取是否是今天的資料"""
    today = datetime.date.today().isoformat()
    return cache_data.get('date') == today

def load_api_usage():
    """載入 API 使用記錄"""
    if os.path.exists(API_USAGE_FILE):
        try:
            with open(API_USAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_api_usage(usage_data):
    """儲存 API 使用記錄"""
    try:
        with open(API_USAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(usage_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"無法儲存 API 使用記錄: {e}")

def check_api_limit():
    """檢查今日 API 呼叫次數是否超限"""
    today = datetime.date.today().isoformat()
    usage = load_api_usage()
    
    daily_usage = usage.get(today, {})
    calls_today = daily_usage.get('calls', 0)
    
    return calls_today < MAX_API_CALLS_PER_DAY

def record_api_call(api_name):
    """記錄 API 呼叫"""
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now().isoformat()
    usage = load_api_usage()
    
    if today not in usage:
        usage[today] = {'calls': 0, 'log': []}
    
    usage[today]['calls'] += 1
    usage[today]['log'].append({
        'api': api_name,
        'timestamp': now
    })
    
    save_api_usage(usage)
    return usage[today]['calls']

# ===============================
# 核心業務邏輯函數
# ===============================
def fetch_adr_price():
    """從 Alpha Vantage 抓取 ADR 價格（帶 API 限制檢查）"""
    # 檢查 API 限制
    if not check_api_limit():
        print(f"⚠️  API 呼叫已達每日限制 ({MAX_API_CALLS_PER_DAY} 次)")
        return None
    
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=TSM&apikey={ALPHA_VANTAGE_API_KEY}"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        # 記錄 API 呼叫
        calls_today = record_api_call('ALPHA_VANTAGE_ADR')
        print(f"📊 Alpha Vantage API 呼叫次數: {calls_today}/{MAX_API_CALLS_PER_DAY}")
        
        if "Global Quote" in data:
            return float(data["Global Quote"]["05. price"])
        else:
            return None
    except Exception as e:
        print(f"無法取得 ADR 價格: {e}")
        return None

def fetch_tw_price():
    """從台灣證交所抓取台積電股價"""
    try:
        url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_2330.tw"
        res = requests.get(url, verify=False, timeout=5)
        data = res.json()
        
        msg = data.get("msgArray", [])
        if msg:
            price = msg[0].get("z") or msg[0].get("p")
            if price and price != "-":
                return float(price)
        return None
    except Exception as e:
        print(f"無法取得台股價格: {e}")
        return None

def fetch_usd_twd():
    """從台灣銀行抓取美元匯率"""
    try:
        url = "https://rate.bot.com.tw/xrt/flcsv/0/day"
        res = requests.get(url, verify=False, timeout=10)
        usd_row = [r for r in res.text.split("\n") if "USD" in r]
        if usd_row:
            return float(usd_row[0].split(",")[12])
        return None
    except Exception as e:
        print(f"無法取得匯率: {e}")
        return None

def get_cached_prices():
    """取得快取的價格資料"""
    cache = load_cache()
    
    if is_cache_valid(cache):
        return {
            'adr_price': cache.get('adr_price'),
            'tw_price': cache.get('tw_price'),
            'usd_twd': cache.get('usd_twd'),
            'last_updated': cache.get('last_updated'),
            'cache_date': cache.get('date')
        }
    
    # 快取過期，重新抓取（受 API 限制保護）
    print(f"📅 快取過期，嘗試更新價格資料...")
    
    adr_price = fetch_adr_price()  # 受 API 限制保護
    tw_price = fetch_tw_price()    # 台股資料免費
    usd_twd = fetch_usd_twd()      # 銀行匯率免費
    
    # 只有在成功獲取 ADR 價格時才更新快取
    if adr_price is not None:
        today = datetime.date.today().isoformat()
        now = datetime.datetime.now().isoformat()
        
        cache = {
            'date': today,
            'adr_price': adr_price,
            'tw_price': tw_price,
            'usd_twd': usd_twd,
            'last_updated': now,
            'data_source': 'fresh_api_call'
        }
        save_cache(cache)
        print(f"✅ 快取已更新，所有用戶將看到相同的最新資料")
        
        return {
            'adr_price': adr_price,
            'tw_price': tw_price,
            'usd_twd': usd_twd,
            'last_updated': now,
            'cache_date': today,
            'data_source': 'fresh_api_call'
        }
    else:
        # API 限制達到，返回舊快取（如果有的話）
        print(f"⚠️  API 限制達到，返回現有快取資料")
        return {
            'adr_price': cache.get('adr_price'),
            'tw_price': tw_price,  # 台股和匯率仍可更新
            'usd_twd': usd_twd,
            'last_updated': cache.get('last_updated'),
            'cache_date': cache.get('date'),
            'data_source': 'cached_due_to_api_limit'
        }

def fetch_tw_price_by_date(date_str):
    """取得特定日期的台股歷史價格 (使用台灣證交所 API)"""
    try:
        # 台灣證交所 - 歷史資料查詢
        year, month, day = date_str.split('-')
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={year}{month}{day}&stockNo=2330"
        res = requests.get(url, verify=False, timeout=5)
        data = res.json()
        
        if "data" in data and len(data["data"]) > 0:
            # API 可能返回該月份的所有日期，需要查找對應的日期
            # 日期格式為 "114/11/26" (民國/月/日)
            target_date = f"{int(year) - 1911}/{month}/{day}"  # 轉換為民國年份
            
            for row in data["data"]:
                if row[0] == target_date:
                    # 取得收盤價 (index 6)，格式可能為 "1,510.00"，需要去掉逗號
                    price_str = str(row[6]).replace(',', '')
                    closing_price = float(price_str)
                    return closing_price
            
            # 如果沒有找到該日期，可能是休市日，返回 None
            return None
        return None
    except Exception as e:
        print(f"無法取得 {date_str} 的台股價格: {e}")
        return None

def fetch_historical_data():
    """抓取歷史資料 - 使用真實的台股和匯率數據"""
    history = load_history_cache()
    today = datetime.date.today().isoformat()
    
    # 檢查是否今天已經更新過
    if history.get('last_fetch_date') == today:
        return history
    
    try:
        # 抓取 ADR 歷史資料
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSM&apikey={ALPHA_VANTAGE_API_KEY}"
        res = requests.get(url, timeout=15)
        data = res.json()
        
        if "Time Series (Daily)" in data:
            daily_data = data["Time Series (Daily)"]
            
            # 處理過去30天的資料
            for date_str, adr_data in list(daily_data.items())[:30]:
                try:
                    adr_price = float(adr_data["4. close"])
                    
                    # 獲取真實的台股價格和匯率（使用固定匯率，因為歷史匯率 API 限制）
                    tw_price = fetch_tw_price_by_date(date_str)
                    
                    # 使用當前匯率作為近似值，或使用固定匯率
                    # 在實際應用中應該使用歷史匯率 API
                    usd_twd = 32.0  # 可改為歷史匯率 API
                    
                    if tw_price is None:
                        # 如果無法取得台股價格，跳過此日期
                        continue
                    
                    history[date_str] = {
                        'adr_price': adr_price,
                        'tw_price': tw_price,
                        'usd_twd': usd_twd,
                        'timestamp': f"{date_str}T16:00:00"
                    }
                except Exception as e:
                    print(f"處理 {date_str} 時出錯: {e}")
                    continue
            
            history['last_fetch_date'] = today
            save_history_cache(history)
            print(f"✅ 歷史資料已更新，共 {len([k for k in history if k != 'last_fetch_date'])} 筆記錄")
    
    except Exception as e:
        print(f"無法取得歷史資料: {e}")
    
    return history

# ===============================
# API 路由
# ===============================
@app.get("/")
async def root():
    return {"message": "台積電 ADR 換算 API 服務"}

@app.get("/api/prices", response_model=PriceData)
async def get_current_prices():
    """取得當前價格資料"""
    try:
        prices = get_cached_prices()
        return PriceData(**prices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert", response_model=ConversionResponse)
async def convert_adr_to_tw(request: ConversionRequest):
    """ADR 價格換算成台股價格"""
    try:
        converted_price = (request.adr_price / 5) * request.usd_twd
        formula = f"台股價格 = ADR價格 ÷ 5 × 匯率 = {request.adr_price:.2f} ÷ 5 × {request.usd_twd:.2f} = {converted_price:.2f} 元"
        
        # 取得台股參考價格進行比較
        current_prices = get_cached_prices()
        compared_data = None
        
        if current_prices['tw_price']:
            diff = converted_price - current_prices['tw_price']
            diff_percent = (diff / current_prices['tw_price']) * 100
            compared_data = {
                'tw_reference_price': current_prices['tw_price'],
                'difference': diff,
                'difference_percent': diff_percent
            }
        
        return ConversionResponse(
            converted_price=converted_price,
            formula_explanation=formula,
            compared_to_tw_price=compared_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical")
async def get_historical_data():
    """取得歷史價差資料"""
    try:
        history = fetch_historical_data()
        
        # 整理過去30天的資料
        today = datetime.date.today()
        historical_data = []
        
        for i in range(30, 0, -1):
            date = today - datetime.timedelta(days=i)
            date_str = date.isoformat()
            
            if date_str in history and isinstance(history[date_str], dict):
                record = history[date_str]
                if all(key in record for key in ['adr_price', 'tw_price', 'usd_twd']):
                    adr_in_twd = (record['adr_price'] / 5) * record['usd_twd']
                    difference = adr_in_twd - record['tw_price']
                    difference_percent = (difference / record['tw_price']) * 100
                    
                    historical_data.append({
                        'date': date_str,
                        'adr_price_usd': record['adr_price'],
                        'tw_price': record['tw_price'],
                        'usd_twd': record['usd_twd'],
                        'adr_in_twd': adr_in_twd,
                        'difference': difference,
                        'difference_percent': difference_percent
                    })
        
        return {"data": historical_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康檢查和系統狀態"""
    today = datetime.date.today().isoformat()
    usage = load_api_usage()
    daily_usage = usage.get(today, {})
    calls_today = daily_usage.get('calls', 0)
    
    cache = load_cache()
    cache_valid = is_cache_valid(cache)
    
    return {
        "status": "healthy", 
        "timestamp": datetime.datetime.now().isoformat(),
        "api_usage": {
            "calls_today": calls_today,
            "limit": MAX_API_CALLS_PER_DAY,
            "remaining": MAX_API_CALLS_PER_DAY - calls_today
        },
        "cache_status": {
            "valid": cache_valid,
            "last_updated": cache.get('last_updated'),
            "cache_date": cache.get('date')
        },
        "system_info": {
            "version": "1.0.0",
            "shared_cache": "enabled",
            "api_protection": "enabled"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
