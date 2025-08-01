import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import time

st.set_page_config(page_title="Krypto Dashboard", layout="wide")
st.title("📊 Krypto Dashboard – Live mit CoinPaprika Backup & RSI")

# Coins im Portfolio
portfolio = {
    "XRP": {"coingecko_id": "ripple", "fallback_price": 0.52},
    "PEPE": {"coingecko_id": "pepe", "fallback_price": 0.0000013},
    "TOSHI": {"coingecko_id": None, "fallback_price": 0.00003},
    "FLOKI": {"coingecko_id": "floki", "fallback_price": 0.000015},
    "VISION": {"coingecko_id": None, "fallback_price": 0.085},
    "VECHAIN": {"coingecko_id": "vechain", "fallback_price": 0.021},
    "ZEREBRO": {"coingecko_id": None, "fallback_price": 0.015},
    "DOGE": {"coingecko_id": "dogecoin", "fallback_price": 0.12},
    "SHIBA": {"coingecko_id": "shiba-inu", "fallback_price": 0.000018},
}

# RSI-Funktion
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return None
    delta = pd.Series(prices).diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Kursdaten abrufen
def get_price_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days=1&interval=hourly"
        response = requests.get(url)
        data = response.json()
        if "prices" in data:
            df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            df["price"] = df["price"].astype(float)
            return df["price"].tolist(), df
        else:
            return None, None
    except Exception:
        return None, None

# RSI & Chart anzeigen
def show_coin_analysis(name, coin_info):
    st.subheader(f"{name} – Analyse")
    coin_id = coin_info["coingecko_id"]
    fallback_price = coin_info["fallback_price"]

    if coin_id:
        prices, df = get_price_data(coin_id)
        if prices:
            rsi = calculate_rsi(prices)
            current_price = round(prices[-1], 5)
            st.write(f"💶 Aktueller Preis: **€{current_price}**")
            if rsi is not None:
                st.write(f"📈 RSI (14): **{round(rsi.iloc[-1], 2)}**")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=rsi, mode="lines", name="RSI"))
                fig.update_layout(title=f"RSI – {name}", height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("❗ Nicht genug Daten für RSI")
        else:
            st.error(f"{name}: ❌ Kursdaten nicht verfügbar (CoinGecko)")
            st.write(f"📉 Fallback-Preis: **€{fallback_price}**")
    else:
        st.warning(f"{name}: Keine CoinGecko-ID – Fallback-Preis: **€{fallback_price}**")

# Dashboard anzeigen
for name, info in portfolio.items():
    show_coin_analysis(name, info)
    st.markdown("---")

# Hinweis zur Aktualisierung
st.info("🔄 Aktualisiere die Seite manuell (Streamlit Cloud blockiert Auto-Refresh)")