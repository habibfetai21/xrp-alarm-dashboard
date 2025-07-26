import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import time

# Telegram-Konfiguration
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_USER_ID = "7620460833"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Telegram-Fehler: {e}")

# Coin-Liste mit CoinGecko-IDs
coins = {
    "xrp": "ripple",
    "pepe": "pepe",
    "toshi": "toshi",           # Falls CoinGecko-ID anders: später ergänzen
    "floki": "floki",
    "vision": "vision",         # manuell ergänzen falls nötig
    "vechain": "vechain",
    "zerebro": "zerebro",       # manuell ergänzen
    "doge": "dogecoin",
    "shiba": "shiba-inu"
}

# Portfolio-Bestand
portfolio = {
    "xrp": 1562.17810323,
    "pepe": 67030227.81257255,
    "toshi": 1240005.931827331,
    "floki": 3963427.93550601,
    "vision": 1796.50929707,
    "vechain": 3915.56782781,
    "zerebro": 2892.77660435,
    "doge": 199.28496554,
    "shiba": 1615356.17235691
}

# === RSI-Berechnung ===
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# === CoinGecko-Abruf ===
@st.cache_data(ttl=60)
def fetch_coin_data(coin_id, days=30, interval='hourly'):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "eur",
        "days": days,
        "interval": interval
    }
    try:
        r = requests.get(url, params=params)
        data = r.json()
        prices = pd.DataFrame(data['prices'], columns=["timestamp", "price"])
        prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
        prices.set_index("timestamp", inplace=True)
        return prices, data.get('market_caps', [])
    except:
        return None, None

# === App Layout ===
st.set_page_config(layout="wide")
st.title("🚀 Krypto Performance Dashboard (Live)")

for symbol, coingecko_id in coins.items():
    st.subheader(f"{symbol.upper()} – Analyse")

    prices_df, market_caps = fetch_coin_data(coingecko_id)

    if prices_df is not None and not prices_df.empty:
        current_price = prices_df["price"].iloc[-1]
        bestand = portfolio.get(symbol, 0)
        wert = current_price * bestand

        # RSI-Werte für verschiedene Zeiträume
        rsi_14 = calculate_rsi(prices_df["price"], 14)
        rsi_7 = calculate_rsi(prices_df["price"], 7)
        rsi_3 = calculate_rsi(prices_df["price"], 3)

        st.markdown(f"""
        - 📈 **Kurs aktuell:** €{current_price:.6f}
        - 📦 **Bestand:** {bestand:.4f}
        - 💰 **Wert:** €{wert:.2f}
        - 📊 **RSI 14 Tage:** {rsi_14.dropna().iloc[-1]:.2f}
        - 📊 **RSI 7 Tage:** {rsi_7.dropna().iloc[-1]:.2f}
        - 📊 **RSI 3 Tage:** {rsi_3.dropna().iloc[-1]:.2f}
        """)

        if rsi_14.dropna().iloc[-1] < 30:
            st.success("✅ RSI < 30: Guter Kaufzeitpunkt!")
            send_telegram_message(f"Kaufsignal {symbol.upper()} – RSI: {rsi_14.iloc[-1]:.2f}")
        elif rsi_14.dropna().iloc[-1] > 70:
            st.warning("⚠️ RSI > 70: Überkauft – Verkaufssignal!")
            send_telegram_message(f"Verkaufssignal {symbol.upper()} – RSI: {rsi_14.iloc[-1]:.2f}")

        # Chart anzeigen
        st.line_chart(prices_df["price"])

        # MarketCap
        if market_caps:
            last_cap = market_caps[-1][1]
            st.info(f"📦 Marktkapitalisierung: €{last_cap:,.0f}")
    else:
        st.warning(f"{symbol.upper()}: ❌ Kursdaten nicht verfügbar (CoinGecko)")

# Automatische Aktualisierung
st.caption("🔄 Automatische Aktualisierung alle 5 Sekunden")
st.experimental_rerun()
time.sleep(5)
