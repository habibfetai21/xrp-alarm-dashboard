import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objs as go
import time

st.set_page_config(page_title="Krypto-Dashboard", layout="wide")
st.title("📊 Krypto Dashboard – Live mit CoinPaprika Backup & RSI")

# Coins & IDs
coins = {
    "XRP": "ripple",
    "PEPE": "pepe",
    "DOGE": "dogecoin",
    "FLOKI": "floki",
    "SHIBA": "shiba-inu",
    "VECHAIN": "vechain"
}
portfolio = {
    "TOSHI": 1240005.9318,
    "VISION": 1796.5093,
    "ZEREBRO": 2892.7766
}
fallback_prices = {
    **{c: None for c in coins.keys()},
    "TOSHI": 0.000032, "VISION": 0.085, "ZEREBRO": 0.015
}

# Preis & Historie
@st.cache_data(ttl=60)
def fetch_gecko_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    try:
        return requests.get(url, timeout=10).json()
    except:
        return {}

@st.cache_data(ttl=60)
def fetch_paprika_price(symbol):
    try:
        r = requests.get(f"https://api.coinpaprika.com/v1/tickers/{symbol.lower()}-{symbol.lower()}", timeout=10)
        return r.json().get("quotes", {}).get("EUR", {}).get("price")
    except:
        return None

@st.cache_data(ttl=300)
def fetch_history(id_, days=30):
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{id_}/market_chart",
            params={"vs_currency":"eur","days":days}, timeout=10)
        return [p[1] for p in r.json().get("prices", [])]
    except:
        return []

def calc_rsi(prices, period=14):
    if len(prices) < period:
        return None
    delta = np.diff(prices)
    gain = np.maximum(delta, 0)
    loss = -np.minimum(delta, 0)
    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:]) or 1e-9
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

# Manuelle Aktualisierung
if st.button("🔄 Aktualisieren"):
    st.cache_data.clear()

prices = fetch_gecko_prices()

for coin, cg_id in coins.items():
    st.subheader(f"{coin}")
    price = prices.get(cg_id, {}).get("eur")
    source = "CoinGecko"
    if price is None:
        price = fetch_paprika_price(coin)
        source = "CoinPaprika" if price else "–"
    if price:
        st.metric("Preis (EUR)", f"€{price:.5f}")
    else:
        price = fallback_prices.get(coin)
        if price:
            source = "Fallback"
            st.warning(f"{coin}: Fallback-Preis €{price:.5f}")

    hist = fetch_history(cg_id) if source == "CoinGecko" else []
    if hist:
        st.write(f"RSI 30d: {calc_rsi(pd.Series(hist), 14)} | RSI 7d: {calc_rsi(pd.Series(hist[-7:]),14)} | RSI 1d: {calc_rsi(pd.Series(hist[-1:]),14)}")
        fig = go.Figure(data=[go.Scatter(y=hist, mode='lines', name=coin)])
        fig.update_layout(title=f"{coin} Preisverlauf (30 d)", height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"{coin}: Keine Historie verfügbar ({source})")

for coin, amt in portfolio.items():
    st.markdown(f"### {coin} (Eigenbestand)")
    price = fallback_prices.get(coin)
    st.metric("Preis (Fallback)", f"€{price:.7f}")
    st.metric("Marktwert", f"€{price * amt:,.2f}")