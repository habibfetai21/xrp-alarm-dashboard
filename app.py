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

# === Fallback-Preise (wenn CoinGecko nichts liefert) ===
fallback_prices = {
    "vision": 0.085,
    "zerebro": 0.015,
    "toshi": 0.000032
}

# === Deine Bestände ===
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

# === CoinGecko IDs ===
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

# === Datenabruf von CoinGecko ===
@st.cache_data(ttl=900)
def fetch_data(symbol, days=30):
    if coingecko_ids[symbol] is None:
        return None
    url = f"https://api.coingecko.com/api/v3/coins/{coingecko_ids[symbol]}/market_chart?vs_currency=eur&days={days}"
    try:
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
    except:
        return None

# === Analysefunktion ===
def analyze(df, coin, amount):
    if df is not None and not df.empty:
        latest = df.iloc[-1]
        price = latest["price"]
    else:
        price = fallback_prices.get(coin)
        if price is None:
            return f"{coin.upper()}: Kursdaten nicht verfügbar.", 0, None

    value = price * amount
    rsi = df["rsi"].iloc[-1] if df is not None else None

    if rsi:
        if rsi < 30:
            signal = f"🚀 **Kaufempfehlung** (RSI: {round(rsi, 2)})"
            send_telegram_message(f"{coin.upper()} RSI < 30 – Kauf!")
        elif rsi > 70:
            signal = f"⚠️ **Verkaufssignal** (RSI: {round(rsi, 2)})"
            send_telegram_message(f"{coin.upper()} RSI > 70 – Verkauf!")
        else:
            signal = f"📊 Beobachten (RSI: {round(rsi, 2)})"
    else:
        signal = "📊 Keine RSI-Daten verfügbar"

    result = f"""
### {coin.upper()} – Analyse

Aktuell: {round(price, 6)} €
📦 Bestand: {round(amount, 4)} ⇒ €{round(value, 2)}
{signal}
"""
    return result, price, df

# === Streamlit UI ===
st.set_page_config(page_title="Krypto Portfolio Dashboard", layout="centered")
st.title("📊 Krypto-Portfolio Dashboard (mit Telegram)")

total_value = 0
for coin, amount in portfolio.items():
    df = fetch_data(coin)
    output, price, df_result = analyze(df, coin, amount)
    st.markdown(output)
    if df_result is not None:
        fig, ax = plt.subplots()
        df_result["price"].plot(ax=ax, label="Preis", color="blue")
        df_result["supertrend"].plot(ax=ax, label="Supertrend", linestyle="--", color="green")
        ax.set_title(f"{coin.upper()} Preis & Supertrend")
        ax.legend()
        st.pyplot(fig)
    if price:
        total_value += price * amount

st.success(f"💰 **Gesamtwert Portfolio:** €{round(total_value, 2)}")
st.caption("🔄 Automatische Updates alle 15 Minuten • RSI & Supertrend aus CoinGecko-Daten • Telegram-Warnung bei starken Signalen")
