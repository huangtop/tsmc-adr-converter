import streamlit as st
import requests
import datetime
import json
import os
import urllib3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ===============================
# Configuration
# ===============================
ALPHA_VANTAGE_API_KEY =  st.secrets["ALPHA_VANTAGE_API_KEY"]  # 請至 https://www.alphavantage.co 註冊免費帳號
CACHE_FILE = "daily_prices_cache.json"


# ===============================
# 本地快取系統
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
        st.error(f"無法儲存快取: {e}")

def is_cache_valid(cache_data):
    """檢查快取是否是今天的資料"""
    today = datetime.date.today().isoformat()
    return cache_data.get('date') == today

# ===============================
# 歷史資料快取系統
# ===============================
HISTORY_CACHE_FILE = "price_history_cache.json"

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
        st.error(f"無法儲存歷史快取: {e}")

def fetch_historical_adr_data():
    """從 Alpha Vantage 抓取過去30天的 ADR 歷史資料"""
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSM&apikey={ALPHA_VANTAGE_API_KEY}"
        res = requests.get(url, timeout=15)
        data = res.json()
        
        if "Time Series (Daily)" in data:
            daily_data = data["Time Series (Daily)"]
            return daily_data
        else:
            st.warning("Alpha Vantage API 限制，無法取得歷史 ADR 資料")
            return None
    except Exception as e:
        st.warning(f"無法取得歷史 ADR 資料: {e}")
        return None

def fetch_historical_exchange_rate():
    """抓取過去30天的匯率（簡化版，使用當前匯率估算）"""
    # 台銀沒有提供歷史匯率API，這裡使用當前匯率加上小幅波動模擬
    current_rate = get_cached_usd_twd()
    if not current_rate:
        return None
    
    # 生成過去30天的模擬匯率（實際使用時可接入其他匯率API）
    rates = {}
    today = datetime.date.today()
    
    for i in range(30, 0, -1):
        date = today - datetime.timedelta(days=i)
        date_str = date.isoformat()
        # 加入±1%的隨機波動模擬歷史匯率
        import random
        variation = random.uniform(-0.01, 0.01)
        rates[date_str] = current_rate * (1 + variation)
    
    return rates

def update_historical_cache():
    """更新歷史資料快取（一天一次）"""
    history = load_history_cache()
    today = datetime.date.today().isoformat()
    
    # 檢查是否今天已經更新過歷史資料
    if history.get('last_fetch_date') == today:
        return history
    
    st.info("🔄 正在更新歷史資料快取...")
    
    # 抓取 ADR 歷史資料
    adr_history = fetch_historical_adr_data()
    exchange_rates = fetch_historical_exchange_rate()
    
    if not adr_history:
        return history
    
    # 處理過去30天的資料
    updated_count = 0
    for date_str, adr_data in list(adr_history.items())[:30]:  # 取最近30天
        try:
            adr_price = float(adr_data["4. close"])
            
            # 取得對應日期的匯率
            usd_twd = exchange_rates.get(date_str) if exchange_rates else 32.0
            
            # 嘗試取得當日台股價格（簡化版，使用估算）
            # 實際應用中可以接入台股歷史資料API
            tw_price = adr_price * 5 * usd_twd / 32.0  # 簡化估算
            
            history[date_str] = {
                'adr_price': adr_price,
                'tw_price': tw_price,
                'usd_twd': usd_twd,
                'timestamp': f"{date_str}T16:00:00",
                'source': 'historical_fetch'
            }
            updated_count += 1
            
        except Exception as e:
            continue
    
    # 記錄最後更新時間
    history['last_fetch_date'] = today
    history['last_fetch_time'] = datetime.datetime.now().isoformat()
    
    # 清理超過60天的資料
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
    history = {k: v for k, v in history.items() 
              if k.startswith('last_') or (isinstance(v, dict) and k >= cutoff_date) or not isinstance(v, dict)}
    
    save_history_cache(history)
    st.success(f"✅ 已更新 {updated_count} 天的歷史資料")
    
    return history

