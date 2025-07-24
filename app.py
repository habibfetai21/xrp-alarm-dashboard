import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "TOSHI": "toshi-token",
    "PEPPE": "peppe-token",
    "VISION": "vision-token",
    "VECHAIN": "vechain",
    "ZEREBRO": "zerebro-token",
    "DOGE": "dogecoin",
    "FLOKI": "floki"
}

def get_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    try:
        data = requests.get(url).json()
        return {symbol: data.get(coins[symbol], {}).get("usd") for symbol in coins}
    except:
        return {symbol: None for symbol in coins}

st.set_page_config(page_title="Xrp Alarm", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Alarm – Live-Kurse & Alarme")

# Automatischer Refresh alle 15 Sekunden
st_autorefresh(interval=15 * 1000, key="refresh")

prices = get_prices()
for sym, pr in prices.items():
    if pr is None:
        st.write(f"⚠️ {sym}: Daten nicht verfügbar")
    else:
        text = f"{sym}: ${pr:.4f}"
        if sym == "XRP":
            if pr < 3.34:
                st.error(text + " ⬇️ Unter 3.34!")
            elif pr > 3.84:
                st.success(text + " 🚀 Über 3.84!")
            else:
                st.info(text)
        else:
            st.write(text)

st.caption("🔄 Auto-Update alle 15 Sekunden")
    st.experimental_rerun()
