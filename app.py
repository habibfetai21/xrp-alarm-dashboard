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

# === Technische Analyse Daten laden ===
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
    df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
    return df

# === Analysefunktion mit Empfehlung ===
def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    trend = latest["supertrend"]

    signal = ""
    if rsi < 30:
        signal = f"🚀 {coin.upper()} ist **stark überverkauft** → *Kaufgelegenheit* (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    elif rsi > 70:
        signal = f"⚠️ {coin.upper()} ist **überkauft** → *Verkaufssignal* (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    elif price > trend:
        signal = f"📈 {coin.upper()} im **Aufwärtstrend** – Beobachte für möglichen Einstieg (RSI: {round(rsi, 2)})"
    elif price < trend:
        signal = f"📉 {coin.upper()} im **Abwärtstrend** – Kein Einstieg empfohlen (RSI: {round(rsi, 2)})"
    else:
        signal = f"🔎 {coin.upper()} neutral – Warte auf klaren Impuls (RSI: {round(rsi, 2)})"
    return signal

# === Social-Media-Stimmung (simuliert) ===
def fetch_sentiment(coin):
    trends = {
        "xrp": "Bullish 📈",
        "btc": "Neutral 😐",
        "eth": "Bearish 📉",
        "doge": "Neutral",
        "floki": "Bullish",
        "pepe": "Bearish",
        "vechain": "Neutral",
        "vision": "Trend schwach",
        "zerebro": "Keine Daten",
        "toshi": "Kleiner Hype",
        "shiba-inu": "Neutral"
    }
    return trends.get(coin, "Keine Daten")

# === Streamlit App ===
st.set_page_config(page_title="Krypto Analyse Dashboard", layout="centered")
st.title("📊 Krypto Analyse Dashboard (Kauf-/Verkaufssignale)")

coins = {
    "xrp": "ripple",
    "btc": "bitcoin",
    "eth": "ethereum",
    "doge": "dogecoin",
    "floki": "floki",
    "pepe": "pepe",
    "vechain": "vechain",
    "toshi": "toshi",
    "vision": "vision",
    "zerebro": "zerebro",
    "shiba-inu": "shiba-inu"
}

for symbol, coingecko_id in coins.items():
    df = fetch_data(coingecko_id)
    st.subheader(f"{symbol.upper()} – Analyse")
    if df is not None and not df.empty:
        st.write(analyze(df, symbol))

        # Chart anzeigen
        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["supertrend"].plot(ax=ax, label="Supertrend", linestyle="--", color="green")
        ax.set_title(f"{symbol.upper()} – Preis vs Supertrend")
        ax.legend()
        st.pyplot(fig)

        # Stimmung
        sentiment = fetch_sentiment(symbol)
        st.info(f"📣 Social Media Trend: {sentiment}")
    else:
        st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar.")

st.caption("⏱️ Automatische Analyse alle 15 Minuten • RSI & Supertrend • Telegram-Warnung bei Signal")
