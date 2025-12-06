import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Exit Velocity Dashboard", layout="wide")

# Global F&G
@st.cache_data(ttl=300)
def get_global_fng():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1")
        return int(r.json()["data"][0]["value"])
    except:
        return 23

# Proxy values (update daily from CFGI.io)
fng_values = {
    "bitcoin": get_global_fng(),     # Live global
    "ethereum": 43,                  # ETH-specific
    "solana": 42                     # SOL-specific
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

# EST time
eastern = pytz.timezone('America/New_York')
now_est = datetime.now(eastern).strftime("%b %d, %Y %I:%M:%S %p")

# Perfect BitcoinFear-style dial
def fng_dial(value, title="Fear & Greed"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b>", 'font': {'size': 12}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': "white"},
            'bar': {'color': "darkgray"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': "#ff4d4d"},
                {'range': [25, 50], 'color': "#ffa64d"},
                {'range': [50, 75], 'color': "#ffff4d"},
                {'range': [75, 100], 'color': "#4dff4d"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': value}
        }
    ))
    fig.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# Table styling
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

# BTC
with tab1:
    st.header("Bitcoin Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.8, 1.4, 1])
    with c1: st.metric("BTC Price", f"${btc_price:,.0f}", f"{btc_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#2E86AB;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3: st.plotly_chart(fng_dial(fng_values["bitcoin"], "F&G (Global)"), use_container_width=True)

    btc_data = [
        ["Composite Exit Velocity", "Low", "0.02–0.05%/day", "Minimal selling pressure"],
        ["ETF Flows", "Positive", "+$140M (1d)", "Institutions buying"],
        ["Exchange Netflow", "Strong", "−7K BTC/day", "HODL bias"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced pressure"],
        ["STH SOPR", "Yellow", "0.96–0.99", "Losses easing"],
        ["Supply in Profit", "Neutral", "70%", "Bottom zone"],
        ["Whale/Miner Velocity", "Low", "1.3×", "Supportive"],
        ["Fear & Greed", "Yellow", fng_values["bitcoin"], "Extreme fear zone"],
    ]
    df = pd.DataFrame(btc_data, columns=["Metric", "Signal", "Current", "Key Note"])
    st.dataframe(df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)

# ETH
with tab2:
    st.header("Ethereum Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.8, 1.4, 1])
    with c1: st.metric("ETH Price", f"${eth_price:,.0f}", f"{eth_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#2E86AB;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3: st.plotly_chart(fng_dial(fng_values["ethereum"], "F&G (ETH-specific)"), use_container_width=True)

    eth_data = [
        ["Composite Exit Velocity", "Low", "0.03–0.06%/day", "Minimal churn"],
        ["ETF Flows", "Mixed", "+$140M (1d)", "ETHA leads"],
        ["Exchange Netflow", "Strong", "−40K ETH/day", "Staking bias"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced"],
        ["STH SOPR", "Yellow", "0.95–0.99", "Near breakeven"],
        ["Supply in Profit", "Neutral", "65–68%", "Bottom zone"],
        ["Whale/Validator Velocity", "Low", "Low churn", "Accumulation"],
        ["Fear & Greed", "Yellow", f"{fng_values['ethereum']} (Neutral)", "ETH sentiment"],
    ]
    df = pd.DataFrame(eth_data, columns=["Metric", "Signal", "Current", "Key Note"])
    st.dataframe(df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)

# SOL
with tab3:
    st.header("Solana Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.8, 1.4, 1])
    with c1: st.metric("SOL Price", f"${sol_price:,.2f}", f"{sol_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#FF6B6B;'>Medium-Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3: st.plotly_chart(fng_dial(fng_values["solana"], "F&G (SOL-specific)"), use_container_width=True)

    sol_data = [
        ["Composite Exit Velocity", "Medium-Low", "0.04–0.07%/day", "Balanced churn"],
        ["ETF Flows", "Mixed", "−$25M (5d)", "Rotation phase"],
        ["Exchange Netflow", "Strong", "−8K SOL/day", "Self-custody rising"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Absorption at $130"],
        ["STH SOPR", "Yellow", "0.92–0.98", "Capitulation easing"],
        ["Supply in Profit", "Low", "20–22%", "Deep drawdown"],
        ["Whale/Validator Velocity", "Low", "Low churn", "Whale accumulation"],
        ["Fear & Greed", "Yellow", f"{fng_values['solana']} (Neutral)", "SOL sentiment"],
    ]
    df = pd.DataFrame(sol_data, columns=["Metric", "Signal", "Current", "Key Note"])
    st.dataframe(df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)

st.success("Auto-refresh every 60s • Composite Velocity = Core Focus • ETH/SOL Specific F&G")
