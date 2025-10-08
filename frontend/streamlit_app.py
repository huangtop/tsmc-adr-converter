"""
台積電 ADR 換算前端應用
純展示層，所有邏輯都透過 API 呼叫後端服務
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# 後端 API 設定 - 優先使用雲端部署版本
API_BASE_URL = os.getenv('API_BASE_URL', 'https://your-app-name.railway.app')

# 備用 API 端點（如果你有多個部署）
FALLBACK_URLS = [
    'https://your-app-name.railway.app',
    'https://your-app-name.onrender.com',
    'http://localhost:8000'  # 本地開發時的備用
]

# ===============================
# API 呼叫函數
# ===============================
def call_api(endpoint, method='GET', data=None):
    """統一的 API 呼叫函數，支援多個端點容錯"""
    urls_to_try = [API_BASE_URL] + [url for url in FALLBACK_URLS if url != API_BASE_URL]
    
    for i, base_url in enumerate(urls_to_try):
        try:
            url = f"{base_url}{endpoint}"
            if method == 'GET':
                response = requests.get(url, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=15)
            
            if response.status_code == 200:
                if i > 0:  # 如果不是第一個 URL 成功，顯示訊息
                    st.info(f"✅ 連接到備用服務: {base_url}")
                return response.json()
            else:
                if i < len(urls_to_try) - 1:  # 不是最後一個，繼續嘗試
                    continue
                st.error(f"API 錯誤: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            if i < len(urls_to_try) - 1:  # 不是最後一個，繼續嘗試下一個
                continue
            st.error(f"連線錯誤: 所有服務都無法連接")
            return None

def get_current_prices():
    """取得當前價格資料"""
    return call_api('/api/prices')

def convert_price(adr_price, usd_twd):
    """呼叫換算 API"""
    data = {
        'adr_price': adr_price,
        'usd_twd': usd_twd
    }
    return call_api('/api/convert', 'POST', data)

def get_historical_data():
    """取得歷史資料"""
    return call_api('/api/historical')

def check_api_health():
    """檢查後端 API 狀態"""
    return call_api('/api/health')

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(
    page_title="台積電 ADR ↔ 台股換算計算機", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown('<h4>💹台積電ADR ↔ 台股股價換算計算機</h4>', unsafe_allow_html=True)

# 檢查後端 API 連線狀態
with st.spinner('檢查後端服務連線...'):
    api_health = check_api_health()
    
if not api_health:
    st.error("""
    🚨 **無法連線到後端 API 服務**
    
    請確認：
    1. 後端服務是否已啟動 (`uvicorn api_server:app --reload`)
    2. API_BASE_URL 設定是否正確
    3. 網路連線是否正常
    """)
    st.stop()

st.success(f"✅ 後端服務連線正常 (更新時間: {api_health.get('timestamp', 'N/A')})")

st.markdown("""
這個工具會自動載入每日快取的股價和匯率：
- 🇺🇸 台積電 ADR (TSM.US) 前收盤價
- �� 台灣銀行美元匯率
- 🇹🇼 台積電台股前收盤價
- 💡 支援手動輸入任何 ADR 價格進行測試
""")

# 取得當前價格資料
with st.spinner('載入價格資料...'):
    current_prices = get_current_prices()

if not current_prices:
    st.error("無法取得價格資料")
    st.stop()

# 顯示參考資料
st.subheader("📊 參考資料（每日快取）")
col1, col2, col3 = st.columns(3)

with col1:
    if current_prices.get('adr_price'):
        st.metric("TSM ADR 前收", f"${current_prices['adr_price']:.2f}")
    else:
        st.metric("TSM ADR 前收", "N/A")

with col2:
    if current_prices.get('usd_twd'):
        st.metric("USD/TWD", f"{current_prices['usd_twd']:.2f}")
    else:
        st.metric("USD/TWD", "N/A")

with col3:
    if current_prices.get('tw_price'):
        st.metric("台積電台股", f"{current_prices['tw_price']:.2f} 元")
    else:
        st.metric("台積電台股", "N/A")

# ===============================
# 📈 歷史價差圖表
# ===============================
st.subheader("📈 ADR vs 台股價差歷史圖表")

with st.spinner('載入歷史資料...'):
    historical_data = get_historical_data()

if historical_data and historical_data.get('data'):
    try:
        hist_df = pd.DataFrame(historical_data['data'])
        
        if not hist_df.empty:
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
            
            # 更新軸標籤
            fig.update_xaxes(title_text="日期", row=2, col=1)
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
        else:
            st.info("📊 暫無歷史資料")
    
    except Exception as e:
        st.error(f"圖表繪製錯誤: {e}")
else:
    st.info("📊 載入歷史資料中，請稍候...")

# ===============================
# 🎯 ADR 換算計算器
# ===============================
st.subheader("🎯 ADR 換算計算器")
st.markdown("請輸入要測試的 ADR 價格和匯率：")

# 使用從後端取得的預設值
default_adr = current_prices.get('adr_price', 100.0)
default_usd = current_prices.get('usd_twd', 32.0)

adr_price = st.number_input(
    "輸入 ADR 價格 (USD)", 
    min_value=0.0, 
    value=float(default_adr) if default_adr else 100.0, 
    step=0.01,
    help="可以輸入任何價格來測試換算結果"
)

usd_twd = st.number_input(
    "輸入匯率 (USD/TWD)", 
    min_value=20.0, 
    value=float(default_usd) if default_usd else 32.0, 
    step=0.01,
    help="參考當日台銀匯率，或輸入想測試的匯率"
)

# 呼叫後端 API 進行換算
if adr_price and usd_twd:
    with st.spinner('計算中...'):
        conversion_result = convert_price(adr_price, usd_twd)
    
    if conversion_result:
        st.subheader("📊 換算結果")
        st.success(f"推算台股價格 ≈ **{conversion_result['converted_price']:.2f} 元** (ADR價格÷5×匯率)")

        # 如果有台股參考價格，顯示比較
        if conversion_result.get('compared_to_tw_price'):
            compared = conversion_result['compared_to_tw_price']
            diff = compared['difference']
            diff_percent = compared['difference_percent']
            
            if diff > 0:
                st.info(f"📈 比台股前收高 **{diff:.2f} 元** ({diff_percent:+.2f}%)")
            else:
                st.info(f"📉 比台股前收低 **{abs(diff):.2f} 元** ({diff_percent:+.2f}%)")
        
        # 顯示換算公式說明
        st.markdown("**💡 換算公式說明：**")
        st.markdown(conversion_result['formula_explanation'])
        st.caption("註：1 張台積電台股 = 5 股TSM ADR")
    else:
        st.error("換算失敗，請稍後再試")

# 顯示快取狀態
st.divider()
if current_prices.get('cache_date') and current_prices.get('last_updated'):
    cache_date = current_prices['cache_date']
    try:
        update_time = datetime.fromisoformat(current_prices['last_updated'].replace('Z', '+00:00')).strftime('%H:%M')
        st.caption(f"📅 參考資料日期：{cache_date} | ⏰ 最後更新：{update_time}")
    except:
        st.caption(f"📅 參考資料日期：{cache_date}")

# 備註
st.caption("""
> **系統架構：**
> - 🏗️ 前後端分離架構，安全且可擴展
> - 🔒 核心邏輯在後端 API 服務中保護
> - 📊 前端專注於資料展示和用戶體驗
> 
> **資料來源：**
> - Alpha Vantage (合法授權金融資料 API)
> - 台灣銀行匯率公開資料
> - 台灣證券交易所公開資料
""")

st.info("💡 提示：此工具僅供參考，實際投資請以即時報價為準")
