import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px

# ==============================
# INIT
# ==============================
st.set_page_config(page_title="Küchen-Markt Dashboard Österreich", layout="wide")
st.title("📊 Küchen-Markt Dashboard Österreich")

pytrends = TrendReq(hl='de-AT', tz=60)

# ==============================
# Sidebar Optionen
# ==============================
st.sidebar.header("Filter & Optionen")
keywords = ["Möbelix", "Mömax", "Küchenplanung"]
kitchen_types = ["Einbauküche", "Landhausküche", "Modulküche", "Designküche"]
device_brands = ["Siemens", "Bosch", "AEG", "Miele", "Samsung"]
kitchen_brands = ["IKEA", "Mömax", "Möbelix", "Leiner", "DanKüchen"]

selected_keywords = st.sidebar.multiselect("Keywords", keywords, default=keywords)
selected_kitchen_types = st.sidebar.multiselect("Küchenart", kitchen_types, default=kitchen_types)
selected_device_brands = st.sidebar.multiselect("Küchengeräte Marken", device_brands, default=device_brands)
selected_kitchen_brands = st.sidebar.multiselect("Küchenhersteller Marken", kitchen_brands, default=kitchen_brands)

timeframes = {"Letzte 30 Tage": "today 1-m", "Letzte 90 Tage": "today 3-m", "Letztes Jahr": "today 12-m"}
selected_timeframe = st.sidebar.selectbox("Zeitraum", list(timeframes.keys()), index=0)

# ==============================
# Helper Funktion
# ==============================
def get_trends_keywords(keywords_list, timeframe, geo='AT'):
    pytrends.build_payload(keywords_list, cat=0, timeframe=timeframe, geo=geo, gprop='')
    data = pytrends.interest_over_time()
    if not data.empty:
        data = data.drop(columns=["isPartial"])
    return data

# ==============================
# KEYWORDS TRENDS
# ==============================
st.header("🔑 Keyword Trends")
if selected_keywords:
    data_keywords = get_trends_keywords(selected_keywords, timeframes[selected_timeframe])
    if not data_keywords.empty:
        fig_keywords = px.line(data_keywords, x=data_keywords.index, y=data_keywords.columns,
                               labels={'value':'Suchinteresse', 'index':'Datum'}, title="Keyword Trends")
        st.plotly_chart(fig_keywords, use_container_width=True)
        latest_keywords = data_keywords.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Top Keyword aktuell:** {latest_keywords.idxmax()}")

# ==============================
# KÜCHENART TRENDS
# ==============================
st.header("🏠 Küchenarten Trends")
if selected_kitchen_types:
    data_kitchen_types = get_trends_keywords(selected_kitchen_types, timeframes[selected_timeframe])
    if not data_kitchen_types.empty:
        fig_kitchen_types = px.line(data_kitchen_types, x=data_kitchen_types.index, y=data_kitchen_types.columns,
                                    labels={'value':'Suchinteresse', 'index':'Datum'}, title="Küchenarten Trends")
        st.plotly_chart(fig_kitchen_types, use_container_width=True)
        latest_kitchen_types = data_kitchen_types.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Top Küchenart aktuell:** {latest_kitchen_types.idxmax()}")

# ==============================
# KÜCHENGERÄTE & HERSTELLER
# ==============================
st.header("🍳 Küchengeräte & Küchenhersteller Trends")

# Küchengeräte
if selected_device_brands:
    data_devices = get_trends_keywords(selected_device_brands, timeframes[selected_timeframe])
    if not data_devices.empty:
        fig_devices = px.line(data_devices, x=data_devices.index, y=data_devices.columns,
                              labels={'value':'Suchinteresse', 'index':'Datum'}, title="Küchengeräte Marken Trends")
        st.plotly_chart(fig_devices, use_container_width=True)
        latest_devices = data_devices.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Top Küchengeräte Marke aktuell:** {latest_devices.idxmax()}")

# Küchenhersteller
if selected_kitchen_brands:
    data_kitchens = get_trends_keywords(selected_kitchen_brands, timeframes[selected_timeframe])
    if not data_kitchens.empty:
        fig_kitchens = px.line(data_kitchens, x=data_kitchens.index, y=data_kitchens.columns,
                               labels={'value':'Suchinteresse', 'index':'Datum'}, title="Küchenhersteller Marken Trends")
        st.plotly_chart(fig_kitchens, use_container_width=True)
        latest_kitchens = data_kitchens.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Top Küchenhersteller Marke aktuell:** {latest_kitchens.idxmax()}")

# ==============================
# ONLINE-KÄUFE SCHÄTZUNG
# ==============================
st.header("🛒 Am meisten online gesuchte/gekaufte Marke")
combined_brands = selected_device_brands + selected_kitchen_brands
if combined_brands:
    data_combined = get_trends_keywords(combined_brands, timeframes[selected_timeframe])
    if not data_combined.empty:
        latest_combined = data_combined.iloc[-1].sort_values(ascending=False)
        st.markdown(f"**Häufigste Online-Kauf-Marke (Schätzung): {latest_combined.idxmax()}**")
        fig_combined = px.bar(latest_combined, x=latest_combined.index, y=latest_combined.values,
                              labels={'x':'Marke', 'y':'Suchinteresse'}, title="Online-Kauf-Interesse nach Marke")
        st.plotly_chart(fig_combined, use_container_width=True)

# ==============================
# BUNDESLÄNDER ANALYSE
# ==============================
st.header("🌍 Suche nach Bundesländern")
geo_keywords = selected_keywords + selected_kitchen_types + selected_device_brands + selected_kitchen_brands
if geo_keywords:
    pytrends.build_payload(geo_keywords, cat=0, timeframe=timeframes[selected_timeframe], geo='AT', gprop='')
    data_region = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
    if not data_region.empty:
        st.dataframe(data_region.sort_values(by=geo_keywords, ascending=False))
        for kw in geo_keywords:
            fig_region = px.choropleth(data_region, locations=data_region.index, locationmode="ISO-3166-2",
                                       color=kw, hover_name=data_region.index,
                                       color_continuous_scale="Blues", title=f"Suche nach Bundesländern: {kw}")
            st.plotly_chart(fig_region, use_container_width=True)
