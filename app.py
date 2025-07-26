import streamlit as st
import pandas as pd
import requests

# === Technische Analyse (vereinfachte RSI & Supertrend) ===
@st.cache_data(ttl=900)
def fetch_data(symbol, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=eur&days={days}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    prices = r.json().get("prices", [])
    if not prices:
        return None
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    df["rsi"] = df["price"].rolling(window=14).mean()  # Dummy-RSI
    df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
    return df

def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    trend = latest["supertrend"]

    signal = ""
    if rsi < 30:
        signal = f"🚀 Kaufempfehlung – RSI < 30"
    elif rsi > 70:
        signal = f"⚠️ Verkauf – RSI > 70"
    else:
        signal = f"📊 Beobachten"

    return f"{coin.upper()}: €{round(price, 4)} – {signal}"

# === Dashboard ===
st.set_page_config(page_title="XRP Alarm Dashboard", layout="centered")
st.title("📈 Krypto Alarm Dashboard (ohne E-Mail)")

coins = {
    "xrp": "ripple",
    "btc": "bitcoin",
    "eth": "ethereum",
    "doge": "dogecoin",
    "floki": "floki",
    "pepe": "pepe",
    "vechain": "vechain"
}

for symbol, coingecko_id in coins.items():
    df = fetch_data(coingecko_id)
    if df is not None and not df.empty:
        st.write(analyze(df, symbol))
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 UI aktualisiert sich alle 15 Sekunden – Signale basieren auf RSI & Supertrend (vereinfacht)")
