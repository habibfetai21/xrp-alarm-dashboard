# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Österreich Markt & Trends", layout="wide")
st.title("📊 Dashboard: Zinsen, Baubranche & Google-Suchtrends in Österreich")

# ==============================
# BANKEN & ZINSEN
# ==============================
st.header("🏦 Banken & Zinslage (Stand: August 2025)")
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
# BAUBRANCHE MARKTENTWICKLUNG
# ==============================
st.header("🏗 Baubranche – Marktentwicklung Österreich")
df_bau = pd.DataFrame({
    "Jahr": [2023, 2024, 2025],
    "Produktion Veränderung (%)": [None, -4.4, 0.4]
})
st.line_chart(df_bau.set_index("Jahr"))
st.markdown("**Quelle:** FIEC-Statistik 2024/2025 – 2024 Rückgang um −4,4 %, 2025 leichte Erholung (+0,4 %).")

# ==============================
# GOOGLE TRENDS – Grunddaten
# ==============================
st.header("🔍 Google Suchtrends (Österreich) – Möbelix, Mömax, Küchenplanung")
pytrends = TrendReq(hl='de-AT', tz=360)

keywords_main = ["Möbelix", "Mömax", "Küchenplanung"]
pytrends.build_payload(keywords_main, cat=0, timeframe='today 12-m', geo='AT', gprop='')
data_main = pytrends.interest_over_time()

if not data_main.empty:
    data_main = data_main.drop(columns=["isPartial"])
    st.line_chart(data_main)
    avg_interest = data_main.mean().reset_index()
    avg_interest.columns = ["Keyword", "Ø Suchinteresse"]
    st.subheader("📅 Durchschnittliches Suchinteresse (12 Monate)")
    st.table(avg_interest.sort_values("Ø Suchinteresse", ascending=False))
else:
    st.error("Keine Google-Trends-Daten gefunden. Eventuell API-Limit erreicht.")

# ==============================
# MONATLICHE TRENDS
# ==============================
st.header("📊 Monatliche Suchtrends")
if not data_main.empty:
    monthly_data = data_main.resample('M').mean()
    fig2, ax2 = plt.subplots(figsize=(10,5))
    for kw in keywords_main:
        ax2.plot(monthly_data.index, monthly_data[kw], marker='o', label=kw)
    ax2.set_ylabel("Suchinteresse")
    ax2.set_xlabel("Monat")
    ax2.set_title("Monatliches Suchinteresse")
    ax2.legend()
    st.pyplot(fig2)

# ==============================
# KÜCHENARTEN-ANALYSE
# ==============================
st.header("🍽 Beliebteste Küchenarten")
kitchen_types = ["Einbauküche", "Modulküche", "Landhausküche", "Designküche", "Systemküche"]
pytrends.build_payload(kitchen_types, cat=0, timeframe='today 12-m', geo='AT', gprop='')
data_kitchen = pytrends.interest_over_time().drop(columns=["isPartial"])
st.line_chart(data_kitchen)
avg_kitchen = data_kitchen.mean().reset_index()
avg_kitchen.columns = ["Küchenart", "Ø Suchinteresse"]
st.subheader("Ø Suchinteresse pro Küchenart (12 Monate)")
st.table(avg_kitchen.sort_values("Ø Suchinteresse", ascending=False))

# ==============================
# BUNDESLÄNDER-ANALYSE
# ==============================
st.header("🏢 Suchtrends nach Bundesland")
# Google Trends lässt uns mit `interest_by_region` die Daten nach Region holen
pytrends.build_payload(["Küchenplanung"], cat=0, timeframe='today 12-m', geo='AT', gprop='')
region_data = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
st.dataframe(region_data.sort_values(by="Küchenplanung", ascending=False))
fig3, ax3 = plt.subplots(figsize=(10,5))
ax3.bar(region_data.index, region_data["Küchenplanung"], color="#2196F3")
ax3.set_ylabel("Suchinteresse")
ax3.set_title("Suchinteresse nach Bundesland")
plt.xticks(rotation=45)
st.pyplot(fig3)
