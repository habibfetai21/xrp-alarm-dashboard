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

# === Coins + Portfolio-Bestand ===
portfolio = {
    "xrp": 1562.17810323,
    "pepe": 67030227.81257255,
    "toshi": 1240005.931827331,
    "floki": 3963427.93550601,
    "vision": 1796.50929707,
    "vechain": 3915.56782781,
    "zerebro": 2892.77660435,
    "doge": 199.28496554,
    "shiba-inu": 1615356.17235691
}

coingecko_ids = {
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

# Manueller Fallback für Coins ohne CoinGecko-Daten
fallback_prices = {
    "toshi": 0.000032,
    "vision": 0.085,
    "zerebro": 0.015
}

@st.cache_data(ttl=900)
def fetch_data(symbol):
    if symbol not in coingecko_ids or coingecko_ids[symbol] is None:
        return None
    url = f"https://api.coingecko.com/api/v3/coins/{coingecko_ids[symbol]}/market_chart?vs_currency=eur&days=30"
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

def analyze(df, symbol):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    signal = ""
    if rsi < 30:
        signal = f"🚀 {symbol.upper()}: €{round(price, 6)} – **Kaufempfehlung** (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    elif rsi > 70:
        signal = f"⚠️ {symbol.upper()}: €{round(price, 6)} – Verkaufssignal (RSI: {round(rsi, 2)})"
        send_telegram_message(signal)
    else:
        signal = f"📊 {symbol.upper()}: €{round(price, 6)} – Beobachten (RSI: {round(rsi, 2)})"
    return signal, price

# === Streamlit UI ===
st.set_page_config(page_title="Krypto Portfolio Dashboard", layout="centered")
st.title("📈 Erweiterter Krypto-Portfolio Monitor")

total_value = 0.0

for symbol, amount in portfolio.items():
    st.subheader(f"{symbol.upper()} – Analyse")

    df = fetch_data(symbol)
    if df is not None and not df.empty:
        signal, price = analyze(df, symbol)
        value = amount * price
        total_value += value

        st.write(signal)
        st.write(f"📦 Bestand: {round(amount, 4)} ⇒ €{round(value, 2)}")

        # Plot
        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["supertrend"].plot(ax=ax, label="Supertrend", linestyle="--", color="green")
        ax.set_title(f"{symbol.upper()} Preisverlauf")
        ax.legend()
        st.pyplot(fig)
    else:
        # Fallback für Coins ohne API
        price = fallback_prices.get(symbol)
        if price:
            value = amount * price
            total_value += value
            st.info(f"Aktuell: {price} €\n\n📦 Bestand: {round(amount, 4)} ⇒ €{round(value, 2)}")
        else:
            st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar.")

st.success(f"💰 Gesamtwert Portfolio: €{round(total_value, 2)}")
st.caption("🔄 Live-Daten über CoinGecko (teilweise Fallback für unbekannte Coins). Telegram-Warnungen bei RSI-Signalen.")
