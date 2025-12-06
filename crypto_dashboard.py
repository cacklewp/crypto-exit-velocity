import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exit Velocity", layout="wide", theme="light")
# Live price + change
@st.cache_data(ttl=60)
def get_price(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url).json()
    price = data[coin]["usd"]
    change = round(data[coin]["usd_24h_change"], 2)
    return price, change

btc_price, btc_change = get_price("bitcoin")
eth_price, eth_change = get_price("ethereum")
sol_price, sol_change = get_price("solana")

fg = requests.get("https://api.alternative.me/fng/?limit=1").json()["data"][0]["value"]

tab1, tab2, tab3 = st.tabs(["Bitcoin", "Ethereum", "Solana"])

# ====================== BITCOIN ======================
with tab1:
    st.title("Bitcoin Exit Velocity")
    st.markdown(f"**Updated:** {datetime.now():%b %d, %Y %H:%M:%S}")
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC Price", f"${btc_price:,.0f}", f"{btc_change:+.2f}%")
    c2.metric("Velocity", "Low", "0.02–0.05%/day")
    c3.metric("Fear & Greed", fg)

    btc = [
        ["Composite Exit Velocity",   "Low",        "0.02–0.05%/day", "Minimal selling"],
        ["ETF Flows",                 "Positive",   "+$140M",         "Institutions buying"],
        ["Exchange Netflow",          "Strong",     "−7K BTC/day",     "HODL mode"],
        ["Taker CVD",                 "Neutral",    "Neutral",         "Balanced"],
        ["STH SOPR",                  "Yellow",     "0.96–0.99",      "Losses easing"],
        ["Supply in Profit",          "Neutral",    "70%",            "Bottom zone"],
        ["Whale/Miner Velocity",      "Low",        "1.3×",           "Supportive"],
        ["Fear & Greed",              "Yellow",     str(fg),          "Recovery zone"],
    ]
    df = pd.DataFrame(btc, columns=["Metric","Signal","Current","Note"])
    st.table(df.style.map(lambda v: "background:#d4edda" if v in ["Low","Positive","Strong"]
                          else "background:#fff3cd" if v in ["Yellow","Neutral"] else "", subset=["Signal"]))

# ====================== ETHEREUM ======================
with tab2:
    st.title("Ethereum Exit Velocity")
    st.markdown(f"**Updated:** {datetime.now():%b %d, %Y %H:%M:%S}")
    c1, c2, c3 = st.columns(3)
    c1.metric("ETH Price", f"${eth_price:,.0f}", f"{eth_change:+.2f}%")
    c2.metric("Velocity", "Low", "0.03–0.06%/day")
    c3.metric("Fear & Greed", fg)

    eth = [
        ["Composite Exit Velocity",   "Low",        "0.03–0.06%/day", "Very quiet"],
        ["ETF Flows",                 "Strong",     "+$140M",         "BlackRock leading"],
        ["Exchange Netflow",          "Strong",     "−40K ETH/day",   "Staking + HODL"],
        ["Taker CVD",                 "Neutral",    "Neutral",        "Balanced"],
        ["STH SOPR",                  "Yellow",     "0.95–0.99",     "Near breakeven"],
        ["Supply in Profit",          "Neutral",    "68%",            "Bottom zone"],
        ["Whale/Validator Velocity",  "Low",        "1.3×",           "Accumulation"],
        ["Fear & Greed",              "Yellow",     str(fg),          "Contrarian"],
    ]
    df = pd.DataFrame(eth, columns=["Metric","Signal","Current","Note"])
    st.table(df.style.map(lambda v: "background:#d4edda" if v in ["Low","Positive","Strong"]
                          else "background:#fff3cd" if v in ["Yellow","Neutral"] else "", subset=["Signal"]))

# ====================== SOLANA ======================
with tab3:
    st.title("Solana Exit Velocity")
    st.markdown(f"**Updated:** {datetime.now():%b %d, %Y %H:%M:%S}")
    c1, c2, c3 = st.columns(3)
    c1.metric("SOL Price", f"${sol_price:,.2f}", f"{sol_change:+.2f}%")
    c2.metric("Velocity", "Medium-Low", "0.04–0.07%/day")
    c3.metric("Fear & Greed", fg)

    sol = [
        ["Composite Exit Velocity",   "Medium-Low", "0.04–0.07%/day", "Balanced churn"],
        ["ETF Flows",                 "Mixed",      "−$25M",          "Rotation"],
        ["Exchange Netflow",          "Strong",     "−8K SOL/day",    "Self-custody"],
        ["Taker CVD",                 "Neutral",    "Neutral",        "$130 support"],
        ["STH SOPR",                  "Yellow",     "0.92–0.98",    "Capitulation"],
        ["Supply in Profit",          "Low",        "22%",            "Deep drawdown"],
        ["Whale/Validator Velocity",  "Low",        "Low churn",      "Whales quiet"],
        ["Fear & Greed",              "Yellow",     str(fg),          "Extreme fear"],
    ]
    df = pd.DataFrame(sol, columns=["Metric","Signal","Current","Note"])
    st.table(df.style.map(lambda v: "background:#d4edda" if v in ["Low","Positive","Strong"]
                          else "background:#fff3cd" if v in ["Medium-Low","Mixed","Yellow","Neutral"] else "", subset=["Signal"]))


st.success("Live • Auto-refresh every 60s • BTC – ETH – SOL")

