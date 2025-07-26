import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.graph_objs as go
import time

# BLOCK 1 – Einstellungen & Coin-Liste
st.set_page_config(page_title="Krypto Dashboard", layout="wide")

# Benutzerdefinierte Coins und ihre Bestände
portfolio = {
    "xrp": 4023.87,
    "pepe": 1526000,
    "toshi": 1240005.9318,
    "floki": 210000,
    "vision": 1796.5093,
    "vechain": 2600,
    "zerebro": 2892.7766,
    "dogecoin": 395,
    "shiba-inu": 195000
}

# CoinGecko IDs (bitte bei Bedarf anpassen!)
coingecko_ids = {
    "xrp": "ripple",
    "pepe": "pepe",
    "toshi": "toshi",
    "floki": "floki",
    "vision": None,
    "vechain": "vechain",
    "zerebro": None,
    "dogecoin": "dogecoin",
    "shiba-inu": "shiba-inu"
}

fallback_prices = {
    "toshi": 0.000032,
    "vision": 0.085,
    "zerebro": 0.015
}

# BLOCK 2 – Preis & RSI-Funktionen
@st.cache_data(ttl=60)
def get_price(coin_id):
    if coin_id is None:
        return None
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=eur&include_market_cap=true"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()[coin_id]
    except:
        return None

@st.cache_data(ttl=60)
def fetch_candle_data(coin_id, days=30):
    if coin_id is None:
        return None
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}&interval=daily"
    try:
        r = requests.get(url)
        data = r.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except:
        return None

def calculate_rsi(df, period: int = 14):
    if df is None or df.empty or len(df) < period:
        return None
    delta = df["price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# BLOCK 3 – Automatische Aktualisierung (kompatibel mit Streamlit Cloud)
placeholder = st.empty()
refresh_interval = 5  # Sekunden

with st.sidebar:
    st.markdown("🕒 **Automatische Aktualisierung**")
    progress_bar = st.progress(0)
    count = st.empty()

    for i in range(refresh_interval):
        progress_bar.progress(i / refresh_interval)
        count.markdown(f"Aktualisierung in **{refresh_interval - i} Sekunden**...")
        time.sleep(1)

    st.rerun()

# Hauptbereich – Analyse für alle Coins
st.title("📊 Krypto Portfolio Analyse mit RSI & Live-Daten")

for coin, amount in portfolio.items():
    st.subheader(f"{coin.upper()} – Analyse")

    coin_id = coingecko_ids.get(coin)
    price_data = get_price(coin_id)
    price = price_data["eur"] if price_data else fallback_prices.get(coin)

    if price:
        market_value = price * amount
        st.metric(f"{coin.upper()} ➤ Aktueller Preis", f"€{price:,.5f}")
        st.metric(f"{coin.upper()} ➤ Marktwert Bestand", f"€{market_value:,.2f}")
    else:
        st.warning(f"{coin.upper()}: ❌ Kursdaten nicht verfügbar (CoinGecko)")

    # RSI Analyse & Chart
    df = fetch_candle_data(coin_id)
    if df is not None:
        for period, label in zip([14, 7, 30], ["Tage", "1 Woche", "1 Monat"]):
            rsi = calculate_rsi(df, period)
            if rsi is not None:
                last_rsi = round(rsi.iloc[-1], 2)
                signal = "🟢 Kauf" if last_rsi < 30 else "🔴 Verkauf" if last_rsi > 70 else "⚪ Neutral"
                st.write(f"**RSI ({label}):** {last_rsi} – {signal}")
        
        # Chart anzeigen
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Preisverlauf"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"{coin.upper()}: Keine Chartdaten verfügbar – Fallback-Preis verwendet.")
