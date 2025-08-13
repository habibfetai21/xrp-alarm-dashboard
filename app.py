# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pytrends.request import TrendReq

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Österreich Küchen & Markt Dashboard", layout="wide")
st.title("📊 Österreich Küchen & Markt Dashboard")

# ==============================
# BANKEN & ZINSEN
# ==============================
st.header("🏦 Banken & Bauzinsen")
df_zinsen = pd.DataFrame({
    "Kategorie": ["EURIBOR (3M)", "Variable Bauzinsen", "Fixzinsen (25 Jahre)"],
    "Zinssatz (%)": [1.99, 3.24, 3.35]
})
st.table(df_zinsen)
fig1, ax1 = plt.subplots()
ax1.bar(df_zinsen["Kategorie"], df_zinsen["Zinssatz (%)"], color=["#4CAF50", "#2196F3", "#FFC107"])
ax1.set_ylabel("Zinssatz in %")
ax1.set_title("Zinsvergleich")
st.pyplot(fig1)

# ==============================
# BAUBRANCHE
# ==============================
st.header("🏗 Baubranche – Marktentwicklung Österreich")
df_bau = pd.DataFrame({
    "Jahr": [2023, 2024, 2025],
    "Produktion Veränderung (%)": [None, -4.4, 0.4]
})
st.line_chart(df_bau.set_index("Jahr"))
st.markdown("**Quelle:** FIEC-Statistik 2024/2025")

# ==============================
# GOOGLE TRENDS SETUP
# ==============================
st.header("🔍 Google Trends Analyse")
pytrends = TrendReq(hl='de-AT', tz=360)

# Sidebar Filter
st.sidebar.header("Filter & Optionen")
keywords_main = st.sidebar.multiselect("Keywords", ["Möbelix", "Mömax", "Küchenplanung"], default=["Möbelix", "Mömax", "Küchenplanung"])
kitchen_types = ["Einbauküche", "Modulküche", "Landhausküche", "Designküche", "Systemküche"]
selected_kitchens = st.sidebar.multiselect("Küchenarten", kitchen_types, default=kitchen_types)
timeframe_options = {"Letzte 12 Monate":"today 12-m", "Letzte 5 Jahre":"today 5-y", "Letzte 30 Tage":"now 30-d"}
selected_timeframe = st.sidebar.selectbox("Zeitraum", list(timeframe_options.keys()))
geo_option = st.sidebar.selectbox("Region", ["Österreich gesamt", "Bundesländer"], index=0)

# ==============================
# Funktion für Trends abrufen
# ==============================
def get_trends(keywords, timeframe, geo='AT'):
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
    data = pytrends.interest_over_time()
    if not data.empty:
        data = data.drop(columns=["isPartial"])
    return data

# ==============================
# Keyword-Trends
# ==============================
st.subheader("📈 Keyword Trends")
if keywords_main:
    data_main = get_trends(keywords_main, timeframe_options[selected_timeframe])
    if not data_main.empty:
        fig_main = px.line(data_main, x=data_main.index, y=data_main.columns,
                           labels={'value':'Suchinteresse', 'index':'Datum'}, title="Keyword-Trends")
        st.plotly_chart(fig_main, use_container_width=True)
        # Top 3 Keywords
        latest_values = data_main.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Top 3 Keywords aktuell:** {', '.join(latest_values.head(3).index)}")
        st.dataframe(data_main.tail(10))
    else:
        st.error("Keine Daten gefunden. Bitte später erneut versuchen.")

# ==============================
# Küchenarten-Trends
# ==============================
st.subheader("🍽 Küchenarten Trends")
if selected_kitchens:
    data_kitchen = get_trends(selected_kitchens, timeframe_options[selected_timeframe])
    if not data_kitchen.empty:
        fig_kitchen = px.line(data_kitchen, x=data_kitchen.index, y=data_kitchen.columns,
                              labels={'value':'Suchinteresse', 'index':'Datum'}, title="Küchenarten Trends")
        st.plotly_chart(fig_kitchen, use_container_width=True)
        # Top 3 Küchenarten
        latest_kitchen = data_kitchen.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Top 3 Küchenarten aktuell:** {', '.join(latest_kitchen.head(3).index)}")
        st.dataframe(data_kitchen.tail(10))

# ==============================
# Bundesländer Trends
# ==============================
if geo_option == "Bundesländer":
    st.subheader("🏢 Suchinteresse nach Bundesland (Keyword: Küchenplanung)")
    pytrends.build_payload(["Küchenplanung"], cat=0, timeframe=timeframe_options[selected_timeframe], geo='AT')
    region_data = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True)
    region_data_sorted = region_data.sort_values(by="Küchenplanung", ascending=False)
    fig_region = px.bar(region_data_sorted, x=region_data_sorted.index, y="Küchenplanung",
                        title="Suchinteresse nach Bundesland", labels={'Küchenplanung':'Suchinteresse', 'index':'Bundesland'})
    st.plotly_chart(fig_region, use_container_width=True)
    st.dataframe(region_data_sorted)

# ==============================
# Monatliche Auswertung
# ==============================
st.subheader("📅 Monatliche Auswertung (Möbelix & Mömax)")
if keywords_main:
    monthly_data = data_main.resample('M').mean()
    fig_monthly = px.line(monthly_data, x=monthly_data.index, y=monthly_data.columns,
                          labels={'value':'Suchinteresse', 'index':'Monat'}, title="Monatliche Trends")
    st.plotly_chart(fig_monthly, use_container_width=True)
