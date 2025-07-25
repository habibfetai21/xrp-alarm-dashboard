import streamlit as st
import requests
import datetime
import pandas as pd
import ta  # Technische Analyse-Bibliothek
from streamlit_autorefresh import st_autorefresh

# Coins und ihre CoinGecko-IDs
coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "VECHAIN": "vechain",
    "DOGE": "dogecoin",
    "FLOKI": "floki"
}

st.set_page_config(page_title="Xrp Pro Dashboard", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Pro Dashboard – Kurse, Charts & Profi-Signale")

st_autorefresh(interval=15 * 1000, key="refresh")

# 1️⃣ Preise abrufen
def fetch_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    res = requests.get(url)
    if res.status_code == 429:
        st.error("Rate Limit erreicht. Bitte etwas warten.")
        return None
    res.raise_for_status()
    return res.json()

# 2️⃣ Chartdaten & Signale berechnen
@st.cache_data(ttl=300)
def fetch_technical(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    data = requests.get(url).json()
    df = pd.DataFrame(data["prices"], columns=["ts", "close"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.set_index("ts")
    # Indikatoren
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    atr = ta.volatility.AverageTrueRange(high=df["close"], low=df["close"], close=df["close"], window=14)
    df["supertrend"] = (df["close"] + atr.atr()) / 2  # vereinfachter Supertrend = Durchschnitt + ATR
    return df

prices = fetch_prices()

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📈 Live Kurse & Profi-Signale")
    if not prices:
        st.warning("Keine Kursdaten verfügbar.")
    else:
        for sym, cid in coins.items():
            price = prices.get(cid, {}).get("eur")
            if not price:
                st.warning(f"{sym}: keine Daten")
                continue

            # 3️⃣ Charts & Signale abrufen (nur XRP im Beispiel rechts)
            signal = "✅ Halten"
            if sym == "XRP":
                df = fetch_technical(cid, 30)
                latest = df.iloc[-1]
                # RSI Signale
                if latest["rsi"] > 70:
                    signal = "⚠️ Verkauf (RSI overbought)"
                elif latest["rsi"] < 30:
                    signal = "🚀 Kauf (RSI oversold)"
                # Supertrend-Signal
                signal = (signal + " / 📈 Supertrend:" +
                          ("Kauf" if latest["close"] > latest["supertrend"] else "Verkauf"))
            st.write(f"{sym}: €{price:.4f} → {signal}")

with col2:
    st.header("📊 XRP Chart + Signale (30 Tage)")
    df = fetch_technical(coins["XRP"], 30)
    st.line_chart(df["close"])
    st.line_chart(df["rsi"])

st.caption("🔄 UI alle 15s • Dat
