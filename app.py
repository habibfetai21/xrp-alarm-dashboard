import streamlit as st
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ========== Einstellungen ==========
st.set_page_config(page_title="🚨 Krypto Performance Dashboard", layout="wide")
st.title("📊 Krypto Performance Dashboard")

AUTOREFRESH_INTERVAL = 5  # Sekunden
st.caption(f"🔄 Automatische Aktualisierung alle {AUTOREFRESH_INTERVAL} Sekunden")

# ========== Unterstützte Coins ==========
coins = {
    "xrp": "ripple",
    "pepe": "pepe",
    "toshi": None,
    "floki": "floki",
    "vision": None,
    "vechain": "vechain",
    "zerebro": None,
    "doge": "dogecoin",
    "shiba": "shiba-inu"
}

bitpanda_prices = {
    "toshi": "0.000032",
    "vision": "0.085",
    "zerebro": "0.015"
}

bestände = {
    "xrp": 1000,
    "pepe": 9000000,
    "toshi": 1240005.93,
    "floki": 600000,
    "vision": 1796.51,
    "vechain": 3000,
    "zerebro": 2892.77,
    "doge": 2500,
    "shiba": 8000000
}

# ========== RSI Berechnung ==========
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ========== Kursdaten abrufen ==========
@st.cache_data(ttl=300)
def fetch_data_from_coingecko(coin_id, days=30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}&interval=hourly"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        market_caps = pd.DataFrame(data["market_caps"], columns=["timestamp", "market_cap"])

        prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
        prices.set_index("timestamp", inplace=True)
        prices["price"] = prices["price"].astype(float)
        prices["rsi"] = calculate_rsi(prices["price"])

        market_caps["timestamp"] = pd.to_datetime(market_caps["timestamp"], unit="ms")
        market_caps.set_index("timestamp", inplace=True)
        prices["market_cap"] = market_caps["market_cap"]
        return prices
    except:
        return None

# ========== Analysefunktion ==========
def analyze(df, coin, amount):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    market_cap = latest.get("market_cap", None)
    value = price * amount

    st.metric(label=f"{coin.upper()} ➤ Aktueller Preis", value=f"€{price:.5f}")
    st.metric(label=f"{coin.upper()} ➤ Marktwert Bestand", value=f"€{value:,.2f}")
    st.metric(label=f"{coin.upper()} ➤ RSI (14 Tage)", value=f"{rsi:.2f}")
    if market_cap:
        st.metric(label=f"{coin.upper()} ➤ Market Cap", value=f"€{market_cap:,.0f}")

    # Chart
    st.line_chart(df[["price"]].rename(columns={"price": f"{coin.upper()} Preisverlauf"}))

    # Signal
    signal = ""
    if rsi < 30:
        signal = f"🟢 **KAUF-Zone (RSI < 30)**"
    elif rsi > 70:
        signal = f"🔴 **VERKAUF-Zone (RSI > 70)**"
    else:
        signal = f"🟡 **Neutral (RSI zwischen 30-70)**"
    st.info(f"{coin.upper()} Analyse: {signal}")

# ========== Hauptloop ==========
for symbol, coingecko_id in coins.items():
    st.subheader(f"{symbol.upper()} – Analyse")
    if coingecko_id:
        df = fetch_data_from_coingecko(coingecko_id)
        if df is not None:
            analyze(df, symbol, bestände[symbol])
        else:
            st.error(f"{symbol.upper()}: ❌ Kursdaten nicht verfügbar (CoinGecko)")
    else:
        try:
            price = float(bitpanda_prices.get(symbol, "0"))
            amount = bestände.get(symbol, 0)
            value = price * amount
            st.metric(label=f"{symbol.upper()} ➤ Aktueller Preis", value=f"€{price:.5f}")
            st.metric(label=f"{symbol.upper()} ➤ Marktwert Bestand", value=f"€{value:.2f}")
            # Kein RSI/Chart verfügbar
            st.warning(f"{symbol.upper()}: Keine Chartdaten verfügbar – Fallback-Preis verwendet.")
        except:
            st.error(f"{symbol.upper()}: ❌ Kein Preis gefunden")

# ========== Auto-Refresh ==========
st.experimental_rerun()  # ⛔ wird nur lokal unterstützt, auf Streamlit Cloud ggf. deaktivieren
