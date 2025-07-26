import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Erweitertes Krypto-Portfolio Dashboard", layout="wide")

st.title("💰 Erweitertes Krypto-Portfolio Dashboard")

# === Portfolio mit Bestand (Anzahl, Durchschnittspreis in EUR) ===
portfolio = {
    "xrp": {"amount": 1562, "avg_price": 1.7810323},
    "pepe": {"amount": 67030227, "avg_price": 0.81257255},
    "toshi": {"amount": 1240005, "avg_price": 0.931827331},      # Kein CoinGecko-Datensatz
    "floki": {"amount": 3963427, "avg_price": 0.93550601},
    "vision": {"amount": 1796, "avg_price": 0.50929707},
    "vechain": {"amount": 3915, "avg_price": 0.56782781},
    "zerebro": {"amount": 2892, "avg_price": 0.77660435},
    "doge": {"amount": 199, "avg_price": 0.28496554},
    "shiba": {"amount": 1615356, "avg_price": 0.17235691},
}

# === CoinGecko-IDs (für Preisdaten) ===
coingecko_ids = {
    "xrp": "ripple",
    "pepe": "pepe",
    "toshi": None,             # Kein offizieller CoinGecko-Eintrag
    "floki": "floki",
    "vision": "vision-token",
    "vechain": "vechain",
    "zerebro": "cerebro",
    "doge": "dogecoin",
    "shiba": "shiba-inu",
}

@st.cache_data(ttl=900)
def fetch_price(coingecko_id):
    if coingecko_id is None:
        return None
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=eur"
    try:
        r = requests.get(url)
        data = r.json()
        price = data[coingecko_id]["eur"]
        return float(price)
    except Exception:
        return None

total_value = 0
total_cost = 0
missing_data = []

st.subheader("Portfolio Details:")

for symbol, data in portfolio.items():
    coingecko_id = coingecko_ids.get(symbol)
    price = fetch_price(coingecko_id)
    amount = data["amount"]
    avg_price = data["avg_price"]

    if price is None:
        st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar")
        missing_data.append(symbol)
        continue

    current_value = price * amount
    cost_value = avg_price * amount
    profit_loss = current_value - cost_value
    profit_loss_pct = (profit_loss / cost_value) * 100 if cost_value != 0 else 0

    total_value += current_value
    total_cost += cost_value

    st.write(f"**{symbol.upper()}**: Aktueller Preis: €{price:.6f} | Bestand: {amount:,} | "
             f"Wert: €{current_value:,.2f} | Gewinn/Verlust: €{profit_loss:,.2f} ({profit_loss_pct:.2f}%)")

if total_cost == 0:
    total_cost = 1  # Vermeidung Division durch Null

total_profit_loss = total_value - total_cost
total_profit_loss_pct = (total_profit_loss / total_cost) * 100

st.markdown("---")
st.subheader("📊 Gesamtübersicht")
st.write(f"**Gesamtwert Portfolio:** €{total_value:,.2f}")
st.write(f"**Gesamt Gewinn/Verlust:** €{total_profit_loss:,.2f} ({total_profit_loss_pct:.2f}%)")

if missing_data:
    st.warning(f"Folgende Assets konnten nicht bewertet werden: {', '.join(missing_data).upper()}")

# Optional: kleine Chart-Darstellung für Portfolioverteilung
try:
    import matplotlib.pyplot as plt

    labels = []
    sizes = []

    for symbol, data in portfolio.items():
        coingecko_id = coingecko_ids.get(symbol)
        price = fetch_price(coingecko_id)
        if price is None:
            continue
        value = price * data["amount"]
        labels.append(symbol.upper())
        sizes.append(value)

    if sizes:
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        st.pyplot(fig)

except ImportError:
    st.info("Für die Darstellung der Portfolioverteilung ist matplotlib nötig.")
