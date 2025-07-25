import streamlit as st
import requests
import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Xrp Alarm Plus", page_icon="🚨", layout="wide")
st.title("🚨 Xrp Alarm Plus – Live Kurse & Charts in €")

# Coins und ihre CoinGecko-IDs
coins = {
    "XRP": "ripple",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "VECHAIN": "vechain",
    "DOGE": "dogecoin",
    "FLOKI": "floki"
}

# Auto-Refresh alle 15 Sekunden
st_autorefresh(interval=15 * 1000, key="refresh")

# Funktion: Preise abrufen von CoinGecko
def fetch_prices():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    response = requests.get(url)
    if response.status_code == 429:
        st.error("API Rate Limit erreicht! Bitte etwas warten oder weniger häufig aktualisieren.")
        return None
    response.raise_for_status()
    return response.json()

# Funktion: XRP Kursverlauf (7, 14 oder 30 Tage)
@st.cache_data(ttl=60)
def fetch_market_chart(coin_id: str, days: int):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    prices = data.get("prices", [])
    if not prices:
        return pd.DataFrame()
    dates = [datetime.datetime.fromtimestamp(p[0] / 1000) for p in prices]
    values = [p[1] for p in prices]
    df = pd.DataFrame({"Datum": dates, "Preis (EUR)": values})
    df.set_index("Datum", inplace=True)
    return df

# Preise laden
prices = None
try:
    prices = fetch_prices()
except Exception as e:
    st.error(f"Fehler beim Laden der Preise: {e}")

# Zwei Spalten: links Kurse, rechts Chart
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📈 Live Kurse (EUR) & Kauf-/Verkaufshinweise")

    if prices is None:
        st.warning("Keine Preisdaten verfügbar.")
    else:
        for symbol, coin_id in coins.items():
            coin_data = prices.get(coin_id)
            if coin_data and "eur" in coin_data:
                eur_price = coin_data["eur"]
                text = f"{symbol}: €{eur_price:.4f}"

                # Beispiel Kauf/Verkaufsempfehlungen nur für XRP
                if symbol == "XRP":
                    if eur_price < 0.3:
                        st.error(text + " ⬇️ Verkauf empfohlen!")
                    elif eur_price > 0.8:
                        st.success(text + " 🚀 Kauf empfohlen!")
                    else:
                        st.info(text + " ⚠️ Halten")
                else:
                    st.write(text)
            else:
                st.warning(f"⚠️ {symbol}: Keine Daten")

with col2:
    st.header("📊 XRP Kursverlauf")

    days = st.select_slider(
        "Zeitraum wählen:",
        options=[7, 14, 30],
        value=7,
        help="Wähle den Zeitraum für den Kursverlauf in Tagen"
    )

    if prices is None:
        st.warning("Keine Kursdaten für Chart verfügbar.")
    else:
        try:
            df = fetch_market_chart(coins["XRP"], days)
            if df.empty:
                st.warning("Keine Chartdaten verfügbar.")
            else:
                st.line_chart(df["Preis (EUR)"])
        except Exception as e:
            st.error(f"Fehler beim Laden der Chartdaten: {e}")

# Footer / Statusanzeige
st.caption("🔄 Auto-Update alle 15 Sekunden · Kursquelle: CoinGecko · Charts nur für XRP")
