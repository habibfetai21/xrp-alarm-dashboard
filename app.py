_id in coins.items():
    df = fetch_data(coingecko_id)
    if df is not None and not df.empty:
        st.write(analyze(df, symbol))
    else:
        st.warning(f"{symbol.upper()}: Marktdaten nicht verfügbar")

st.caption("🔄 UI aktualisiert sich alle 15 Sekunden – Signale basieren auf RSI & Supertrend (vereinfacht)")
