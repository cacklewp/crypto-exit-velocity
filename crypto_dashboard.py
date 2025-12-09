import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- Configuration and Setup ---

st.set_page_config(page_title="Exit Velocity Dashboard", layout="wide")

# --- 1. Centralized Static Data ---

STATIC_SIGNALS = {
    "bitcoin": {
        "Composite Exit Velocity": {
            "signal": "Low", 
            "current": "0.02–0.05%/day", 
            "key_note": "Minimal selling pressure",
            "box_color": "#e8f5e9", "signal_color": "#2e7d32"
        },
        "ETF Flows": {"signal": "Positive", "current": "+$87.3M", "key_note": "Institutions buying; IBIT leads"},
        "Exchange Netflow": {"signal": "Strong", "current": "−7K BTC/day", "key_note": "Multi-year lows; HODL bias"},
        "Taker CVD": {"signal": "Neutral", "current": "Neutral (90d)", "key_note": "Balanced pressure"},
        "STH SOPR": {"signal": "Yellow", "current": "0.96–0.99", "key_note": "Losses easing; capitulation near peak"},
        "Supply in Profit": {"signal": "Neutral", "current": "70%", "key_note": "Bottom zone; ~30% at loss"},
        "Whale/Miner Velocity": {"signal": "Low", "current": "1.3×; miners steady", "key_note": "Low churn; supportive cohorts"},
        "Fear & Greed": {"signal": "Yellow", "current": "Global Sentiment", "key_note": "Extreme fear; contrarian buy zone"},
    },
    "ethereum": {
        "Composite Exit Velocity": {
            "signal": "Low", 
            "current": "0.03–0.06%/day", 
            "key_note": "Minimal churn; supply stable",
            "box_color": "#e8f5e9", "signal_color": "#2e7d32"
        },
        "ETF Flows": {"signal": "Mixed", "current": "−$41.6M", "key_note": "ETHA leads; mixed trends"},
        "Exchange Netflow": {"signal": "Strong", "current": "−40K ETH/day", "key_note": "Outflows; staking + HODL bias"},
        "Taker CVD": {"signal": "Neutral", "current": "Neutral (90d)", "key_note": "Balanced absorption"},
        "STH SOPR": {"signal": "Yellow", "current": "0.95–0.99", "key_note": "Losses easing; near breakeven"},
        "Supply in Profit": {"signal": "Neutral", "current": "65–68%", "key_note": "Bottom zone; ~32% underwater"},
        "Whale/Validator Velocity": {"signal": "Low", "current": "Low churn; steady", "key_note": "Accumulation supportive"},
        "Fear & Greed": {"signal": "Yellow", "current": "ETH Sentiment", "key_note": "ETH sentiment: Neutral zone"},
    },
    "solana": {
        "Composite Exit Velocity": {
            "signal": "Medium-Low", 
            "current": "0.04–0.07%/day", 
            "key_note": "Balanced churn; stabilizing",
            "box_color": "#ffebee", "signal_color": "#c62828"
        },
        "ETF Flows": {"signal": "Positive", "current": "+$113K", "key_note": "Rotation phase; watch inflows"},
        "Exchange Netflow": {"signal": "Strong", "current": "−8K SOL/day", "key_note": "Sustained outflows; self-custody rising"},
        "Taker CVD": {"signal": "Neutral", "current": "Neutral (90d)", "key_note": "Absorption at $130 support"},
        "STH SOPR": {"signal": "Yellow", "current": "0.92–0.98", "key_note": "Capitulation easing; top-heavy"},
        "Supply in Profit": {"signal": "Low", "current": "20–22%", "key_note": "2025 low zone; ~78% at loss"},
        "Whale/Validator Velocity": {"signal": "Low", "current": "Low churn; steady", "key_note": "Whale accumulation intact"},
        "Fear & Greed": {"signal": "Yellow", "current": "SOL Sentiment", "key_note": "SOL sentiment: Neutral zone"},
    }
}

