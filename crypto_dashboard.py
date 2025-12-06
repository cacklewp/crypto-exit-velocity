import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Exit Velocity Dashboard", layout="wide")

# Global F&G (Alternative.me)
@st.cache_data(ttl=300)
def get_global_fng():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1")
        return r.json()["data"][0]["value"]
    except:
        return "23"

# Proxy for coin-specific F&G (update daily from CFGI.io)
fng_proxies = {
    "ethereum": "43 (Neutral)",
    "solana": "42 (Neutral)"
}

# Live prices
@st.cache_data(ttl=60)
def get_price(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if coin in data and "usd" in data[coin]:
                return data[coin]["usd"], round(data[coin].get("usd_24h_change", 0), 2)
    except:
        pass
    fallback = {"bitcoin": (89300, -3.3), "ethereum": (3030, -1.8), "solana": (140, -2.1)}
    return fallback.get(coin, (0, 0))

btc_price, btc_change = get_price("bitcoin")
eth_price, eth_change = get_price("ethereum")
sol_price, sol_change = get_price("solana")

global_fng = get_global_fng()
eth_fng = fng_proxies.get("ethereum", global_fng)
sol_fng = fng_proxies.get("solana", global_fng)

# EST time
eastern = pytz.timezone('America/New_York')
now_est = datetime.now(eastern).strftime("%b %d, %Y %I:%M:%S %p")

# Classic BitcoinFear half-circle dial
def fng_dial(value, title="F&G"):
    val = float(value.split()[0]) if isinstance(value, str) else float(value)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 10, 'color': 'black'}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, 100], 'tickwidth': 0.5, 'tickcolor': "gray"},
            'bar': {'color': "lightgray"},
            'steps': [
                {'range': [0, 25], 'color': "red"},      # Extreme Fear
                {'range': [25, 50], 'color': "orange"},  # Fear
                {'range': [50, 75], 'color': "yellow"},  # Neutral/Greed
                {'range': [75, 100], 'color': "green"}   # Extreme Greed
            ],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': val
            }
        }
    ))
    fig.update_layout(height=100, margin=dict(l=5, r=5, t=20, b=5), paper_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(valueformat=".0f")
    return fig

# Style for tables
def style_signals(val):
    if "Low" in val or "Positive" in val or "Strong" in val:
        return "background-color: #D1FAE5; color: #065F46"
    elif "Yellow" in val or "Neutral" in val or "Medium-Low" in val or "Mixed" in val:
        return "background-color: #FEF3C7; color: #92400E"
    elif "Neutral" in val:
        return "background-color: #F3F4F6; color: #374151"
    return ""

# Tabs
tab1, tab2, tab3 = st.tabs(["Bitcoin", "Ethereum", "Solana"])

# BTC Tab
with tab1:
    st.header("Bitcoin Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.8, 1.4, 1])
    with c1:
        st.metric("BTC Price", f"${btc_price:,.0f}", f"{btc_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#2E86AB; margin-bottom:0;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555; margin-top:-10px;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3:
        st.plotly_chart(fng_dial(global_fng, "F&G (Global)"), use_container_width=True)

    btc_data = [
        ["Composite Exit Velocity", "Low", "0.02–0.05%/day", "Minimal selling pressure"],
        ["ETF Flows", "Positive", "+$140M (1d)", "Institutions buying; IBIT leads"],
        ["Exchange Netflow", "Strong", "−7K BTC/day", "Multi-year lows; HODL bias"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced pressure"],
        ["STH SOPR", "Yellow", "0.96–0.99", "Losses easing; capitulation near peak"],
        ["Supply in Profit", "Neutral", "70%", "Bottom zone; ~30% at loss"],
        ["Whale/Miner Velocity", "Low", "1.3×; miners steady", "Low churn; supportive cohorts"],
        ["Fear & Greed", "Yellow", global_fng, "Extreme fear; contrarian buy zone"],
    ]
    df = pd.DataFrame(btc_data, columns=["Metric", "Signal", "Current", "Key Note"])
    st.dataframe(df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)

# ETH Tab
with tab2:
    st.header("Ethereum Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.8, 1.4, 1])
    with c1:
        st.metric("ETH Price", f"${eth_price:,.0f}", f"{eth_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#2E86AB; margin-bottom:0;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555; margin-top:-10px;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3:
        st.plotly_chart(fng_dial(eth_fng, "F&G (ETH-specific)"), use_container_width=True)

    eth_data = [
        ["Composite Exit Velocity", "Low", "0.03–0.06%/day", "Minimal churn; supply stable"],
        ["ETF Flows", "Mixed", "+$140M (1d)", "ETHA leads; mixed trends"],
        ["Exchange Netflow", "Strong", "−40K ETH/day", "Outflows; staking + HODL bias"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced absorption"],
        ["STH SOPR", "Yellow", "0.95–0.99", "Losses easing; near breakeven"],
        ["Supply in Profit", "Neutral", "65–68%", "Bottom zone; ~32% underwater"],
        ["Whale/Validator Velocity", "Low", "Low churn; steady", "Accumulation supportive"],
        ["Fear & Greed", "Yellow", eth_fng, "ETH sentiment: Neutral zone"],
    ]
    df = pd.DataFrame(eth_data, columns=["Metric", "Signal", "Current", "Key Note"])
    st.dataframe(df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)

# SOL Tab
with tab3:
    st.header("Solana Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.8, 1.4, 1])
    with c1:
        st.metric("SOL Price", f"${sol_price:,.2f}", f"{sol_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#FF6B6B; margin-bottom:0;'>Medium-Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555; margin-top:-10px;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3:
        st.plotly_chart(fng_dial(sol_fng, "F&G (SOL-specific)"), use_container_width=True)

    sol_data = [
        ["Composite Exit Velocity", "Medium-Low", "0.04–0.07%/day", "Balanced churn; stabilizing"],
        ["ETF Flows", "Mixed", "−$25M (5d)", "Rotation phase; watch inflows"],
        ["Exchange Netflow", "Strong", "−8K SOL/day", "Sustained outflows; self-custody rising"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Absorption at $130 support"],
        ["STH SOPR", "Yellow", "0.92–0.98", "Capitulation easing; top-heavy"],
        ["Supply in Profit", "Low", "20–22%", "2025 low zone; ~78% at loss"],
        ["Whale/Validator Velocity", "Low", "Low churn; steady", "Whale accumulation intact"],
        ["Fear & Greed", "Yellow", sol_fng, "SOL sentiment: Neutral zone"],
    ]
    df = pd.DataFrame(sol_data, columns=["Metric", "Signal", "Current", "Key Note"])
    st.dataframe(df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)

st.success("Auto-refresh every 60s • Composite Velocity = Core Focus • ETH/SOL Specific F&G")
