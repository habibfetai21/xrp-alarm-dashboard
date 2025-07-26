import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Coins mit Coinpaprika IDs
coins = {
    "xrp": {"symbol": "XRP", "coinpaprika_id": "xrp-xrp"},
    "btc": {"symbol": "BTC", "coinpaprika_id": "btc-bitcoin"},
    "eth": {"symbol": "ETH", "coinpaprika_id": "eth-ethereum"},
    "doge": {"symbol": "DOGE", "coinpaprika_id": "doge-dogecoin"},
    "floki": {"symbol": "FLOKI", "coinpaprika_id": None},  # kein Eintrag? Dann nur CC
    "pepe": {"symbol": "PEPE", "coinpaprika_id": None},
    "vechain": {"symbol": "VET", "coinpaprika_id": "vet-vechain"},
    "vision": {"symbol": "VISION", "coinpaprika_id": None},
    "zerebro": {"symbol": "ZEREBRO", "coinpaprika_id": None},
    "toshi": {"symbol": "TOSHI", "coinpaprika_id": None},
    "shiba-inu": {"symbol": "SHIB", "coinpaprika_id": "shib-shiba-inu"}
}

def get_price_cryptocompare(symbol, currency='EUR'):
    try:
        url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms={currency}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        price = data.get(currency)
        if price is None:
            return None
        return price
    except:
        return None

def get_price_coinpaprika(coin_id, currency='eur'):
    if not coin_id:
        return None
    try:
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        price = data['quotes'][currency.upper()]['price']
        return price
    except:
        return None

# RSI-Berechnung (vereinfacht)
def compute_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

st.title("📈 Krypto Alarm Dashboard mit CryptoCompare & Coinpaprika")

for key, coin in coins.items():
    symbol = coin['symbol']
    st.header(f"{key.upper()}")

    price = get_price_cryptocompare(symbol)
    if price is None:
        price = get_price_coinpaprika(coin['coinpaprika_id'])
    
    if price is None:
        st.warning(f"{key.upper()}: Kursdaten nicht verfügbar.")
        continue
    
    st.write(f"Aktueller Preis: €{price:.6f}")

    # Beispiel: Hol historische Daten von CryptoCompare (30 Tage) für RSI
    try:
        url_hist = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={symbol}&tsym=EUR&limit=30"
        r = requests.get(url_hist)
        r.raise_for_status()
        data_hist = r.json()
        prices = pd.Series([item['close'] for item in data_hist['Data']['Data']])
        rsi = compute_rsi(prices)
        latest_rsi = rsi.iloc[-1]
        st.write(f"RSI (14 Tage): {latest_rsi:.2f}")

        # Kauf-/Verkaufssignal basierend auf RSI
        if latest_rsi < 30:
            st.success("🚀 Kaufempfehlung (RSI < 30)")
        elif latest_rsi > 70:
            st.error("⚠️ Verkaufssignal (RSI > 70)")
        else:
            st.info("📊 Neutral / Abwarten")

        # Chart Preis + RSI
        fig, ax1 = plt.subplots()
        ax1.plot(prices.index, prices.values, color='blue', label='Preis (€)')
        ax1.set_ylabel('Preis (€)', color='blue')
        ax2 = ax1.twinx()
        ax2.plot(rsi.index, rsi.values, color='orange', label='RSI')
        ax2.axhline(30, color='green', linestyle='--')
        ax2.axhline(70, color='red', linestyle='--')
        ax2.set_ylabel('RSI', color='orange')
        plt.title(f"{key.upper()} Preis & RSI")
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Fehler bei historischen Daten für {key.upper()}: {e}")

st.caption("Datenquelle: CryptoCompare & Coinpaprika • Aktualisierung automatisch bei jedem Laden")
