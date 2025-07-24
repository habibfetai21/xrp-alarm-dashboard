import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import datetime

coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "VECHAIN": "vechain",
    "DOGE": "dogecoin",
    "FLOKI": "floki"
}

def get_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    try:
        response = requests.get(url)
        data = response.json()
        return {symbol: data.get(coins[symbol], {}).get("eur") for symbol in coins}
    except Exception as e:
        st.error(f"Fehler beim Laden der Preise: {e}")
        return {symbol: None for symbol in coins}

def get_market_chart(coin_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    try:
        data = requests.get(url).json()
        prices = data.get("prices", [])
        dates = [datetime.datetime.fromtimestamp(p[0]/1000) for p in prices]
        values = [p[1] for p in prices]
        return dates, values
    except Exception as e:
        st.error(f"Fehler beim Laden der Chart-Daten: {e}")
        return [], []

st.set_page_config(page_title="Xrp Alarm Plus", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Alarm Plus – Kurse & Charts in Euro")

st_autorefresh(interval=15 * 1000, key="refresh")

prices = get_prices()

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
    dates, values = get_market_chart("ripple", days)
    if dates:
        st.line_chart({"Datum": dates, "Preis (EUR)": values})
    else:
        st.write("Chart-Daten nicht verfügbar")

st.caption("🔄 Auto-Update alle 15 Sekunden")
