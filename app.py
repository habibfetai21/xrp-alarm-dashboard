# app.py
import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Küchen & Möbel Trends Österreich", layout="wide")
st.title("📊 Küchen- & Möbel-Trends in Österreich 🇦🇹")

# Pytrends Setup
pytrends = TrendReq(hl='de-AT', tz=360)

# Kategorien mit Keywords
trend_groups = {
    "Möbel & Küchenplanung": ["Möbelix", "Mömax", "Küchenplanung"],
    "Küchenarten": ["Landhausküche", "Moderne Küche", "Designküche"],
    "Küchengeräte-Marken": ["Bosch Küche", "Siemens Küche", "AEG Küche"],
    "Küchenhersteller": ["Nobilia", "Häcker Küche", "IKEA Küche"]
}

# Zeitraum-Auswahl
timeframes = {
    "Letzte 12 Monate": "today 12-m",
    "Letzte 5 Jahre": "today 5-y"
}
selected_timeframe = st.selectbox("Zeitraum auswählen", list(timeframes.keys()))
timeframe = timeframes[selected_timeframe]

# Funktion mit Cache + Wartezeit
@st.cache_data(ttl=86400)
def get_trends(keyword, timeframe):
    time.sleep(5)  # Anti-Blockade
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='AT', gprop='')
    df_time = pytrends.interest_over_time()
    df_region = pytrends.interest_by_region(resolution='region', inc_low_vol=True)
    return df_time, df_region

# Funktion für Top-Marken (Ranking)
@st.cache_data(ttl=86400)
def get_top_keywords(keywords, timeframe):
    scores = {}
    for kw in keywords:
        try:
            df_time, _ = get_trends(kw, timeframe)
            if not df_time.empty:
                scores[kw] = df_time[kw].mean()
        except:
            scores[kw] = 0
    top_df = pd.DataFrame.from_dict(scores, orient='index', columns=['Score']).sort_values(by='Score', ascending=False)
    return top_df

# Schleife durch jede Kategorie
for group_name, keywords in trend_groups.items():
    st.subheader(f"📌 {group_name}")

    # Zeit- und Regionsdaten kombinieren
    data_time_combined = pd.DataFrame()
    data_region_combined = pd.DataFrame()
    for kw in keywords:
        df_time, df_region = get_trends(kw, timeframe)
        if not df_time.empty:
            data_time_combined[kw] = df_time[kw]
        if not df_region.empty:
            df_region = df_region.rename(columns={kw: "Wert"}).reset_index()
            df_region["Keyword"] = kw
            data_region_combined = pd.concat([data_region_combined, df_region])

    # Zeitverlauf anzeigen
    if not data_time_combined.empty:
        data_time_combined = data_time_combined.reset_index()
        fig_time = px.line(data_time_combined, x='date', y=keywords, title=f"Interesse über Zeit – {group_name}")
        st.plotly_chart(fig_time, use_container_width=True)

    # Bundesländer anzeigen
    if not data_region_combined.empty:
        fig_region = px.bar(
            data_region_combined,
            x='geoName',
            y='Wert',
            color='Keyword',
            barmode='group',
            title=f"Beliebtheit nach Bundesland – {group_name}"
        )
        st.plotly_chart(fig_region, use_container_width=True)

# 🔹 Top 10 Online-Küchenmarken
st.subheader("🏆 Top Online Küchenmarken in Österreich (Ranking nach Suchvolumen)")
all_manufacturers = ["Nobilia", "Häcker Küche", "IKEA Küche", "Leicht", "Poggenpohl", "Bulthaup", "Schüller", "Next125", "Pino", "Wellmann"]
top_keywords_df = get_top_keywords(all_manufacturers, timeframe)
fig_top = px.bar(top_keywords_df.head(10), x=top_keywords_df.head(10).index, y='Score', title="Top Online Küchenmarken")
st.plotly_chart(fig_top, use_container_width=True)
