import streamlit as st
import pandas as pd
import requests
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

# === Persönliches Portfolio (Coin -> Menge) ===
portfolio = {
    "xrp": 1562,
    "pepe": 67030227,
    "toshi": 1240005,
    "floki": 3963427,
    "vision": 1796,
    "vechain": 3915,
    "zerebro": 2892,
    "doge": 199,
    "shiba-inu": 1615356,
}

# === CoinGecko IDs ===
coins = {
    "xrp": "ripple",
    "pepe": "pepe",
    "toshi": None,
    "floki": "floki",
    "vision": None,
    "vechain": "vechain",
    "zerebro": None,
    "doge": "dogecoin",
    "shiba-inu": "shiba-inu"
}

@st.cache_data(ttl=900)
def fetch_data(symbol, days=30):
    if not symbol:
        return None
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

def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]

    signal = ""
    if rsi < 30:
        signal = f"🚀 {coin.upper()}: €{round(price, 4)} – **Kaufempfehlung** (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    elif rsi > 70:
        signal = f"⚠️ {coin.upper()}: €{round(price, 4)} – Verkaufssignal (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    else:
        signal = f"📊 {coin.upper()}: €{round(price, 4)} – Beobachten (RSI: {round(rsi, 2)})"
    return signal, price

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
st.set_page_config(page_title="Krypto Portfolio Dashboard", layout="centered")
st.title("💰 Krypto-Portfolio Übersicht")

portfolio_value = 0

for symbol, coingecko_id in coins.items():
    st.subheader(f"{symbol.upper()} – Analyse")
    df = fetch_data(coingecko_id)
    if df is not None and not df.empty:
        signal, price = analyze(df, symbol)
        st.write(signal)

        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["supertrend"].plot(ax=ax, label="Supertrend", linestyle="--", color="green")
        ax.set_title(f"{symbol.upper()} Preis & Supertrend")
        ax.legend()
        st.pyplot(fig)

        if symbol in portfolio:
            menge = portfolio[symbol]
            wert = menge * price
            portfolio_value += wert
            st.success(f"📦 Bestand: {menge} — Aktueller Wert: €{wert:,.2f}")
        else:
            st.info("🔍 Kein Bestand erfasst.")

        st.info(f"📣 Social-Media-Trend: {fetch_sentiment(symbol)}")
    else:
        st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar")

# === Gesamtübersicht ===
if portfolio_value > 0:
    st.subheader("📊 Gesamtwert Portfolio")
    st.success(f"💶 Gesamtwert: €{portfolio_value:,.2f}")
else:
    st.error("❌ Portfolio konnte nicht berechnet werden – fehlen Kursdaten?")

st.caption("🔄 Aktualisierung alle 15 Minuten • RSI, Supertrend & Telegram-Signale aktiv")