# Tooltip definitions
tooltips = {
    "Composite Exit Velocity": "Daily % of supply that moves on-chain. Lower = stronger HODL bias.",
    "ETF Flows": "Net daily inflows/outflows into spot BTC/ETH/SOL ETFs (BlackRock, Fidelity, etc.).",
    "Exchange Netflow": "14-day SMA of coins moving to/from exchanges. Negative = accumulation.",
    "Taker CVD": "Cumulative Volume Delta — measures aggressive buying vs. selling pressure.",
    "STH SOPR": "Spent Output Profit Ratio for coins held <155 days. <1 = realized losses.",
    "Supply in Profit": "% of circulating supply with cost basis below current price.",
    "Whale/Miner Velocity": "How actively large holders/miners are spending.",
    "Fear & Greed": "Market-wide sentiment index (0 = Extreme Fear, 100 = Extreme Greed).",
}

# F&G values (Note: ETH and SOL are currently hardcoded, BTC is live)
fng_values = {
    "bitcoin": None, # Will be updated by get_global_fng
    "ethereum": 43, 
    "solana": 42
}
fng_labels = {
    "bitcoin": "Extreme Fear",
    "ethereum": "Neutral",
    "solana": "Neutral"
}

# --- 2. Live Data Fetching (Using @st.cache_data for performance) ---

@st.cache_data(ttl=300)
def get_global_fng():
    """Fetches the Fear & Greed Index value."""
    try:
        data = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()
        return int(data["data"][0]["value"])
    except:
        return 23

