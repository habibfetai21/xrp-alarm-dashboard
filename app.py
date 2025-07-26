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

# === Persönliches Portfolio (Coin -> [Menge, Einkaufspreis]) ===
portfolio = {
    "xrp": [1562, 17810.32],
    "pepe": [67030227, 81257.26],
    "toshi": [1240005, 931827.33],
    "floki": [3963427, 93550.60],
    "vision": [1796, 50929.71],
    "vechain": [3915, 56782.78],
    "zerebro": [2892, 77660.44],
    "doge": [199, 2849.66],
    "shiba-inu": [1615356, 17235.69],
}

# === CoinGecko IDs für Abruf
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

# === Datenabruf von CoinGecko ===
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
    return signal, price

# === Social-Media-Stimmung (Dummy-Daten) ===
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
st.title("💰 Erweitertes Krypto-Portfolio Dashboard")

portfolio_value = 0
portfolio_cost = 0

for symbol, coingecko_id in coins.items():
    st.subheader(f"{symbol.upper()} – Analyse & Portfolio")
    df = fetch_data(coingecko_id)
    if df is not None and not df.empty:
        signal, price = analyze(df, symbol)
        st.write(signal)

        # Chart anzeigen
        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["supertrend"].plot(ax=ax, label="Supertrend", linestyle="--", color="green")
        ax.set_title(f"{symbol.upper()} Preis & Supertrend")
        ax.legend()
        st.pyplot(fig)

        # Portfolio-Berechnung
        if symbol in portfolio:
            menge, einkauf = portfolio[symbol]
            wert = menge * price
            gewinn = wert - einkauf
            portfolio_value += wert
            portfolio_cost += einkauf
            st.success(f"📦 Bestand: {menge} — Aktueller Wert: €{wert:,.2f} — Gekauft für: €{einkauf:,.2f} — Gewinn/Verlust: €{gewinn:,.2f}")
        else:
            st.info("🔍 Kein Bestand erfasst.")

        # Social Media Trend
        st.info(f"📣 Social-Media-Trend: {fetch_sentiment(symbol)}")
    else:
        st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar")

# === Gesamtübersicht ===
if portfolio_value > 0:
    gesamtgewinn = portfolio_value - portfolio_cost
    prozent = (gesamtgewinn / portfolio_cost) * 100
    st.subheader("📊 Gesamtwert Portfolio")
    st.success(f"💶 Gesamtwert: €{portfolio_value:,.2f}")
    st.info(f"📉 Gesamt Gewinn/Verlust: €{gesamtgewinn:,.2f} ({prozent:.2f}%)")
else:
    st.error("❌ Portfolio konnte nicht berechnet werden – fehlen Kurse?")

st.caption("🔄 Alle Daten aktualisieren sich alle 15 Minuten – basierend auf CoinGecko")
