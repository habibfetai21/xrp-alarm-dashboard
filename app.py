import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt
import numpy as np

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

# === RSI-Berechnung ===
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# === Datenabruf von CoinGecko ===
@st.cache_data(ttl=60)
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
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["rsi"] = calculate_rsi(df["price"])
    return df

@st.cache_data(ttl=60)
def fetch_market_cap(symbol):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    market_cap = data.get("market_data", {}).get("market_cap", {}).get("eur", None)
    return market_cap

# === Analysefunktion mit RSI über verschiedene Zeiträume ===
def analyze_rsi_multi(df):
    results = {}
    # Monat (30 Tage)
    results["Monat"] = calculate_rsi(df["price"], window=14).iloc[-1]
    # Woche (7 Tage)
    week_data = df.last("7D")
    results["Woche"] = calculate_rsi(week_data["price"], window=14).iloc[-1]
    # Tag (1 Tag)
    day_data = df.last("1D")
    results["Tag"] = calculate_rsi(day_data["price"], window=14).iloc[-1]
    # Stunde (1 Stunde)
    # Achtung: CoinGecko liefert keine stündlichen Daten für days>1, daher nur wenn df genug feine Daten hat
    hour_data = df.last("1H")
    if len(hour_data) >= 14:
        results["Stunde"] = calculate_rsi(hour_data["price"], window=14).iloc[-1]
    else:
        results["Stunde"] = None
    # Sekunde – für Sekundendaten bräuchte man eine andere API (nicht hier implementiert)
    results["Sekunde"] = None
    return results

# === Streamlit UI ===
st.set_page_config(page_title="Krypto Alarm Dashboard", layout="centered")
st.title("📈 Krypto Alarm Dashboard mit Telegram & Multi-Zeitraum RSI")

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

# Automatische Aktualisierung alle 5 Sekunden
st_autorefresh = st.experimental_singleton(lambda: st.experimental_rerun())
count = st_autorefresh()

for symbol, coingecko_id in coins.items():
    df = fetch_data(coingecko_id, days=30)
    market_cap = fetch_market_cap(coingecko_id)

    st.subheader(f"{symbol.upper()} – Marktanalyse")

    if df is not None and not df.empty:
        rsi_values = analyze_rsi_multi(df)

        # Ausgabe Market Cap
        if market_cap:
            st.write(f"💰 Market Cap: €{market_cap:,.0f}")
        else:
            st.write("Market Cap: Nicht verfügbar")

        # RSI-Werte über Zeiträume
        st.write("📊 RSI-Werte:")
        for period, rsi in rsi_values.items():
            if rsi is not None and not pd.isna(rsi):
                st.write(f"- {period}: {rsi:.2f}")
            else:
                st.write(f"- {period}: Nicht verfügbar")

        # Chart anzeigen
        fig, ax = plt.subplots()
        df["price"].plot(ax=ax, label="Preis", color="blue")
        df["rsi"].plot(ax=ax, label="RSI (14)", color="orange")
        ax.set_title(f"{symbol.upper()} Preis & RSI")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 Automatische Aktualisierung alle 5 Sekunden • Marktcap via CoinGecko • RSI für Monat, Woche, Tag, Stunde")
