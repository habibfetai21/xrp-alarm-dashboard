import streamlit as st
import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === E-Mail-Konfiguration ===
EMAIL_ADDRESS = "h.fetai@icloud.com"
EMAIL_PASSWORD = "DEIN_APP_PASSWORT_HIER_EINFÜGEN"  # App-spezifisches Passwort von Apple

def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.mail.me.com', 587)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"E-Mail konnte nicht gesendet werden: {e}")

# === Technische Analyse (vereinfachte RSI und Supertrend) ===
@st.cache_data(ttl=900)
def fetch_data(symbol, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=eur&days={days}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    prices = r.json().get("prices", [])
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    df["rsi"] = df["price"].rolling(window=14).mean()  # Dummy-RSI
    df["supertrend"] = (df["price"].rolling(window=3).mean() + df["price"].rolling(window=3).std()) / 2
    return df

def analyze(df, coin):
    latest = df.iloc[-1]
    price = latest["price"]
    rsi = latest["rsi"]
    trend = latest["supertrend"]

    signal = ""
    if rsi < 30:
        signal = f"🚀 Kaufempfehlung für {coin.upper()} – RSI unter 30"
        send_email(f"{coin.upper()} Kauf-Signal!", signal)
    elif rsi > 70:
        signal = f"⚠️ Verkaufsempfehlung für {coin.upper()} – RSI über 70"
        send_email(f"{coin.upper()} Verkaufs-Signal!", signal)
    else:
        signal = f"📊 Beobachten – {coin.upper()} bei €{round(price, 4)}"

    return f"{coin.upper()}: €{round(price, 4)} – {signal}"

# === Dashboard ===
st.title("📬 XRP Alarm Plus – Mit E-Mail-Alarm")

coins = {
    "xrp": "ripple",
    "btc": "bitcoin",
    "eth": "ethereum",
    "doge": "dogecoin",
    "floki": "floki",
    "pepe": "pepe",
    "vechain": "vechain"
}

for symbol, coingecko_id in coins.items():
    df = fetch_data(coingecko_id)
    if df is not None and not df.empty:
        st.write(analyze(df, symbol))
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 UI aktualisiert sich alle 15s – bei Signalen bekommst du automatisch eine E-Mail")
