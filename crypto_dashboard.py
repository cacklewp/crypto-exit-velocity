import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
from streamlit_extras.metric_cards import style_metric_cards 

st.set_page_config(page_title="Exit Velocity Dashboard", layout="wide")

# --- 1. Centralized Static METADATA (Descriptions Only) ---
# This dictionary contains the static text descriptions (key_note).

STATIC_METADATA = {
    "bitcoin": {
        "Composite Exit Velocity": {"key_note": "Minimal selling pressure"},
        "ETF Flows": {"key_note": "Institutions buying; IBIT leads"},
        "Exchange Netflow": {"key_note": "Multi-year lows; HODL bias"},
        "Taker CVD": {"key_note": "Balanced pressure"},
        "STH SOPR": {"key_note": "Losses easing; capitulation near peak"},
        "Supply in Profit": {"key_note": "Bottom zone; ~30% at loss"},
        "Whale/Miner Velocity": {"key_note": "Low accumulation"},
        "Fear & Greed": {"key_note": "Current Market Sentiment"}
    },
    "ethereum": {
        "Composite Exit Velocity": {"key_note": "Selling pressure dropping"},
        "Exchange Netflow": {"key_note": "Strong accumulation"},
        "STH SOPR": {"key_note": "Consolidation zone"},
        "Supply in Profit": {"key_note": "Market in a healthy zone"},
        "Whale/Miner Velocity": {"key_note": "High accumulation"},
        "Fear & Greed": {"key_note": "Current Market Sentiment"}
    },
    "solana": {
        "Composite Exit Velocity": {"key_note": "Velocity is very high"},
        "Exchange Netflow": {"key_note": "Weakest of the majors"},
        "STH SOPR": {"key_note": "Heavy profit-taking"},
        "Supply in Profit": {"key_note": "Near market cycle peak"},
        "Whale/Miner Velocity": {"key_note": "Whales taking profits"},
        "Fear & Greed": {"key_note": "Current Market Sentiment"}
    }
}

# --- 2. Static Styles for Custom Velocity Box ---
VELOCITY_STYLES = {
    "Low": {"color": "#2e7d32", "background": "#e8f5e9"},      # Green
    "Medium": {"color": "#ffb300", "background": "#fff8e1"},   # Yellow
    "High": {"color": "#c62828", "background": "#ffebee"}      # Red
}

# --- 3. Global Configuration Dictionaries (These will be updated in main) ---
fng_values = {"bitcoin": 60, "ethereum": 43, "solana": 42} # Restored original F&G values
fng_labels = {"bitcoin": "Greed", "ethereum": "Neutral", "solana": "Fear"} 
tooltips = {
    "Composite Exit Velocity": "Daily % of supply that moves on-chain. **Low = stronger HODL bias.**",
    "ETF Flows": "Net daily inflows/outflows into spot ETFs (BlackRock, Fidelity, etc.). Positive is bullish.",
    "Exchange Netflow": "14-day SMA of coins moving to/from exchanges. **Negative = accumulation.**",
    "Taker CVD": "Cumulative Volume Delta — aggressive buying vs. selling pressure. **Positive = aggressive buying.**",
    "STH SOPR": "Spent Output Profit Ratio for coins held <155 days. **<1 = realized losses (capitulation).**",
    "Supply in Profit": "% of circulating supply with cost basis below current price. **Low % = capitulation zone.**",
    "Whale/Miner Velocity": "How actively large holders and miners are moving coins. **Low = accumulation.**",
    "Fear & Greed": "A sentiment indicator where 0 is Extreme Fear and 100 is Extreme Greed."
}

# --- 4. API & Utility Functions ---

