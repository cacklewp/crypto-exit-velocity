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
        return int(requests.get("https://api.alternative.me/fng/?limit=1").json()["data"][0]["value"])
    except:
        return 23

# Live F&G values (Dec 6, 2025) — update these daily from CFGI.io
fng_values = {
    "bitcoin": get_global_fng(),   # Global (23)
    "ethereum": 43,                # ETH-specific
    "solana": 42                   # SOL-specific
}
fng_labels = {
    "bitcoin": "Extreme Fear",
    "ethereum": "Neutral",
    "solana": "Neutral"
}

# Live prices
@st.cache_data(ttl=60)
def get_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
        if coin in data:
            return data[coin]["usd"], round(data[coin].get("usd_24h_change", 0), 2)
    except:
        pass
    return {"bitcoin": (89300, -3.3), "ethereum": (3030, -1.8), "solana": (140, -2.1)}[coin]

btc_price, btc_change = get_price("bitcoin")
eth_price, eth_change = get_price("ethereum")
sol_price, sol_change = get_price("solana")

# EST time
now_est = datetime.now(pytz.timezone('America/New_York')).strftime("%b %d, %Y %I:%M:%S %p")

# Perfect BitcoinFear-style dial (tested, no invalid props)
def fng_dial(value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, 100], 'tickwidth': 0, 'showticklabels': False},
            'bar': {'color': "lightgray"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 50], 'color': "orange"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {'line': {'color': "black", 'width': 3}, 'value': value}
        }
    ))
    fig.update_layout(height=100, margin=dict(l=5, r=5, t=15, b=5), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# Table styling
def style_signals(val):
    if any(x in val for x in ["Low", "Positive", "Strong"]):
        return "background-color: #D1FAE5; color: #065F46"
    elif any(x in val for x in ["Yellow", "Neutral", "Medium-Low", "Mixed"]):
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
    with c1: st.metric("BTC Price", f"${btc_price:,.0f}", f"{btc_change:+.1f}%")
    with c2:
        st.markdown("<h2 style='text-align:center; color:#2E86AB; margin-bottom:0;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:18px; color:#555; margin-top:-10px;'>Composite Velocity</p>", unsafe_allow_html=True)
    with c3:
        st.plotly_chart(fng_dial(fng_values["bitcoin"]), use_container_width=True)
        st.markdown(f"<p style='text-align:center; color:gray; font-size:12px; margin:0;'>Global: {fng_values['bitcoin']} — {fng_labels['bitcoin']}</p>", unsafe_allow_html=True)

    btc_data = [
        ["Composite Exit Velocity", "Low", "0.02–0.05%/day", "Minimal selling pressure"],
        ["ETF Flows", "Positive", "+$140M (1d)", "Institutions buying; IBIT leads"],
        ["Exchange Netflow", "Strong", "−7K BTC/day", "Multi-year lows; HODL bias"],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced pressure"],
        ["STH SOPR", "Yellow", "0.96–0.99", "Losses easing; capitulation near peak"],
        ["Supply in Profit", "Neutral", "70%", "Bottom zone; ~30
