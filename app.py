# app.py
import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px

st.title("Küchen- & Möbel-Trends in Österreich 🇦🇹")

# Pytrends Setup
pytrends = TrendReq(hl='de-AT', tz=360)

# Suchbegriffe
keywords = ["Möbelix", "Mömax", "Küchenplanung"]

st.header("Google Trends Daten")

# Zeiträume definieren
timeframes = {
    "Letzte 12 Monate": "today 12-m",
    "Letzte 5 Jahre": "today 5-y"
}

selected_timeframe = st.selectbox("Zeitraum auswählen", list(timeframes.keys()))
timeframe = timeframes[selected_timeframe]

# Bundesländer
region = "AT"  # Österreich

# Holen der Daten
pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=region, gprop='')

# Interesse über Zeit
data_time = pytrends.interest_over_time()
if not data_time.empty:
    st.subheader("Interesse über Zeit")
    data_time = data_time.reset_index()
    fig = px.line(data_time, x='date', y=keywords, title='Trends über Zeit')
    st.plotly_chart(fig)
else:
    st.write("Keine Daten verfügbar.")

# Interesse nach Bundesland
st.subheader("Interesse nach Bundesland")
data_region = pytrends.interest_by_region(resolution='region', inc_low_vol=True)
if not data_region.empty:
    data_region = data_region.sort_values(by=keywords[0], ascending=False)
    fig2 = px.bar(data_region, x=data_region.index, y=keywords, title="Beliebtheit nach Bundesland")
    st.plotly_chart(fig2)
else:
    st.write("Keine Daten verfügbar.")
