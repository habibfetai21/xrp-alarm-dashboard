import streamlit as st
import requests
import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Coins, die du überwachen willst
coins = ["XRP", "BTC", "ETH", "VECHAIN", "DOGE", "FLOKI"]

def fetch_prices():
    url = "https://api.bitpanda.com/v1/ticker"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    # Bitpanda liefert Einträge wie "XRP_EUR"
    prices = {}
    for coin in coins:
        key = f"{coin}_EUR"
        if key in data and "EUR" in data[key]:
            prices[coin] = float(data[key]["EUR"])
        else:
            prices[coin] = None
    return prices

@st.cache_data(ttl=60)
def fetch_market_chart(coin, days=7):
    # Fallback auf CoinGecko für Charts
    cg_ids = {"XRP": "ripple", "BTC": "bitcoin", "ETH": "ethereum",
              "VECHAIN": "vechain", "DOGE": "dogecoin", "FLOKI": "floki"}
    coin_id = cg_ids[coin]
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    prices = data.get("prices", [])
    dates = [datetime.datetime.fromtimestamp(p[0]/1000) for p in prices]
    values = [p[1] for p in prices]
    df = pd.DataFrame({"Datum": dates, "Preis (EUR)": values}).set_index("Datum")
    return df

st.set_page_config(page_title="Xrp Alarm Plus", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Alarm Plus – Bitpanda Live Kurse & Charts")

st_autorefresh(interval=15 * 1000, key="refresh")

# Preise abrufen
try:
    prices = fetch_prices()
except Exception as e:
    st.error(f"Fehler beim Laden der Preise: {e}")
    prices = {coin: None for coin in coins}

col1, col2 = st.columns(2)

with col1:
    st.header("📈 Live Kurse & Empfehlungen (Bitpanda)")
    for sym, pr in prices.items():
        if pr is None:
            st.write(f"⚠️ {sym}: Daten nicht verfügbar")
        else:
            text = f"{sym}: €{pr:.4f}"
            if sym == "XRP":
                if pr < 3.00:
                    st.error(text + " ⬇️ Verkauf empfohlen!")
                elif pr > 3.80:
                    st.success(text + " 🚀 Kauf empfohlen!")
                else:
                    st.info(text + " ⚠️ Halten")
            else:
                st.write(text)

with col2:
    st.header("📊 Kursverlauf XRP (CoinGecko)")
    days = st.select_slider("Zeitraum wählen:", options=[7, 14, 21, 30], value=7)
    try:
        df = fetch_market_chart("XRP", days)
        if not df.empty:
            st.line_chart(df)
        else:
            st.write("Chart-Daten nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler beim Laden des Charts: {e}")

st.caption("🔄 Frontend refresh 15 s · Preise neu alle 60 s")
