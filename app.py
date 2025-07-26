import streamlit as st
import pandas as pd
import requests
import numpy as np
import datetime
import time

# === Telegram Setup ===
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_USER_ID = "7620460833"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        if not r.ok:
            st.error(f"Telegram Fehler: {r.json()}")
    except Exception as e:
        st.error(f"Telegram Fehler: {e}")

# === Technische Analyse Funktionen ===
@st.cache_data(ttl=900)
def fetch_data(symbol, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=eur&days={days}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json().get("prices", [])
    if not data:
        return None
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["price"] = df["price"].astype(float)
    df["rsi"] = df["price"].rolling(window=14).mean()
    df["macd"] = df["price"].ewm(span=12).mean() - df["price"].ewm(span=26).mean()
    df["signal"] = df["macd"].ewm(span=9).mean()
    df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
    df["bb_upper"] = df["price"].rolling(window=20).mean() + 2 * df["price"].rolling(window=20).std()
    df["bb_lower"] = df["price"].rolling(window=20).mean() - 2 * df["price"].rolling(window=20).std()
    df["ma200"] = df["price"].rolling(window=200).mean()
    return df

def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    macd = latest["macd"]
    signal_line = latest["signal"]
    supertrend = latest["supertrend"]

    msg = f"{coin.upper()}: €{round(price, 4)} – "

    if rsi < 30 and price > supertrend and macd > signal_line:
        msg += "🚀 *Starke Kaufchance* (RSI <30, MACD Crossover, über Supertrend)"
        send_telegram_message(msg)
    elif rsi > 70 and price < supertrend and macd < signal_line:
        msg += "⚠️ *Verkaufssignal* (RSI >70, MACD unten, unter Supertrend)"
        send_telegram_message(msg)
    else:
        msg += "📊 Beobachten"

    return msg

# === Dashboard UI ===
st.set_page_config(page_title="📈 Krypto Super Dashboard", layout="centered")
st.title("🚨 Krypto Alarm Dashboard (Telegram aktiviert)")

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
        msg = analyze(df, symbol)
        st.markdown(msg)
        st.line_chart(df["price"], height=200, use_container_width=True)
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 UI aktualisiert sich alle 15 Sekunden. Telegram aktiv. RSI, MACD, Supertrend, Bollinger Bands & MA200 integriert.")

# Auto-Refresh
time.sleep(15)
st.rerun()
