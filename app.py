import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# === Telegram-Konfiguration ===
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_USER_ID = "7620460833"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            st.error(f"Telegram Fehler: {response.json()}")
    except Exception as e:
        st.error(f"Telegram Nachricht konnte nicht gesendet werden: {e}")

# === Automatische Seite alle 5 Sekunden neu laden ===
st_autorefresh(interval=5 * 1000, limit=None, key="refresh")

# === CoinGecko IDs & Bestände ===
coins = {
    "xrp": {"id": "ripple", "amount": 1562.17810323},
    "pepe": {"id": "pepe", "amount": 67030227.81257255},
    "toshi": {"id": "toshi-token", "amount": 1240005.931827331},
    "floki": {"id": "floki", "amount": 3963427.93550601},
    "vision": {"id": "vision", "amount": 1796.50929707},
    "vechain": {"id": "vechain", "amount": 3915.56782781},
    "zerebro": {"id": "zerebro", "amount": 2892.77660435},
    "doge": {"id": "dogecoin", "amount": 199.28496554},
    "shiba-inu": {"id": "shiba-inu", "amount": 1615356.17235691},
}

st.set_page_config(page_title="Erweitertes Krypto Dashboard", layout="wide")
st.title("📈 Erweitertes Krypto Dashboard mit automatischer Aktualisierung")

# === Funktionen ===
@st.cache_data(ttl=300)
def fetch_market_data(coin_id, vs_currency="eur", days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None
    return r.json()

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def plot_price_and_rsi(df, coin_name):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(df.index, df['price'], label="Preis (€)")
    ax1.set_title(f"{coin_name.upper()} Preisverlauf")
    ax1.legend()
    ax1.grid()

    ax2.plot(df.index, df['rsi'], label="RSI", color="orange")
    ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
    ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
    ax2.set_title(f"{coin_name.upper()} RSI")
    ax2.legend()
    ax2.grid()
    plt.tight_layout()
    st.pyplot(fig)

def fetch_marketcap(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get("market_data", {}).get("market_cap", {}).get("eur", None)

# === Hauptlogik ===
total_portfolio_value = 0.0

for symbol, data in coins.items():
    st.subheader(f"{symbol.upper()} – Analyse")

    coin_id = data["id"]
    amount = data["amount"]

    market_data = fetch_market_data(coin_id, days=30)
    if not market_data:
        st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar.")
        continue

    prices = pd.DataFrame(market_data['prices'], columns=["timestamp", "price"])
    prices['timestamp'] = pd.to_datetime(prices['timestamp'], unit='ms')
    prices.set_index('timestamp', inplace=True)

    prices['rsi'] = calculate_rsi(prices['price'])

    latest_price = prices['price'].iloc[-1]
    latest_rsi = prices['rsi'].iloc[-1]

    # Marketcap
    marketcap = fetch_marketcap(coin_id)

    # Portfolio Wert berechnen
    portfolio_value = amount * latest_price
    total_portfolio_value += portfolio_value

    st.write(f"Aktueller Kurs: €{latest_price:.6f}")
    st.write(f"Bestand: {amount:.4f} ⇒ Wert: €{portfolio_value:.2f}")
    if marketcap:
        st.write(f"Marktkapitalisierung: €{marketcap:,.0f}")
    else:
        st.write("Marktkapitalisierung: Nicht verfügbar")

    # RSI-Werte für verschiedene Zeiträume
    # Für die Zeiträume 1 Monat (30 Tage), 1 Woche (7 Tage), 1 Tag (1 Tag), 1 Stunde (1/24 Tag), 1 Minute (1/1440 Tag)
    st.write("RSI Werte (letzte Werte pro Zeitraum):")
    try:
        rsi_month = prices['rsi'][-30*24*60:] if len(prices) > 30*24*60 else prices['rsi']
        rsi_week = prices['rsi'][-7*24*60:] if len(prices) > 7*24*60 else prices['rsi']
        rsi_day = prices['rsi'][-24*60:] if len(prices) > 24*60 else prices['rsi']
        rsi_hour = prices['rsi'][-60:] if len(prices) > 60 else prices['rsi']
        rsi_minute = prices['rsi'][-1:]
        st.write(f"- Monat (30 Tage): {rsi_month.iloc[-1]:.2f}")
        st.write(f"- Woche (7 Tage): {rsi_week.iloc[-1]:.2f}")
        st.write(f"- Tag: {rsi_day.iloc[-1]:.2f}")
        st.write(f"- Stunde: {rsi_hour.iloc[-1]:.2f}")
        st.write(f"- Minute: {rsi_minute.iloc[-1]:.2f}")
    except Exception as e:
        st.write("RSI-Daten nicht ausreichend für alle Zeiträume.")

    # Kauf-/Verkaufsempfehlung anhand RSI
    signal = ""
    if latest_rsi < 30:
        signal = f"🚀 {symbol.upper()}: Kaufempfehlung (RSI {latest_rsi:.2f})"
        send_telegram_message(signal)
    elif latest_rsi > 70:
        signal = f"⚠️ {symbol.upper()}: Verkaufssignal (RSI {latest_rsi:.2f})"
        send_telegram_message(signal)
    else:
        signal = f"ℹ️ {symbol.upper()}: Neutral, beobachten (RSI {latest_rsi:.2f})"

    st.info(signal)

    # Chart anzeigen
    plot_price_and_rsi(prices, symbol)

st.markdown(f"## Gesamtwert Portfolio: €{total_portfolio_value:.2f}")

st.caption("🔄 Automatische Aktualisierung alle 5 Sekunden • Daten von CoinGecko • RSI & Marketcap inklusive • Telegram-Benachrichtigungen bei Kaufsignalen")
