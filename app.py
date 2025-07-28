# 📦 Block 1: Imports, Einstellungen, Coin-Setup
import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import plotly.graph_objs as go

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Analyse Dashboard – Live mit RSI, Charts, Marketcap")

coins = {
    "XRP": "ripple",
    "PEPE": "pepe",
    "TOSHI": "toshi",
    "FLOKI": "floki",
    "VISION": "vision-game",
    "VECHAIN": "vechain",
    "ZEREBRO": "zerebro",
    "DOGE": "dogecoin",
    "SHIBA": "shiba-inu"
}

portfolio = {
    "TOSHI": 1240005.9318,
    "VISION": 1796.5093,
    "ZEREBRO": 2892.7766
}

# 📈 Block 2: RSI Berechnung
def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else np.nan

# 📡 Block 3: Kursdaten von CoinGecko abrufen
def fetch_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    try:
        res = requests.get(url, params={"vs_currency": "eur", "days": "30", "interval": "hourly"})
        data = res.json()
        prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit='ms')
        prices.set_index("timestamp", inplace=True)
        return prices
    except:
        return None

# 🔄 Block 4: Dashboard-Ansicht für jeden Coin
for name, coin_id in coins.items():
    st.subheader(f"{name} – Analyse")

    data = fetch_price_data(coin_id)
    if data is not None:
        current_price = round(data["price"].iloc[-1], 5)
        st.write(f"💰 Aktueller Preis: **€{current_price}**")

        if name in portfolio:
            bestand = portfolio[name]
            market_value = round(current_price * bestand, 2)
            st.write(f"📦 Marktwert Bestand: **€{market_value}**")

        # RSI-Werte
        rsi_14d = calculate_rsi(data["price"], 14)
        rsi_7d = calculate_rsi(data["price"].tail(7*24), 14)
        rsi_1d = calculate_rsi(data["price"].tail(24), 14)
        rsi_1h = calculate_rsi(data["price"].tail(1), 14)

        st.markdown(f"📈 **RSI 14d:** `{rsi_14d:.2f}` – {'🔴 Überkauft' if rsi_14d > 70 else '🟢 Unterkauft' if rsi_14d < 30 else '⚪ Neutral'}")
        st.markdown(f"📉 **RSI 7d:** `{rsi_7d:.2f}`")
        st.markdown(f"📉 **RSI 1d:** `{rsi_1d:.2f}`")
        st.markdown(f"⏱️ **RSI 1h:** `{rsi_1h:.2f}`")

        # Chart anzeigen
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["price"], mode="lines", name=f"{name} Kurs"))
        fig.update_layout(title=f"{name} – Kursverlauf (30 Tage)", xaxis_title="Zeit", yaxis_title="Preis in €")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"{name}: ❌ Kursdaten nicht verfügbar (CoinGecko)")

# 🔁 Automatische Aktualisierung alle 5 Sekunden lokal (ohne st.experimental_rerun für Streamlit Cloud)
time.sleep(5)
