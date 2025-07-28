import streamlit as st
import pandas as pd
import requests
import numpy as np
import time
import plotly.graph_objs as go
from datetime import datetime, timedelta

# ========== Konfiguration ==========
st.set_page_config(page_title="Krypto-Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align: center;'>📊 Krypto-Dashboard (Live & RSI)</h1>", unsafe_allow_html=True)

# ========== Deine Coins ==========
portfolio = {
    "XRP": 1257.09,
    "PEPE": 123567890.123,
    "TOSHI": 1240005.9318,
    "FLOKI": 302000.87,
    "VISION": 1796.5093,
    "VECHAIN": 6000,
    "ZEREBRO": 2892.7766,
    "DOGE": 1200,
    "SHIBA": 8000000
}

# CoinGecko IDs
coingecko_ids = {
    "XRP": "ripple",
    "PEPE": "pepe",
    "FLOKI": "floki",
    "DOGE": "dogecoin",
    "SHIBA": "shiba-inu",
    "VECHAIN": "vechain"
}

# Fallback-Preise (nur falls API ausfällt)
fallback_prices = {
    "TOSHI": 0.000032,
    "VISION": 0.085,
    "ZEREBRO": 0.015
}

# ========== Funktionen ==========

def get_price_and_marketcap(coin):
    if coin in fallback_prices:
        price = fallback_prices[coin]
        marketcap = None
        return price, marketcap

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_ids[coin]}&vs_currencies=eur&include_market_cap=true"
        r = requests.get(url)
        data = r.json()
        price = data[coingecko_ids[coin]]["eur"]
        marketcap = data[coingecko_ids[coin]].get("eur_market_cap")
        return price, marketcap
    except:
        return None, None

def get_rsi(prices, period=14):
    if len(prices) < period:
        return None
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return round(100 - (100 / (1 + rs)), 2)

def fetch_ohlc_data(coin_id, days=30):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=eur&days={days}&interval=daily"
        r = requests.get(url)
        data = r.json()
        prices = [p[1] for p in data["prices"]]
        return prices
    except:
        return []

# ========== Dashboard Ausgabe ==========
for coin, amount in portfolio.items():
    st.markdown(f"### {coin} – Analyse")
    price, marketcap = get_price_and_marketcap(coin)
    
    if price:
        value = round(price * amount, 2)
        st.markdown(f"**➤ Aktueller Preis:** €{price:.5f}")
        st.markdown(f"**➤ Marktwert Bestand:** €{value:.2f}")
        if marketcap:
            st.markdown(f"**➤ MarketCap:** €{marketcap:,.0f}")
    else:
        st.error(f"{coin}: ❌ Kursdaten nicht verfügbar (CoinGecko)")

    # RSI-Berechnung (verschiedene Zeiträume)
    if coin in coingecko_ids:
        prices_30d = fetch_ohlc_data(coingecko_ids[coin], days=30)
        prices_7d = fetch_ohlc_data(coingecko_ids[coin], days=7)
        prices_1d = fetch_ohlc_data(coingecko_ids[coin], days=1)

        if prices_30d:
            rsi_m = get_rsi(prices_30d)
            rsi_w = get_rsi(prices_7d)
            rsi_d = get_rsi(prices_1d)

            st.markdown(f"📊 **RSI Monat:** `{rsi_m}` | Woche: `{rsi_w}` | Tag: `{rsi_d}`")

            # Performance-Chart (letzte 30 Tage)
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=prices_30d, mode='lines', name=f'{coin} Preis'))
            fig.update_layout(title=f"{coin} – 30-Tage Preisverlauf", height=300, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"{coin}: Keine Chartdaten verfügbar – Fallback-Preis verwendet.")

    st.divider()

# ========== Automatische Aktualisierung ==========
st.markdown("🔄 Automatische Aktualisierung alle **5 Sekunden** (Streamlit Cloud kompatibel)")
st_autorefresh = st.empty()
time.sleep(5)
st.rerun()
