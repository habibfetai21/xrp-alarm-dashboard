_prices.get(symbol)
        if price:
            value = amount * price
            total_value += value
            st.info(f"Aktuell: {price} €\n\n📦 Bestand: {round(amount, 4)} ⇒ €{round(value, 2)}")
        else:
            st.warning(f"{symbol.upper()}: Kursdaten nicht verfügbar.")

st.success(f"💰 Gesamtwert Portfolio: €{round(total_value, 2)}")
st.caption("🔄 Live-Daten über CoinGecko (teilweise Fallback für unbekannte Coins). Telegram-Warnungen bei RSI-Signalen.")
