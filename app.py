import streamlit as st
import requests
import pandas as pd
import ta
from streamlit_autorefresh import st_autorefresh

coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "VECHAIN": "vechain",
    "DOGE": "dogecoin",
    "FLOKI": "floki"
}

st.set_page_config(page_title="Xrp Pro Dashboard", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Pro Dashboard – Kurse & RSI-Signale")

st_autorefresh(interval=15 * 1000, key="refresh")

def fetch_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Fehler beim Laden der Preise")
        return None
    return res.json()

@st.cache_data(ttl=300)
def fetch_rsi(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    data = requests.get(url).json()
    df = pd.DataFrame(data["prices"], columns=["ts", "price"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.set_index("ts")
    df["rsi"] = ta.momentum.rsi(df["price"], window=14)
    return df

prices = fetch_prices()

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📈 Live Kurse & RSI-Signale")
    if not prices:
        st.warning("Keine Preisdaten verfügbar.")
    else:
        for sym, cid in coins.items():
            val = prices.get(cid, {}).get("eur")
            if not val:
                st.warning(f"{sym}: keine Daten")
                continue
            signal = "✅ Halten"
            if sym == "XRP":
                df = fetch_rsi(cid, 30)
                rsi = df["rsi"].iloc[-1]
                if rsi > 70:
                    signal = "⚠️ Verkauf (RSI überkauft)"
                elif rsi < 30:
                    signal = "🚀 Kauf (RSI überverkauft)"
            st.write(f"{sym}: €{val:.4f} → {signal}")

with col2:
    st.header("📊 XRP Chart + RSI (30 Tage)")
    df = fetch_rsi(coins["XRP"], 30)
    st.line_chart(df["price"])
    st.line_chart(df["rsi"])

st.caption("🔄 UI alle 15s • Kurse & RSI über CoinGecko • Daten 5 Min gecached")
