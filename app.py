import streamlit as st
import requests
import pandas as pd
import time
import numpy as np
from datetime import datetime
import pytz

# === Telegram-Konfiguration ===
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_USER_ID = "7620460833"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    requests.post(url, data=payload)

# === Coin-Liste ===
coins = {
    "xrp": "XRP",
    "floki": "FLOKI",
    "pepe": "PEPE",
    "vechain": "VeChain",
    "dogecoin": "DOGE",
    "toshi": "TOSHI",
    "vision-game": "VISION",
    "zebro": "ZEREBRO",
    "shiba-inu": "SHIBA INU"
}

# === RSI-Funktion ===
def compute_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# === Supertrend-Vereinfachung ===
def supertrend_signal(prices, period=10, multiplier=3):
    atr = prices.rolling(period).std()
    hl2 = prices
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr
    close = prices.iloc[-1]
    prev_upper = upperband.iloc[-2]
    prev_lower = lowerband.iloc[-2]
    if close > prev_upper:
        return "Buy"
    elif close < prev_lower:
        return "Sell"
    else:
        return "Neutral"

# === Streamlit UI ===
st.set_page_config(layout="wide", page_title="Krypto RSI Dashboard")
st.title("📈 Krypto RSI & Supertrend Dashboard (Live)")
st.caption("Automatische RSI-Analyse mit Telegram-Alarm – Stand: " + datetime.now(pytz.timezone("Europe/Berlin")).strftime("%H:%M:%S"))

# === Main Loop ===
for coin_id, coin_name in coins.items():
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days=1&interval=hourly"
        response = requests.get(url).json()
        prices = [p[1] for p in response["prices"]]
        timestamps = [datetime.fromtimestamp(p[0]/1000) for p in response["prices"]]
        df = pd.DataFrame({"Time": timestamps, "Price": prices}).set_index("Time")

        rsi = compute_rsi(df["Price"])
        current_rsi = round(rsi.iloc[-1], 2)
        supertrend = supertrend_signal(df["Price"])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(coin_name)
            st.metric("Aktueller Preis (€)", round(df["Price"].iloc[-1], 4))
        with col2:
            st.metric("RSI (1d)", current_rsi)
        with col3:
            st.metric("Supertrend", supertrend)

        st.line_chart(df["Price"], height=200)

        # === Telegram-Alarm senden bei RSI-Signal ===
        if current_rsi < 30:
            send_telegram_message(f"📉 RSI-Alarm ({coin_name}): RSI = {current_rsi} → ÜBERVERKAUFT 🔻")
        elif current_rsi > 70:
            send_telegram_message(f"📈 RSI-Alarm ({coin_name}): RSI = {current_rsi} → ÜBERKAUFT 🔺")

        st.divider()

    except Exception as e:
        st.error(f"Fehler bei {coin_name}: {e}")

st.info("🔁 Automatische Aktualisierung alle 5–10 Sekunden mit Live-Daten von CoinGecko")