@st.cache_data(ttl=600)
def get_price(coin_id):
    """Fetches current price and 24h change."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        price = data.get(coin_id, {}).get('usd', 'N/A')
        change = data.get(coin_id, {}).get('usd_24h_change', 'N/A')
        return price, change
    except requests.exceptions.RequestException:
        return "N/A", "N/A"

@st.cache_data(ttl=3600)
def get_global_fng():
    """Fetches global Fear & Greed Index (Placeholder for a live BTC F&G value)."""
    return 60 # Restored original F&G value

def inject_custom_css():
    """Injects custom CSS for the Composite Velocity box."""
    st.markdown(f"""
        <style>
            .stTabs [data-baseweb="tab-list"] {{
                gap: 12px;
            }}
            .stTabs [data-baseweb="tab"] {{
                font-size: 1.1rem;
                padding: 10px 15px;
            }}
            /* Custom styling for the Composite Velocity box */
            div[data-testid="composite-velocity-box"] {{
                padding: 10px 15px;
                border-radius: 8px;
                border: 1px solid #ddd;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }}
        </style>
    """, unsafe_allow_html=True)

def style_signals(val):
    """Applies CSS styling to the Signal column based on value."""
    if val in ["Low", "Strong Positive", "Strong", "Greed", "Positive", "Low accumulation", "Neutral"]:
        color = '#2e7d32' # Green/Bullish/Neutral (Adjusted Neutral to Green for original data consistency)
    elif val in ["High", "Strong Negative", "Extreme Fear", "Negative", "Heavy profit-taking", "Red", "Fear"]:
        color = '#c62828' # Red/Bearish
    elif val in ["Yellow"]:
        color = '#ffb300' # Yellow/Neutral
    else:
        color = '#ffb300' # Default to Yellow/Neutral
        
    return f'color: {color}; font-weight: bold;'

# --- 5. Dynamic Data Fetching Layer (RESTORED ORIGINAL STATIC VALUES) ---

@st.cache_data(ttl=600)
def fetch_signal_data():
    """
    Central function to fetch all signal data. 
    CURRENTLY USING RESTORED STATIC DATA.
    
    ACTION: Replace these dictionaries with real API calls.
    """
    
    # ------------------- BITCOIN LIVE DATA (RESTORED ORIGINAL DATA) -------------------
    btc_data = {
        "Composite Exit Velocity": {"signal": "Low", "current": "0.02–0.05%/day"},
        "ETF Flows": {"signal": "Positive", "current": "+$87.3M"},
        "Exchange Netflow": {"signal": "Strong", "current": "−7K BTC/day"},
        "Taker CVD": {"signal": "Neutral", "current": "Neutral (90d)"},
        "STH SOPR": {"signal": "Yellow", "current": "0.96–0.99"},
        "Supply in Profit": {"signal": "Neutral", "current": "70%"},
        "Whale/Miner Velocity": {"signal": "Low", "current": "1.2% daily supply"},
        "Fear & Greed": {"signal": "Greed", "current": "60"},
    }

    # ------------------- ETHEREUM LIVE DATA (RESTORED ORIGINAL DATA) -------------------
    eth_data = {
         "Composite Exit Velocity": {"signal": "Low", "current": "0.02–0.05%/day"},
        "Exchange Netflow": {"signal": "Strong", "current": "−70K ETH/day"},
        "STH SOPR": {"signal": "Yellow", "current": "0.98–1.01"},
        "Supply in Profit": {"signal": "Neutral", "current": "70%"},
        "Whale/Miner Velocity": {"signal": "Low", "current": "0.5% daily supply"},
        "Fear & Greed": {"signal": "Neutral", "current": "43"},
    }
    
    # ------------------- SOLANA LIVE DATA (RESTORED ORIGINAL DATA) -------------------
    sol_data = {
         "Composite Exit Velocity": {"signal": "Low", "current": "0.02–0.05%/day"},
        "Exchange Netflow": {"signal": "Negative", "current": "+100K SOL/day"},
        "STH SOPR": {"signal": "Red", "current": "1.10–1.20"},
        "Supply in Profit": {"signal": "High", "current": "90%"},
        "Whale/Miner Velocity": {"signal": "High", "current": "10.0% daily supply"},
        "Fear & Greed": {"signal": "Fear", "current": "42"},
    }
    
    return {
        "bitcoin": btc_data,
        "ethereum": eth_data,
        "solana": sol_data,
    }


# --- 6. Updated DataFrame Creation Function (Unchanged) ---

def create_coin_dataframe(coin_key, coin_live_data):
    """Generates the Signal DataFrame by merging live data with static key notes."""
    data_list = []
    static_metadata = STATIC_METADATA[coin_key] 
    
    for metric, meta in static_metadata.items():
        
        # Skip the custom-rendered velocity metric 
        if metric == "Composite Exit Velocity":
            continue
        
        # Get live data for signal and current
        live_values = coin_live_data.get(metric, {})
        signal = live_values.get("signal", "N/A")
        current = live_values.get("current", "N/A")
        key_note = meta["key_note"]
        
        # Special case: Fear & Greed (uses the global fng_values updated in main)
        if metric == "Fear & Greed":
            fng_val = fng_values.get(coin_key, 'N/A')
            fng_lbl = fng_labels.get(coin_key, '')
            current = f"{fng_val} — {fng_lbl}"
            signal = fng_lbl
            
        data_list.append([metric, signal, current, key_note])

    return pd.DataFrame(data_list, columns=["Metric", "Signal", "Current", "Key Note"])


# --- 7. Updated Render Function (Unchanged) ---

def render_coin_tab(coin_id, price, change, live_signals):
    """Renders the complete content (metrics and table) for a single coin tab."""
    
    coin_live_data = live_signals[coin_id]
    
    # Pull the Velocity Data for the custom-styled box
    velocity_data = coin_live_data["Composite Exit Velocity"]
    velocity_style = VELOCITY_STYLES[velocity_data["signal"]]
    
    # Create the data table 
    coin_df = create_coin_dataframe(coin_id, coin_live_data)
    
    st.header(coin_id.capitalize(), divider='blue')
    
    # Row 1: Price, Custom Velocity Box, Fear & Greed Metric
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Price", f"${price:,.2f}", f"{change:+.2f}%" if isinstance(change, (int, float)) else change, help="24 Hour Change")
        
    with c2:
        # --- CUSTOM RENDERED METRIC (Composite Exit Velocity) ---
        st.markdown(f"""
        <div data-testid="composite-velocity-box" style="
            background-color: {velocity_style['background']}; 
            color: {velocity_style['color']}; 
            border-left: 5px solid {velocity_style['color']};
        ">
            <p style='font-weight:bold; font-size:16px; margin:0;'>{velocity_data['signal']} Signal</p>
            <p style='font-size:22px; margin: 0 0;'>Composite Velocity</p>
            <p style='font-size:14px; color:#666; margin:5px 0 0 0;'>{velocity_data["current"]} — {STATIC_METADATA[coin_id]["Composite Exit Velocity"]["key_note"]}</p>
        </div>
        """, unsafe_allow_html=True)

    with c3: 
        fng_current = f"{fng_values[coin_id]} — {fng_labels[coin_id]}"
        st.metric("Fear & Greed", fng_current, help=tooltips["Fear & Greed"])

    # Row 2: Signal Table
    st.subheader(f"{coin_id.capitalize()} On-Chain Signals")
    # Using st.dataframe with custom styling for the Signal column
    st.dataframe(coin_df.style.map(style_signals, subset=["Signal"]), use_container_width=True, hide_index=True)


# --- MAIN APP EXECUTION (Updated F&G logic for restoration) ---

def main():
    # 1. Inject Custom CSS
    inject_custom_css()
    
    # 2. Aesthetic Upgrade: Apply Card Styling
    style_metric_cards(border_left_color="#1877f2", border_size_px=2)
    
    st.title("Crypto Exit Velocity Dashboard")

    # 3. Fetch Global Live Data
    
    # Price data
    btc_price, btc_change = get_price("bitcoin")
    eth_price, eth_change = get_price("ethereum")
    sol_price, sol_change = get_price("solana")
    
    # Fetch all dynamic signal data (Restored static values)
    live_signals = fetch_signal_data()
    
    # Update Fear & Greed values and labels to match the restored original state
    global_fng_value = get_global_fng() # 60
    fng_values["bitcoin"] = global_fng_value
    fng_labels["bitcoin"] = live_signals["bitcoin"]["Fear & Greed"]["signal"] # Greed
    
    fng_values["ethereum"] = int(live_signals["ethereum"]["Fear & Greed"]["current"]) # 43
    fng_labels["ethereum"] = live_signals["ethereum"]["Fear & Greed"]["signal"] # Neutral
    
    fng_values["solana"] = int(live_signals["solana"]["Fear & Greed"]["current"]) # 42
    fng_labels["solana"] = live_signals["solana"]["Fear & Greed"]["signal"] # Fear

    # 4. Render Tabs
    tab1, tab2, tab3 = st.tabs(["Bitcoin (BTC) ₿", "Ethereum (ETH) ♦️", "Solana (SOL) ☀️"])

    with tab1:
        render_coin_tab("bitcoin", btc_price, btc_change, live_signals)
    with tab2:
        render_coin_tab("ethereum", eth_price, eth_change, live_signals)
    with tab3:
        render_coin_tab("solana", sol_price, sol_change, live_signals)

    # Glossary
    with st.expander("Glossary — Click for metric definitions"):
        for metric, definition in tooltips.items():
             st.markdown(f"- **{metric}**: {definition}")

if __name__ == "__main__":
    main()