@st.cache_data(ttl=60)
def get_price(coin):
    """Fetches live price and 24h change for a coin."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
        if coin in data:
            return data[coin]["usd"], round(data[coin].get("usd_24hr_change", 0), 2)
    except:
        pass
    # Fallback data if API fails (Ensures no crash)
    return {"bitcoin": (89300, -3.3), "ethereum": (3030, -1.8), "solana": (140, -2.1)}.get(coin, (0, 0))

# This function is kept for completeness, but not used in the UI since the chart was removed.
@st.cache_data(ttl=3600)
def get_historical_price_data(coin_id="bitcoin", days=90):
    """
    Fetches historical price data from CoinGecko.
    Includes the critical bug fix (returning a DataFrame instead of None on failure).
    """
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
        
        if 'prices' in data and data['prices']:
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'Price'])
            df['Date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
            df = df.set_index('Date').drop(columns=['timestamp']).groupby(df.index).last()
            return df
    except Exception as e:
        st.warning(f"Could not load historical data for {coin_id}. Error: {e}")
        # **This line is the critical fix** - returns an empty DataFrame instead of None
        return pd.DataFrame() 
    return pd.DataFrame() 

# --- 3. Utility Functions ---

def inject_custom_css():
    """Injects custom CSS to style the velocity box and other elements."""
    st.markdown("""
    <style>
    /* Styling for the central velocity metric box */
    .velocity-box {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%; /* Ensure columns are aligned */
    }
    .stDataFrame {
        border-radius: 8px;
    }
    .stMetric {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


def style_signals(val):
    """Applies conditional formatting to the Signal column in the DataFrame."""
    if any(x in val for x in ["Low", "Positive", "Strong"]):
        return "background-color: #d4edda; color: #155724" # Green
    elif any(x in val for x in ["Yellow", "Neutral", "Medium-Low", "Mixed"]):
        return "background-color: #fff3cd; color: #856404" # Yellow
    elif "Neutral" in val:
        return "background-color: #f8f9fa; color: #495057" # Light Gray
    return ""

def create_coin_dataframe(coin_key):
    """Generates the Signal DataFrame for a given coin."""
    data_list = []
    data_source = STATIC_SIGNALS[coin_key]
    
    for metric, values in data_source.items():
        signal = values["signal"]
        current = values["current"]
        key_note = values["key_note"]
        
        # Inject live F&G value
        if metric == "Fear & Greed":
            fng_val = fng_values.get(coin_key, 'N/A')
            fng_lbl = fng_labels.get(coin_key, '')
            current = f"{fng_val} — {fng_lbl}"
            
        data_list.append([metric, signal, current, key_note])

    return pd.DataFrame(data_list, columns=["Metric", "Signal", "Current", "Key Note"])

# --- 4. Reusable Tab Component (MODULARITY FIX) ---

def render_coin_tab(coin_id, price, change):
    """Renders the complete content (metrics and table) for a single coin tab."""
    
    velocity_data = STATIC_SIGNALS[coin_id]["Composite Exit Velocity"]
    coin_df = create_coin_dataframe(coin_id)

    # Price formatting: BTC/ETH as integer, SOL as 2 decimals
    price_format = ",.0f" if coin_id in ["bitcoin", "ethereum"] else ",.2f"
    formatted_price = f"${price:{price_format}}"
    
    st.header(f"{coin_id.capitalize()} Exit Velocity Dashboard")
    
    # Header Metrics (using columns)
    col1, col2, col3 = st.columns([1.7, 1.5, 1])
    
    with col1: 
        st.metric(f"{coin_id.upper()} Price", formatted_price, f"{change:+.1f}%", help="Live spot price from CoinGecko")
    
    with col2:
        # Composite Velocity Box (Using centralized data for colors)
        st.markdown(f"""
        <div class='velocity-box' style='background-color:{velocity_data["box_color"]};'>
            <h2 style='color:{velocity_data["signal_color"]}; margin:0;'>{velocity_data["signal"]}</h2>
            <p style='font-size:18px; color:#555; margin:10px 0 0 0;'>Composite Velocity</p>
            <p style='font-size:14px; color:#666; margin:5px 0 0 0;'>{velocity_data["current"]} — {velocity_data["key_note"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3: 
        # Fear & Greed
        fng_current = f"{fng_values.get(coin_id, 'N/A')} — {fng_labels.get(coin_id, '')}"
        st.metric("Fear & Greed", fng_current, help=tooltips["Fear & Greed"])

    # Signal Table
    st.dataframe(coin_df.style.map(style_signals, subset=["Signal"]), width='stretch', hide_index=True)
    
    st.divider()


# --- 5. Main Execution Flow ---

def main():
    # 1. Inject Custom CSS
    inject_custom_css()
    
    # 2. Fetch Global Live Data (Only needs to run once per refresh)
    # Price data
    btc_price, btc_change = get_price("bitcoin")
    eth_price, eth_change = get_price("ethereum")
    sol_price, sol_change = get_price("solana")
    
    # Global F&G (Update the value in the global dictionary)
    fng_values["bitcoin"] = get_global_fng()
    
    # Timestamp for footer
    now_est = datetime.now(pytz.timezone('America/New_York')).strftime("%b %d, %Y %I:%M:%S %p")
    
    # 3. Render Tabs
    tab1, tab2, tab3 = st.tabs(["Bitcoin", "Ethereum", "Solana"])
    
    with tab1:
        render_coin_tab("bitcoin", btc_price, btc_change)
    
    with tab2:
        render_coin_tab("ethereum", eth_price, eth_change)

    with tab3:
        render_coin_tab("solana", sol_price, sol_change)

    # 4. Footer Content
    with st.expander("Glossary — Click for metric definitions"):
        st.markdown("""
        - **Composite Exit Velocity**: Daily % of supply that moves on-chain. Lower = stronger HODL bias.
        - **ETF Flows**: Net daily inflows/outflows into spot ETFs (BlackRock, Fidelity, etc.).
        - **Exchange Netflow**: 14-day SMA of coins moving to/from exchanges. Negative = accumulation.
        - **Taker CVD**: Cumulative Volume Delta — aggressive buying vs. selling pressure.
        - **STH SOPR**: Spent Output Profit Ratio for coins held <155 days. <1 = realized losses.
        - **Supply in Profit**: % of circulating supply with cost basis below current price.
        - **Whale/Miner Velocity**: How actively large holders/miners are spending.
        - **Fear & Greed**: Market-wide sentiment index (0 = Extreme Fear, 100 = Extreme Greed).
        """)
    
    st.caption(f"Last updated: {now_est} EST • Data: CoinGecko, Alternative.me, CFGI.io, Farside Investors")


if __name__ == "__main__":
    main()
