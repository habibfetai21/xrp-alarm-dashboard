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

# === Portfolio-Daten (Menge & CoinGecko-ID) ===
portfolio = {
    "xrp":       {"amount": 1562.17810323, "id": "ripple"},
    "pepe":      {"amount": 67030227.81257255, "id": "pepe"},
    "toshi":     {"amount": 1240005.931827331, "id": None},  # Kein CoinGecko-Eintrag
    "floki":     {"amount": 3963427.93550601, "id": "floki"},
    "vision":    {"amount": 1796.50929707, "id": None},
    "vechain":   {"amount": 3915.56782781, "id": "vechain"},
    "zerebro":   {"amount": 2892.77660435, "id": None},
    "doge":      {"amount": 199.28496554, "id": "dogecoin"},
    "shiba-inu": {"amount": 1615356.17235691, "id": "shiba"},
}

# === Fallback-Preise für Coins ohne CoinGecko-ID ===
fallback_prices = {
    "toshi": 0.000032,
    "vision": 0.085,
    "zerebro": 0.015,
}

# === Kursdaten abrufen ===
@st.cache_data(ttl=900)
def fetch_price(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=eur"
        response = requests.get(url)
        return response.json()[coin_id]["eur"]
    except:
        return None

# === Zeitreihe für Analyse laden ===
@st.cache_data(ttl=900)
def fetch_chart_data(coin_id, days=30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
        r = requests.get(url)
        data = r.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df["price"] = df["price"].astype(float)
        df["rsi"] = df["price"].rolling(window=14).mean()
        df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
        return df
    except:
        return None

# === UI & Analyse ===
st.set_page_config(page_title="Krypto Portfolio Dashboard", layout="centered")
st.title("📊 Erweiterter Krypto Portfolio Monitor")

total_value = 0
signal_count = 0

for coin, data in portfolio.items():
    amount = data["amount"]
    coin_id = data["id"]
    price = fetch_price(coin_id) if coin_id else fallback_prices.get(coin)

    if price:
        value = amount * price
        total_value += value
        st.subheader(f"{coin.upper()} – Analyse")
        st.write(f"Aktuell: **{round(price, 6)} €**")
        st.write(f"Bestand: {round(amount, 4)} ⇒ **{round(value, 2)} €**")

        if coin_id:
            df = fetch_chart_data(coin_id)
            if df is not None:
                latest = df.iloc[-1]
                rsi = latest["rsi"]
                signal = ""

                if rsi < 30:
                    signal = f"🚀 RSI < 30 → **Kaufmöglichkeit**"
                    send_telegram_message(f"Kauf-Signal bei {coin.upper()} – RSI {round(rsi,2)}")
                    signal_count += 1
                elif rsi > 70:
                    signal = f"⚠️ RSI > 70 → **Verkaufssignal**"
                    send_telegram_message(f"Verkauf-Signal bei {coin.upper()} – RSI {round(rsi,2)}")
                    signal_count += 1
                else:
                    signal = f"📊 RSI neutral ({round(rsi, 2)})"

                st.write(signal)

                # Chart anzeigen
                fig, ax = plt.subplots()
                df["price"].plot(ax=ax, label="Preis", color="blue")
                df["supertrend"].plot(ax=ax, label="Supertrend", color="green", linestyle="--")
                ax.set_title(f"{coin.upper()} Preis & Supertrend")
                ax.legend()
                st.pyplot(fig)
            else:
                st.info(f"{coin.upper()}: Keine Chartdaten verfügbar.")
    else:
        st.warning(f"{coin.upper()}: Kursdaten nicht verfügbar.")

st.header("📦 Gesamtwert Portfolio")
st.success(f"💰 Gesamtwert: **€{round(total_value, 2)}**")

if signal_count == 0:
    st.info("🕵️‍♂️ Keine starken RSI-Signale aktuell erkannt.")

st.caption("🔄 Kursdaten via CoinGecko • RSI/Trendindikator • Telegram-Benachrichtigungen bei Signalen")
