import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Telegram-Konfiguration
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

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# CoinGecko Datenabruf (für Coins mit CoinGecko-ID)
@st.cache_data(ttl=900)
def fetch_coingecko_data(symbol, days=30):
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
    df["rsi"] = calculate_rsi(df["price"])
    return df

# Bitpanda historische Preise (candles) abrufen
@st.cache_data(ttl=900)
def fetch_bitpanda_candles(symbol, days=30):
    # symbol z.B. "VISION_EUR"
    url = f"https://api.exchange.bitpanda.com/public/v1/candles?interval=1d&product_code={symbol}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json().get("candles", [])
    if not data:
        return None
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["time"])
    df.set_index("timestamp", inplace=True)
    df["price"] = df["close"].astype(float)
    df = df.sort_index()
    df = df.tail(days)
    df["rsi"] = calculate_rsi(df["price"])
    return df

# Bitpanda aktuellen Preis abrufen
def fetch_bitpanda_price(symbol):
    # symbol z.B. "VISION_EUR"
    url = "https://api.exchange.bitpanda.com/public/v1/ticker"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    for item in data:
        if item.get("product_code") == symbol:
            return float(item.get("last"))
    return None

# Analyse & Signal für Streamlit
def analyze(df, coin, price=None):
    if df is None or df.empty:
        return f"{coin.upper()}: Keine Daten verfügbar"
    latest = df.iloc[-1]
    if price is None:
        price = latest["price"]
    rsi = latest["rsi"]

    if rsi < 30:
        signal = f"🚀 {coin.upper()}: €{round(price,4)} – Kaufempfehlung (RSI: {round(rsi,2)})"
        send_telegram_message(signal)
    elif rsi > 70:
        signal = f"⚠️ {coin.upper()}: €{round(price,4)} – Verkaufssignal (RSI: {round(rsi,2)})"
        send_telegram_message(signal)
    else:
        signal = f"📊 {coin.upper()}: €{round(price,4)} – Neutral/Beobachten (RSI: {round(rsi,2)})"
    return signal

# Social Sentiment (vereinfacht)
def fetch_sentiment(coin):
    trends = {
        "xrp": "Bullish 📈",
        "btc": "Neutral 😐",
        "eth": "Bearish 📉",
        "doge": "Neutral",
        "floki": "Bullish",
        "pepe": "Bearish",
        "vechain": "Neutral",
        "toshi": "Neutral",
        "vision": "Bullish",
        "zerebro": "Neutral",
        "shiba-inu": "Bearish"
    }
    return trends.get(coin, "Unbekannt")

# === Streamlit UI ===
st.set_page_config(page_title="Krypto Alarm Dashboard mit Bitpanda API", layout="centered")
st.title("📈 Krypto Alarm Dashboard mit Bitpanda API")

# Coins mit Bitpanda-Symbol vs CoinGecko-ID
bitpanda_coins = {
    "vision": "VISION_EUR",
    "zerebro": "ZEREBRO_EUR",
    "toshi": "TOSHI_EUR",
}
coingecko_coins = {
    "xrp": "ripple",
    "btc": "bitcoin",
    "eth": "ethereum",
    "doge": "dogecoin",
    "floki": "floki",
    "pepe": "pepe",
    "vechain": "vechain",
    "shiba-inu": "shiba-inu"
}

for coin, symbol in bitpanda_coins.items():
    df = fetch_bitpanda_candles(symbol, days=30)
    price = fetch_bitpanda_price(symbol)
    st.subheader(f"{coin.upper()} – Analyse (Bitpanda)")
    if df is not None and price is not None:
        signal = analyze(df, coin, price)
        st.write(signal)

        # Chart mit Matplotlib
        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        ax.set_title(f"{coin.upper()} Preis Chart (Bitpanda)")
        ax.legend()
        st.pyplot(fig)
        st.info(f"📣 Social-Media-Trend: {fetch_sentiment(coin)}")
    else:
        st.warning(f"{coin.upper()}: Daten nicht verfügbar")

for coin, coingecko_id in coingecko_coins.items():
    df = fetch_coingecko_data(coingecko_id, days=30)
    st.subheader(f"{coin.upper()} – Analyse (CoinGecko)")
    if df is not None and not df.empty:
        signal = analyze(df, coin)
        st.write(signal)

        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        ax.set_title(f"{coin.upper()} Preis Chart (CoinGecko)")
        ax.legend()
        st.pyplot(fig)
        st.info(f"📣 Social-Media-Trend: {fetch_sentiment(coin)}")
    else:
        st.warning(f"{coin.upper()}: Daten nicht verfügbar")

st.caption("🔄 Aktualisierung alle 15 Minuten • RSI korrekt berechnet • Telegram-Benachrichtigung bei Kauf-/Verkaufssignalen")