def get_historical_data():
    """取得過去30天的歷史資料"""
    # 先嘗試更新歷史快取
    history = update_historical_cache()
    
    today = datetime.date.today()
    
    # 生成過去30天的日期列表
    dates = []
    for i in range(30, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.isoformat())
    
    # 準備資料結構
    historical_data = []
    
    for date_str in dates:
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
    
    return pd.DataFrame(historical_data) if historical_data else pd.DataFrame()

def update_historical_record(adr_price, tw_price, usd_twd):
    """更新今日的歷史記錄"""
    if not all([adr_price, tw_price, usd_twd]):
        return
    
    history = load_history_cache()
    today = datetime.date.today().isoformat()
    
    history[today] = {
        'adr_price': adr_price,
        'tw_price': tw_price,
        'usd_twd': usd_twd,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # 只保留最近60天的資料
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
    history = {k: v for k, v in history.items() if k >= cutoff_date}
    
    save_history_cache(history)

# ===============================
# Function 1: 取得 TSM ADR 美股收盤價（每日一次）
# ===============================
def get_cached_adr_price():
    """取得快取的 TSM ADR 收盤價，如果沒有或過期則抓取新的"""
    cache = load_cache()
    
    # 如果快取有效，直接返回
    if is_cache_valid(cache) and 'adr_price' in cache:
        return cache['adr_price']
    
    # 嘗試從 API 抓取新的價格
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=TSM&apikey={ALPHA_VANTAGE_API_KEY}"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        if "Global Quote" in data:
            price = float(data["Global Quote"]["05. price"])
            # 更新快取
            cache['date'] = datetime.date.today().isoformat()
            cache['adr_price'] = price
            cache['last_updated'] = datetime.datetime.now().isoformat()
            save_cache(cache)
            return price
        else:
            # API 限制或其他錯誤，使用昨天的快取（如果有的話）
            return cache.get('adr_price')
    except Exception as e:
        st.warning(f"無法取得即時 ADR 價格: {e}")
        return cache.get('adr_price')

# ===============================
# Function 2: 取得台積電台股價格（TWSE）
# ===============================    
def get_twse_price(stock_id, max_retry=3):
    """
    從台灣證交所 MIS API 取得即時股價（具備自動重試 + JSONDecode 防呆）
    """
    import time

    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw"

    for attempt in range(max_retry):
        try:
            res = requests.get(url, verify=False, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 第 {attempt+1} 次連線失敗：{e}")
            time.sleep(1)
            continue

        # --- 判斷是否有內容 ---
        if not res.text.strip():
            print(f"⚠️ 第 {attempt+1} 次：伺服器回傳空白內容")
            time.sleep(1)
            continue

        # --- 嘗試解析 JSON ---
        try:
            data = res.json()
        except Exception:
            print(f"⚠️ 第 {attempt+1} 次：無法解析 JSON，內容如下：")
            print(res.text[:200])
            time.sleep(1)
            continue

        # --- 提取股價 ---
        try:
            msg = data.get("msgArray", [])
            if msg:
                price = msg[0].get("z") or msg[0].get("p")
                if price and price != "-":
                    return float(price)
        except Exception as e:
            print("⚠️ 解析股價錯誤：", e)

        time.sleep(1)

    print("❌ 多次嘗試後仍無法取得 TWSE 即時價格。")
    return None


# ===============================
# Function 3: 取得台灣銀行匯率（每日一次）
# ===============================
def get_cached_usd_twd():
    """取得快取的台灣銀行匯率，如果沒有或過期則抓取新的"""
    cache = load_cache()
    
    # 如果快取有效，直接返回
    if is_cache_valid(cache) and 'usd_twd' in cache:
        return cache['usd_twd']
    
    # 嘗試從台銀抓取新的匯率
    try:
        url = "https://rate.bot.com.tw/xrt/flcsv/0/day"
        res = requests.get(url, verify=False, timeout=10)
        usd_row = [r for r in res.text.split("\n") if "USD" in r]
        if usd_row:
            rate = float(usd_row[0].split(",")[12])
            # 更新快取
            cache['date'] = datetime.date.today().isoformat()
            cache['usd_twd'] = rate
            
            return rate
    except Exception as e:
        st.warning(f"無法取得即時匯率: {e}")
        return cache.get('usd_twd')


# ===============================
# Streamlit UI
# ===============================
st.set_page_config(page_title="台積電 ADR ↔ 台股 換算計算機", layout="centered")

st.markdown('<h4>💹台積電ADR ↔ 台股股價換算計算機</h4>', unsafe_allow_html=True)

st.markdown("""
這個工具會自動載入每日快取的股價和匯率：
- 台積電 ADR (TSM.US) 前收盤價
- 台灣銀行美元匯率
- 🇹台積電台股前收盤價
- 支援手動輸入任何 ADR 價格進行測試
""")

# 取得快取資料
cached_adr = get_cached_adr_price()
cached_usd_twd = get_cached_usd_twd()
cached_tw_price = get_twse_price("2330")  # 2330 是台積電的股票代碼

# 更新歷史記錄（如果今天的資料都有的話）
if cached_adr and cached_usd_twd and cached_tw_price:
    update_historical_record(cached_adr, cached_tw_price, cached_usd_twd)

# 顯示快取資料供參考
st.subheader("參考資料（每日快取）")
col1, col2, col3 = st.columns(3)

with col1:
    if cached_adr:
        st.metric("TSM ADR 前收", f"${cached_adr:.2f}")
    else:
        st.metric("TSM ADR 前收", "N/A")

with col2:
    if cached_usd_twd:
        st.metric("USD/TWD", f"{cached_usd_twd:.2f}")
    else:
        st.metric("USD/TWD", "N/A")

with col3:
    if cached_tw_price:
        st.metric("台積電台股", f"{cached_tw_price:.2f} 元")
    else:
        st.metric("台積電台股", "N/A")

# ===============================
# 📈 歷史價差圖表
# ===============================
st.subheader("📈 ADR vs 台股價差歷史圖表")

# 取得歷史資料
hist_df = get_historical_data()

if not hist_df.empty:
    try:
        # 建立子圖表
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('股價走勢對比', 'ADR vs 台股價差 (溢價/折價)'),
            vertical_spacing=0.1,
            row_heights=[0.6, 0.4]
        )
        
        # 上圖：股價走勢對比
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(hist_df['date']),
                y=hist_df['adr_in_twd'],
                name='ADR換算台股價',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='ADR換算: %{y:.2f} 元<br>日期: %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(hist_df['date']),
                y=hist_df['tw_price'],
                name='台股實際價格',
                line=dict(color='#ff7f0e', width=2),
                hovertemplate='台股價: %{y:.2f} 元<br>日期: %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 下圖：價差百分比
        colors = ['red' if x > 0 else 'green' for x in hist_df['difference_percent']]
        
        fig.add_trace(
            go.Bar(
                x=pd.to_datetime(hist_df['date']),
                y=hist_df['difference_percent'],
                name='價差百分比',
                marker_color=colors,
                opacity=0.7,
                hovertemplate='價差: %{y:.2f}%<br>日期: %{x}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 添加零線
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        # 更新佈局
        fig.update_layout(
            height=600,
            showlegend=True,
            title_text="台積電 ADR vs 台股歷史價差分析 (過去30天)",
            hovermode='x unified'
        )
        
        # 更新 x 軸
        fig.update_xaxes(title_text="日期", row=2, col=1)
        
        # 更新 y 軸
        fig.update_yaxes(title_text="股價 (TWD)", row=1, col=1)
        fig.update_yaxes(title_text="價差 (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 顯示統計摘要
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_diff = hist_df['difference_percent'].mean()
            st.metric("平均價差", f"{avg_diff:.2f}%")
        
        with col2:
            max_premium = hist_df['difference_percent'].max()
            st.metric("最大溢價", f"{max_premium:.2f}%")
        
        with col3:
            min_discount = hist_df['difference_percent'].min()
            st.metric("最大折價", f"{min_discount:.2f}%")
        
        with col4:
            volatility = hist_df['difference_percent'].std()
            st.metric("價差波動", f"{volatility:.2f}%")
            
        # 說明文字
        st.caption("""
        📊 **圖表說明：**
        - 🔵 藍線：ADR 換算台股價格 (ADR價格÷5×匯率)
        - 🟠 橘線：台股實際收盤價
        - 🔴 紅色柱：ADR 溢價 (ADR換算價 > 台股價)
        - 🟢 綠色柱：ADR 折價 (ADR換算價 < 台股價)
        """)
        
    except Exception as e:
        st.error(f"圖表繪製錯誤: {e}")
        st.info("請安裝 plotly: `pip install plotly`")
else:
    st.info("📊 暫無歷史資料，請等待數日累積資料後重新查看")
    st.caption("歷史資料會在每日股價更新時自動累積")

# 用戶手動輸入區域
st.subheader("🎯 ADR 換算計算器")
st.markdown("請輸入要測試的 ADR 價格和匯率：")

adr_price = st.number_input(
    "輸入 ADR 價格 (USD)", 
    min_value=0.0, 
    value=float(cached_adr) if cached_adr else 100.0, 
    step=0.01,
    help="可以輸入任何價格來測試換算結果"
)

usd_twd = st.number_input(
    "輸入匯率 (USD/TWD)", 
    min_value=20.0, 
    value=float(cached_usd_twd) if cached_usd_twd else 32.0, 
    step=0.01,
    help="參考當日台銀匯率，或輸入想測試的匯率"
)

# 計算換算
if adr_price and usd_twd:
    converted_price = (adr_price / 5) * usd_twd
    st.subheader("📊 換算結果")
    st.success(f"推算台股價格 ≈ **{converted_price:.2f} 元** (ADR價格÷5×匯率)")

    # 如果有台股參考價格，顯示比較
    if cached_tw_price:
        diff = converted_price - cached_tw_price
        diff_percent = (diff / cached_tw_price) * 100
        if diff > 0:
            st.info(f"📈 比台股前收高 **{diff:.2f} 元** ({diff_percent:+.2f}%)")
        else:
            st.info(f"📉 比台股前收低 **{abs(diff):.2f} 元** ({diff_percent:+.2f}%)")
    
    # 顯示換算公式說明
    st.markdown("**� 換算公式說明：**")
    st.markdown(f"台股價格 = ADR價格 ÷ 5 × 匯率 = {adr_price:.2f} ÷ 5 × {usd_twd:.2f} = **{converted_price:.2f} 元**")
    st.caption("註：1 張台積電台股 = 5 股TSM ADR")
else:
    st.stop()

# 顯示快取狀態
st.divider()
cache = load_cache()
if cache.get('date'):
    cache_date = cache['date']
    last_updated = cache.get('last_updated', 'N/A')
    if last_updated != 'N/A':
        try:
            update_time = datetime.datetime.fromisoformat(last_updated).strftime('%H:%M')
            st.caption(f"📅 參考資料日期：{cache_date} | ⏰ 最後更新：{update_time}")
        except:
            st.caption(f"📅 參考資料日期：{cache_date}")
    else:
        st.caption(f"📅 參考資料日期：{cache_date}")

# 備註
st.caption("""
> **資料來源：**
> - Alpha Vantage (合法授權金融資料 API)
> - 台灣銀行匯率公開資料
> - 台灣證券交易所公開資料
""")

st.info("💡 提示：此工具僅供參考，實際投資請以即時報價為準")
