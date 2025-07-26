import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import telegram

# === Telegram Bot Setup ===
TELEGRAM_TOKEN = "8105594323:AAGcB-zUIaUGhvITQ430Lt-NvmjkZE3mRtA"
TELEGRAM_CHAT_ID = 7620460833

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        st.error(f"Telegram Nachricht konnte nicht gesendet werden: {e}")

# === Assets mit Menge + Kaufpreis (€/Coin) ===
assets = {
    "ripple": {"amount": 1562.17810323, "buy_price": 0.40},
    "pepe": {"amount": 67030227.81257255, "buy_price": 0.000001},
    "toshi": {"amount": 1240005.931827331, "buy_price": 0.005},
    "floki": {"amount": 3963427.93550601, "buy_price": 0.0001},
    "vision": {"amount": 1796.50929707, "buy_price": 0.10},
    "vechain": {"amount": 3915.56782781, "buy_price": 0.02},
    "zerebro": {"amount": 2892.77660435, "buy_price": 0.05},
    "dogecoin": {"amount": 199.28496554, "buy_price": 0.06},
    "shiba-inu": {"amount": 1615356.17235691, "buy_price": 0.00001},
}

@st.cache_data(ttl=600)
def get_price(coingecko_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=eur"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get(coingecko_id, {}).get("eur", None)

@st.cache_data(ttl=900)
def fetch_price_history(coingecko_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=eur&days={days}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    prices = data.get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def calc_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_rsi_signal(rsi):
    if rsi < 30:
        return "🚀 Kaufempfehlung – RSI < 30"
    elif rsi > 70:
        return "⚠️ Verkauf – RSI > 70"
    else:
        return "📊 Beobachten"

# === Portfolio Übersicht + Gewinn/Verlust ===
def portfolio_overview(assets):
    rows = []
    total_value = 0
    total_cost = 0

    for coin_id, info in assets.items():
        price = get_price(coin_id)
        if price is None:
            st.warning(f"{coin_id} Preis nicht verfügbar")
            continue
        amount = info["amount"]
        buy_price = info["buy_price"]
        value = price * amount
        cost = buy_price * amount
        profit_loss = value - cost
        profit_loss_pct = (profit_loss / cost) * 100 if cost > 0 else 0

        total_value += value
        total_cost += cost

        rows.append({
            "Coin": coin_id,
            "Menge": amount,
            "Aktueller Preis (€)": price,
            "Kaufpreis (€)": buy_price,
            "Wert (€)": value,
            "Gewinn/Verlust (€)": profit_loss,
            "Gewinn/Verlust (%)": profit_loss_pct
        })

    df = pd.DataFrame(rows)
    total_profit_loss = total_value - total_cost
    total_profit_loss_pct = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0

    return df, total_value, total_profit_loss, total_profit_loss_pct

# === Streamlit UI ===
st.title("📈 Erweitertes Krypto-Portfolio Dashboard")

df_portfolio, total_value, total_pl, total_pl_pct = portfolio_overview(assets)
st.dataframe(df_portfolio.style.format({
    "Menge": "{:,.4f}",
    "Aktueller Preis (€)": "€{:,.4f}",
    "Kaufpreis (€)": "€{:,.4f}",
    "Wert (€)": "€{:,.2f}",
    "Gewinn/Verlust (€)": "€{:,.2f}",
    "Gewinn/Verlust (%)": "{:.2f} %"
}))

st.markdown(f"### Gesamtwert Portfolio: €{total_value:,.2f}")
st.markdown(f"### Gesamt Gewinn/Verlust: €{total_pl:,.2f} ({total_pl_pct:.2f} %)")

# === Chart + RSI Signal pro Coin ===
for coin_id in assets.keys():
    df = fetch_price_history(coin_id)
    if df is None or df.empty:
        st.warning(f"{coin_id}: Kursdaten nicht verfügbar")
        continue

    st.subheader(f"{coin_id.upper()} Kursverlauf & RSI Signal")
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(df["date"], df["price"], label="Preis (€)")
    rsi = calc_rsi(df["price"])
    ax2 = ax.twinx()
    ax2.plot(df["date"], rsi, color="orange", label="RSI")
    ax.set_ylabel("Preis (€)")
    ax2.set_ylabel("RSI")
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    st.pyplot(fig)

    latest_rsi = rsi.iloc[-1]
    signal = analyze_rsi_signal(latest_rsi)
    st.markdown(f"**Aktuelles RSI Signal:** {signal}")

# === Telegram Benachrichtigung bei +/-5% Tagesänderung (Optional) ===
if st.checkbox("Telegram-Benachrichtigung bei ±5% Tagesänderung aktivieren"):
    for coin_id in assets.keys():
        df = fetch_price_history(coin_id, days=2)
        if df is None or len(df) < 2:
            continue
        yesterday_close = df["price"].iloc[0]
        today_close = df["price"].iloc[-1]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        if abs(change_pct) >= 5:
            msg = f"⚠️ {coin_id.upper()} Kursänderung: {change_pct:.2f}% in den letzten 24h. Aktueller Preis: €{today_close:.4f}"
            send_telegram_message(msg)
            st.info(f"Telegram Nachricht gesendet: {msg}")

st.caption("🔄 Dashboard aktualisiert alle 15 Minuten")
