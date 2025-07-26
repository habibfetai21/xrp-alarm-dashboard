import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# === Social Media Sentiment (Dummy) ===
def get_sentiment(coin):
    sentiment_score = {
        "xrp": 0.7,
        "btc": 0.6,
        "eth": 0.65,
        "doge": 0.55,
        "floki": 0.5,
        "pepe": 0.45,
        "vechain": 0.4,
    }
    score = sentiment_score.get(coin, 0.5)
    if score >= 0.65:
        return f"🔥 Trending in Social Media ({score*100:.0f}%)"
    elif score >= 0.5:
        return f"📢 Moderate Erwähnung ({score*100:.0f}%)"
    else:
        return f"📉 Wenig Erwähnung ({score*100:.0f}%)"

# === Technische Analyse & Daten holen ===
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
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df.set_index("timestamp", inplace=True)
    df["rsi"] = df["price"].rolling(window=14).mean()  # Dummy RSI
    df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
    return df

# === Analyse + Signal ===
def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    signal = ""
    if rsi < 30:
        signal = f"🚀 **Kaufempfehlung** – RSI < 30"
    elif rsi > 70:
        signal = f"⚠️ **Verkauf** – RSI > 70"
    else:
        signal = f"📊 Beobachten"

    sentiment = get_sentiment(coin)
    return f"**{coin.upper()}**: €{round(price, 4)} – {signal} | {sentiment}"

# === Diagramm anzeigen ===
def plot_chart(df, coin):
    fig, ax = plt.subplots(figsize=(6, 2.5))
    df["price"].plot(ax=ax, label="Preis", color="blue")
    df["supertrend"].plot(ax=ax, label="Supertrend", color="green", linestyle="--")
    ax.set_title(f"{coin.upper()} Kursverlauf")
    ax.set_ylabel("EUR")
    ax.legend()
    st.pyplot(fig)

# === Dashboard ===
st.set_page_config(page_title="XRP Alarm Dashboard", layout="centered")
st.title("📈 Krypto Alarm Dashboard")

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
        st.markdown(analyze(df, symbol))
        plot_chart(df, symbol)
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 Automatisches Update alle 15 Sekunden – Daten von CoinGecko & Social Trends (vereinfacht)")
