import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt

# === Telegram-Konfiguration ===
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_USER_ID = "7620460833"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            st.error(f"Telegram Fehler: {response.json()}")
    except Exception as e:
        st.error(f"Telegram Nachricht konnte nicht gesendet werden: {e}")

# === Datenabruf von CoinGecko ===
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
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["rsi"] = df["price"].rolling(window=14).mean()
    df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
    return df

# === Analysefunktion ===
def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    trend = latest["supertrend"]

    signal = ""
    if rsi < 30:
        signal = f"🚀 {coin.upper()}: €{round(price, 4)} – **Kaufempfehlung** (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    elif rsi > 70:
        signal = f"⚠️ {coin.upper()}: €{round(price, 4)} – Verkaufssignal (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    else:
        signal = f"📊 {coin.upper()}: €{round(price, 4)} – Beobachten (RSI: {round(rsi, 2)})"
    return signal

# === Social-Media-Stimmung (vereinfachte Simulation) ===
def fetch_sentiment(coin):
    trends = {
        "xrp": "Bullish 📈",
        "btc": "Neutral 😐",
        "eth": "Bearish 📉",
        "doge": "Neutral",
        "floki": "Bullish",
        "pepe": "Bearish",
        "vechain": "Neutral"
    }
    return trends.get(coin, "Unbekannt")

# === Streamlit UI ===
st.set_page_config(page_title="Krypto Alarm Dashboard", layout="centered")
st.title("📈 Krypto Alarm Dashboard mit Telegram")

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
        st.subheader(f"{symbol.upper()} – Marktanalyse")
        st.write(analyze(df, symbol))

        # Chart anzeigen
        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["supertrend"].plot(ax=ax, label="Supertrend", linestyle="--", color="green")
        ax.set_title(f"{symbol.upper()} Preis & Supertrend")
        ax.legend()
        st.pyplot(fig)

        # Social-Media-Stimmung anzeigen
        sentiment = fetch_sentiment(symbol)
        st.info(f"📣 Social-Media-Trend: {sentiment}")
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 Aktualisierung alle 15 Minuten • RSI & Supertrend basierend auf CoinGecko • Telegram-Benachrichtigung bei starken Signalen")
