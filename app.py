import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

# --- Telegram Setup ---
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_USER_ID = "7620460833"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            st.error(f"Telegram Fehler: {r.json()}")
    except Exception as e:
        st.error(f"Telegram Nachricht konnte nicht gesendet werden: {e}")

# --- Portfolio & Coin IDs (CoinGecko) ---
portfolio = {
    "xrp": 1562.17810323,
    "pepe": 67030227.81257255,
    "toshi": 1240005.931827331,
    "floki": 3963427.93550601,
    "vision": 1796.50929707,
    "vechain": 3915.56782781,
    "zerebro": 2892.77660435,
    "doge": 199.28496554,
    "shiba-inu": 1615356.17235691,
}

cg_ids = {
    "xrp": "ripple",
    "pepe": "pepe",
    "toshi": None,
    "floki": "floki",
    "vision": None,
    "vechain": "vechain",
    "zerebro": None,
    "doge": "dogecoin",
    "shiba-inu": "shiba-inu",
}

# --- Fallbackpreise für Coins ohne CoinGecko-ID ---
fallback_prices = {
    "vision": 0.147,    # Beispielpreis in Euro
    "toshi": 0.000032,
    "zerebro": 0.027,
}

# --- Holen der aktuellen Preise (CoinGecko API oder Fallback) ---
@st.cache_data(ttl=900)
def fetch_price(symbol):
    cg = cg_ids.get(symbol)
    if cg:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg}&vs_currencies=eur"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return data.get(cg, {}).get("eur")
    # fallback:
    return fallback_prices.get(symbol)

# --- Holen der historischen Preisdaten für Chart + RSI ---
@st.cache_data(ttl=900)
def fetch_historical_data(symbol, days=30):
    cg = cg_ids.get(symbol)
    if not cg:
        return None
    url = f"https://api.coingecko.com/api/v3/coins/{cg}/market_chart?vs_currency=eur&days={days}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    prices = r.json().get("prices", [])
    if not prices:
        return None
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["price"] = df["price"].astype(float)
    return df

# --- RSI Berechnung (14 Tage) ---
def compute_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- Einfacher Supertrend (hier als Mittelwert + std Abweichung) ---
def compute_supertrend(df):
    ma = df["price"].rolling(window=7).mean()
    std = df["price"].rolling(window=7).std()
    supertrend = ma - std
    return supertrend

# --- Social Media Sentiment (vereinfachte Simulation) ---
def fetch_sentiment(symbol):
    trends = {
        "xrp": "Bullish 📈",
        "btc": "Neutral 😐",
        "eth": "Bearish 📉",
        "doge": "Neutral",
        "floki": "Bullish",
        "pepe": "Bearish",
        "vechain": "Neutral",
        "toshi": "Unbekannt",
        "vision": "Unbekannt",
        "zerebro": "Unbekannt",
        "shiba-inu": "Neutral"
    }
    return trends.get(symbol, "Unbekannt")

# --- Streamlit App ---
st.set_page_config(page_title="Erweitertes Krypto-Portfolio Dashboard", layout="wide")
st.title("📈 Erweitertes Krypto-Portfolio Dashboard mit Telegram")

total_value = 0

for symbol, amount in portfolio.items():
    price = fetch_price(symbol)
    if price is None:
        st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar.")
        continue

    value = amount * price
    total_value += value

    st.subheader(f"{symbol.upper()} – Portfolio Analyse")
    st.write(f"Bestand: {amount:,.4f} Stück")
    st.write(f"Aktueller Kurs: €{price:.6f}")
    st.write(f"Wert: **€{value:,.2f}**")

    # Chart und technische Indikatoren nur wenn CoinGecko-Daten vorhanden
    df = fetch_historical_data(symbol)
    if df is not None and not df.empty:
        df["rsi"] = compute_rsi(df["price"])
        df["supertrend"] = compute_supertrend(df)

        latest = df.iloc[-1]
        rsi_val = latest["rsi"]

        # Signal aus RSI generieren und Telegram senden
        if rsi_val < 30:
            signal = f"🚀 {symbol.upper()}: Kaufempfehlung! Kurs €{price:.6f} (RSI: {rsi_val:.1f})"
            send_telegram_message(signal)
            st.success(signal)
        elif rsi_val > 70:
            signal = f"⚠️ {symbol.upper()}: Verkaufssignal! Kurs €{price:.6f} (RSI: {rsi_val:.1f})"
            send_telegram_message(signal)
            st.warning(signal)
        else:
            st.info(f"{symbol.upper()} RSI: {rsi_val:.1f} (kein Signal)")

        # Plot
        fig, ax = plt.subplots(figsize=(10,4))
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["supertrend"].plot(ax=ax, label="Supertrend", color="green", linestyle="--")
        ax.set_title(f"{symbol.upper()} Preis & Supertrend")
        ax.set_ylabel("Preis in €")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info(f"{symbol.upper()}: Historische Daten für Chart nicht verfügbar.")

    # Social Media Sentiment
    sentiment = fetch_sentiment(symbol)
    st.info(f"📣 Social Media Stimmung: {sentiment}")

st.markdown("---")
st.subheader("📊 Gesamtwert Portfolio")
st.success(f"💶 **€{total_value:,.2f}**")
st.caption("🔄 Aktualisierung alle 15 Minuten • Telegram benachrichtigt bei RSI <30 (Kaufen) oder >70 (Verkaufen)")
