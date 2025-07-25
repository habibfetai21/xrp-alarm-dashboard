import streamlit as st
import requests
import pandas as pd
import ta
import matplotlib.pyplot as plt

# Coin Liste mit CoinGecko IDs
coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "VECHAIN": "vechain",
    "DOGE": "dogecoin",
    "FLOKI": "floki",
    "PEPE": "pepe"
}

st.set_page_config(page_title="Krypto Trend & Kauf Dashboard", page_icon="📈", layout="wide")
st.title("📈 Krypto Trend & Kauf Dashboard")

# Funktion: Preise abfragen
def fetch_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Fehler beim Laden der Preise")
        return None
    return res.json()

# Funktion: Kursdaten mit RSI und MA laden
@st.cache_data(ttl=300)
def fetch_market_data(coin_id, days=60):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    data = requests.get(url).json()
    prices = data.get("prices", [])
    if not prices:
        return None
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["rsi"] = ta.momentum.rsi(df["price"], window=14)
    df["ma50"] = df["price"].rolling(window=50).mean()
    df["ma200"] = df["price"].rolling(window=200).mean()
    return df.dropna()

prices = fetch_prices()

if not prices:
    st.warning("Keine Preisdaten verfügbar.")
else:
    for sym, cid in coins.items():
        price = prices.get(cid, {}).get("eur")
        if price is None:
            st.write(f"{sym}: Daten nicht verfügbar")
            continue
        df = fetch_market_data(cid, days=30)
        if df is None or df.empty:
            st.write(f"{sym}: Marktdaten nicht verfügbar")
            continue

        latest_rsi = df["rsi"].iloc[-1]
        ma50 = df["ma50"].iloc[-1]
        ma200 = df["ma200"].iloc[-1]

        # Trend bestimmen: bullish wenn MA50 über MA200
        trend = "Bullish 📈" if ma50 > ma200 else "Bearish 📉"

        # Kauf-/Verkaufssignal ableiten
        if latest_rsi < 30 and trend == "Bullish 📈":
            signal = "🚀 Kauf empfohlen!"
        elif latest_rsi > 70 and trend == "Bearish 📉":
            signal = "⚠️ Verkauf empfohlen!"
        else:
            signal = "➡️ Halten"

        # Anzeige Header mit Preis & Signal
        st.subheader(f"{sym}: €{price:.4f} | Trend: {trend} | RSI: {latest_rsi:.1f} | Signal: {signal}")

        # Plot Kursverlauf der letzten 30 Tage
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(df.index, df["price"], label="Preis (EUR)")
        ax.plot(df.index, df["ma50"], label="MA50")
        ax.plot(df.index, df["ma200"], label="MA200")
        ax.set_title(f"{sym} Kursverlauf letzte 30 Tage")
        ax.set_xlabel("Datum")
        ax.set_ylabel("Preis in €")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

st.caption("Daten via CoinGecko API • RSI & MA berechnet • Updates alle 5 Minuten")
