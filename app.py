import streamlit as st
import requests
import datetime

coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "VECHAIN": "vechain",
    "DOGE": "dogecoin",
    "FLOKI": "floki"
}

# Cache mit manuellem Zeitcheck
@st.cache_data(ttl=60)
def fetch_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {sym: data.get(coins[sym], {}).get("eur") for sym in coins}

@st.cache_data(ttl=60)
def fetch_market_chart(coin_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    prices = data.get("prices", [])
    dates = [datetime.datetime.fromtimestamp(p[0]/1000) for p in prices]
    values = [p[1] for p in prices]
    return dates, values

st.set_page_config(page_title="Xrp Alarm Plus", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Alarm Plus – Kurse & Charts in Euro")

# UI refresht alle 15 Sekunden
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15 * 1000, key="refresh")

try:
    prices = fetch_prices()
except Exception as e:
    st.error(f"Fehler beim Laden der Preise: {e}")
    prices = {sym: None for sym in coins}

col1, col2 = st.columns(2)

with col1:
    st.header("📈 Live Kurse & Kauf-/Verkaufsempfehlungen")
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
    st.header("📊 Kursverlauf XRP")
    days = st.select_slider(
        "Zeitraum wählen:",
        options=[7, 14, 21, 30],
        value=7
    )
    try:
        dates, values = fetch_market_chart("ripple", days)
        if dates:
            st.line_chart({"Datum": dates, "Preis (EUR)": values})
        else:
            st.write("Chart-Daten nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler beim Laden der Chart-Daten: {e}")

st.caption("🔄 Auto-Update alle 15 Sekunden, API-Daten alle 60 Sekunden (Cache)")
