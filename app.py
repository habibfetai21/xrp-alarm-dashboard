 col2:
    st.header("📊 Kursverlauf XRP (CoinGecko)")
    days = st.select_slider("Zeitraum wählen:", options=[7, 14, 21, 30], value=7)
    try:
        df = fetch_market_chart("XRP", days)
        if not df.empty:
            st.line_chart(df)
        else:
            st.write("Chart-Daten nicht verfügbar")
    except Exception as e:
        st.error
