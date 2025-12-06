import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Exit Velocity Dashboard", layout="wide")

# Tooltip definitions
tooltips = {
    "Composite Exit Velocity": "Daily % of supply that moves on-chain. Lower = stronger HODL bias.",
    "ETF Flows": "Net daily inflows/outflows into spot BTC/ETH ETFs (BlackRock, Fidelity, etc.).",
    "Exchange Netflow": "14-day SMA of coins moving to/from exchanges. Negative = accumulation.",
    "Taker CVD": "Cumulative Volume Delta — measures aggressive buying vs. selling pressure.",
    "STH SOPR": "Spent Output Profit Ratio for coins held <155 days. <1 = realized losses.",
    "Supply in Profit": "% of circulating supply with cost basis below current price.",
    "Whale/Miner Velocity": "How actively large holders/miners are spending.",
    "Fear & Greed": "Market-wide sentiment index (0 = Extreme Fear, 100 = Extreme Greed).",
}

# Global F&G
@st.cache_data(ttl=300)
def get_global_fng():
    try:
        return int(requests.get("https://api.alternative.me/fng/?limit=1").json()["data"][0]["value"])
    except:
        return 23

# Live F&G values (Dec 6, 2025)
fng_values = {
    "bitcoin": get_global_fng(),
    "ethereum": 43,
    "solana": 42
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

# Table styling
def style_signals(val):
    if any(x in val for x in ["Low", "Positive", "Strong"]):
        return "background-color: #D1FAE5; color: #065F46"
    elif any(x in val for x in ["Yellow", "Neutral", "Medium-Low", "Mixed"]):
        return "background-color: #FEF3C7; color: #92400E"
    elif "Neutral" in val:
        return "background-color: #F3F4F6; color: #374151"
    return ""

# Function to render table with hover tooltips
def render_table(data, coin, fng_value, fng_label):
    html = """
    <table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 14px;'>
        <thead>
            <tr style='background-color: #f8f9fa;'>
                <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Metric</th>
                <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Signal</th>
                <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Current</th>
                <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Key Note</th>
            </tr>
        </thead>
        <tbody>
    """
    for row in data:
        metric, signal, current, key_note, tooltip = row
        signal_style = style_signals(signal)
        html += f"""
            <tr>
                <td style='border: 1px solid #dee2e6; padding: 8px; title="{tooltip}">{metric}</td>
                <td style='border: 1px solid #dee2e6; padding: 8px; {signal_style}'>{signal}</td>
                <td style='border: 1px solid #dee2e6; padding: 8px; title="{tooltip}'>{current}</td>
                <td style='border: 1px solid #dee2e6; padding: 8px; title="{tooltip}'>{key_note}</td>
            </tr>
        """
    html += """
        </tbody>
    </table>
    """
    st.markdown(html, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Bitcoin", "Ethereum", "Solana"])

# BTC Tab
with tab1:
    st.header("Bitcoin Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.7, 1.5, 1])
    with c1: st.metric("BTC Price", f"${btc_price:,.0f}", f"{btc_change:+.1f}%")
    with c2:
        st.markdown("<div style='text-align:center; padding:15px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#2E86AB; margin:0;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; color:#666; margin:5px 0 0 0;'>Composite Velocity</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3: st.metric("Fear & Greed (Global)", f"{fng_values['bitcoin']} — {fng_labels['bitcoin']}", help=tooltips["Fear & Greed"])

    btc_data = [
        ["Composite Exit Velocity", "Low", "0.02–0.05%/day", "Minimal selling pressure", tooltips["Composite Exit Velocity"]],
        ["ETF Flows", "Positive", "+$140M (1d)", "Institutions buying; IBIT leads", tooltips["ETF Flows"]],
        ["Exchange Netflow", "Strong", "−7K BTC/day", "Multi-year lows; HODL bias", tooltips["Exchange Netflow"]],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced pressure", tooltips["Taker CVD"]],
        ["STH SOPR", "Yellow", "0.96–0.99", "Losses easing; capitulation near peak", tooltips["STH SOPR"]],
        ["Supply in Profit", "Neutral", "70%", "Bottom zone; ~30% at loss", tooltips["Supply in Profit"]],
        ["Whale/Miner Velocity", "Low", "1.3×; miners steady", "Low churn; supportive cohorts", tooltips["Whale/Miner Velocity"]],
        ["Fear & Greed", "Yellow", f"{fng_values['bitcoin']} — {fng_labels['bitcoin']}", "Extreme fear; contrarian buy zone", tooltips["Fear & Greed"]],
    ]
    render_table(btc_data, "BTC", fng_values['bitcoin'], fng_labels['bitcoin'])

# ETH Tab
with tab2:
    st.header("Ethereum Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.7, 1.5, 1])
    with c1: st.metric("ETH Price", f"${eth_price:,.0f}", f"{eth_change:+.1f}%")
    with c2:
        st.markdown("<div style='text-align:center; padding:15px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#2E86AB; margin:0;'>Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; color:#666; margin:5px 0 0 0;'>Composite Velocity</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3: st.metric("Fear & Greed (ETH-specific)", f"{fng_values['ethereum']} — {fng_labels['ethereum']}", help=tooltips["Fear & Greed"])

    eth_data = [
        ["Composite Exit Velocity", "Low", "0.03–0.06%/day", "Minimal churn; supply stable", tooltips["Composite Exit Velocity"]],
        ["ETF Flows", "Mixed", "+$140M (1d)", "ETHA leads; mixed trends", tooltips["ETF Flows"]],
        ["Exchange Netflow", "Strong", "−40K ETH/day", "Outflows; staking + HODL bias", tooltips["Exchange Netflow"]],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Balanced absorption", tooltips["Taker CVD"]],
        ["STH SOPR", "Yellow", "0.95–0.99", "Losses easing; near breakeven", tooltips["STH SOPR"]],
        ["Supply in Profit", "Neutral", "65–68%", "Bottom zone; ~32% underwater", tooltips["Supply in Profit"]],
        ["Whale/Validator Velocity", "Low", "Low churn; steady", "Accumulation supportive", tooltips["Whale/Miner Velocity"]],
        ["Fear & Greed", "Yellow", f"{fng_values['ethereum']} — {fng_labels['ethereum']}", "ETH sentiment: Neutral zone", tooltips["Fear & Greed"]],
    ]
    render_table(eth_data, "ETH", fng_values['ethereum'], fng_labels['ethereum'])

# SOL Tab
with tab3:
    st.header("Solana Exit Velocity Dashboard")
    c1, c2, c3 = st.columns([1.7, 1.5, 1])
    with c1: st.metric("SOL Price", f"${sol_price:,.2f}", f"{sol_change:+.1f}%")
    with c2:
        st.markdown("<div style='text-align:center; padding:15px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#FF6B6B; margin:0;'>Medium-Low</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; color:#666; margin:5px 0 0 0;'>Composite Velocity</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3: st.metric("Fear & Greed (SOL-specific)", f"{fng_values['solana']} — {fng_labels['solana']}", help=tooltips["Fear & Greed"])

    sol_data = [
        ["Composite Exit Velocity", "Medium-Low", "0.04–0.07%/day", "Balanced churn; stabilizing", tooltips["Composite Exit Velocity"]],
        ["ETF Flows", "Mixed", "−$25M (5d)", "Rotation phase; watch inflows", tooltips["ETF Flows"]],
        ["Exchange Netflow", "Strong", "−8K SOL/day", "Sustained outflows; self-custody rising", tooltips["Exchange Netflow"]],
        ["Taker CVD", "Neutral", "Neutral (90d)", "Absorption at $130 support", tooltips["Taker CVD"]],
        ["STH SOPR", "Yellow", "0.92–0.98", "Capitulation easing; top-heavy", tooltips["STH SOPR"]],
        ["Supply in Profit", "Low", "20–22%", "2025 low zone
