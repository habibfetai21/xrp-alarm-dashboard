# app.py
import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Küchen- & Möbel-Trends", layout="wide")
st.title("📊 Küchen- & Möbel-Trends in Österreich 🇦🇹")

# Pytrends Setup
pytrends = TrendReq(hl='de-AT', tz=360)

# ---- Abschnitt 1: Möbelix / Mömax / Küchenplanung ----
st.header("Google Trends: Möbelanbieter & Küchenplanung")

keywords_main = ["Möbelix", "Mömax", "Küchenplanung"]

timeframes = {
    "Letzte 12 Monate": "today 12-m",
    "Letzte 5 Jahre": "today 5-y"
}
selected_timeframe = st.selectbox("Zeitraum auswählen", list(timeframes.keys()), key="main_tf")
timeframe = timeframes[selected_timeframe]

pytrends.build_payload(keywords_main, cat=0, timeframe=timeframe, geo="AT", gprop='')
data_time = pytrends.interest_over_time()
if not data_time.empty:
    fig = px.line(data_time.reset_index(), x='date', y=keywords_main, title='Trends über Zeit')
    st.plotly_chart(fig, use_container_width=True)

data_region = pytrends.interest_by_region(resolution='region', inc_low_vol=True)
if not data_region.empty:
    fig2 = px.bar(data_region.sort_values(by=keywords_main[0], ascending=False),
                  x=data_region.sort_values(by=keywords_main[0], ascending=False).index,
                  y=keywords_main, title="Beliebtheit nach Bundesland")
    st.plotly_chart(fig2, use_container_width=True)

# ---- Abschnitt 2: Küchenarten ----
st.header("Google Trends: Küchenarten")
kitchen_types = ["Landhausküche", "Moderne Küche", "Designküche"]

selected_timeframe_kt = st.selectbox("Zeitraum Küchenarten", list(timeframes.keys()), key="kt_tf")
pytrends.build_payload(kitchen_types, cat=0, timeframe=timeframes[selected_timeframe_kt], geo="AT", gprop='')
data_kt = pytrends.interest_over_time()
if not data_kt.empty:
    fig3 = px.line(data_kt.reset_index(), x='date', y=kitchen_types, title='Beliebte Küchenarten')
    st.plotly_chart(fig3, use_container_width=True)

# ---- Abschnitt 3: Küchenhersteller ----
st.header("Google Trends: Küchenhersteller")
kitchen_brands = ["Nolte Küche", "Ikea Küche", "Dan Küche"]

selected_timeframe_kb = st.selectbox("Zeitraum Küchenhersteller", list(timeframes.keys()), key="kb_tf")
pytrends.build_payload(kitchen_brands, cat=0, timeframe=timeframes[selected_timeframe_kb], geo="AT", gprop='')
data_kb = pytrends.interest_over_time()
if not data_kb.empty:
    fig4 = px.line(data_kb.reset_index(), x='date', y=kitchen_brands, title='Beliebte Küchenhersteller')
    st.plotly_chart(fig4, use_container_width=True)

# ---- Abschnitt 4: Küchengeräte-Marken ----
st.header("Google Trends: Küchengeräte-Marken")
appliance_brands = ["Bosch", "Siemens", "AEG"]

selected_timeframe_ab = st.selectbox("Zeitraum Geräte-Marken", list(timeframes.keys()), key="ab_tf")
pytrends.build_payload(appliance_brands, cat=0, timeframe=timeframes[selected_timeframe_ab], geo="AT", gprop='')
data_ab = pytrends.interest_over_time()
if not data_ab.empty:
    fig5 = px.line(data_ab.reset_index(), x='date', y=appliance_brands, title='Beliebte Küchengeräte-Marken')
    st.plotly_chart(fig5, use_container_width=True)
