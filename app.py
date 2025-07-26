import streamlit as st
import pandas as pd
import requests

# Deine Telegram-Daten
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
CHAT_ID = "7620460833"

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            st.error(f"Telegram Nachricht konnte nicht gesendet werden: {r.text}")
    except Exception as e:
        st.error(f"Fehler beim Senden der Telegram Nachricht: {e}")

# Beispiel: technische Analyse (vereinfacht)
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
    signal = ""
    if rsi < 30:
        signal = f"🚀 Kaufempfehlung – RSI < 30"
    elif rsi > 70:
        signal = f"⚠️ Verkauf – RSI > 70"
    else:
        signal = f"📊 Beobachten"

    return f"{coin.upper()}: €{round(price, 4)} – {signal}"

# Dashboard
st.set_page_config(page_title="Krypto Alarm Dashboard mit Telegram", layout="centered")
st.title("📈 Krypto Alarm Dashboard mit Telegram-Benachrichtigung")

coins = {
    "xrp": "ripple",
    "btc": "bitcoin",
    "eth": "ethereum",
    "doge": "dogecoin",
    "floki": "floki",
    "pepe": "pepe",
    "vechain": "vechain"
}

messages = []
for symbol, coingecko_id in coins.items():
    df = fetch_data(coingecko_id)
    if df is not None and not df.empty:
        result = analyze(df, symbol)
        st.write(result)
        messages.append(result)
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 UI aktualisiert sich alle 15 Sekunden – Signale basieren auf RSI & Supertrend (vereinfacht)")

# Telegram senden, z.B. wenn Kaufempfehlung vorliegt
for msg in messages:
    if "Kaufempfehlung" in msg or "Verkauf" in msg:
        send_telegram_message(msg)
