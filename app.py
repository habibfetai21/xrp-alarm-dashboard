("📊 XRP Chart + Signale (30 Tage)")
    df = fetch_technical(coins["XRP"], 30)
    st.line_chart(df["close"])
    st.line_chart(df["rsi"])

st.caption("🔄 UI alle 15s • Daten aus CoinGecko • RSI & Supertrend • Cache: 5 Min.")
