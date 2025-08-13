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

st.markdown("""
**Quelle:** FIEC-Statistik 2024/2025 – 2024 Rückgang um −4,4 %, 2025 leichte Erholung (+0,4 %).
""")

# ==============================
# GOOGLE TRENDS
# ==============================
st.header("🔍 Google Suchtrends (Österreich) – Möbelix, Mömax, Küchenplanung")

# Init Pytrends
pytrends = TrendReq(hl='de-AT', tz=360)

# Keywords definieren
keywords = ["Möbelix", "Mömax", "Küchenplanung"]

# Daten abrufen (letzte 12 Monate, Österreich)
pytrends.build_payload(keywords, cat=0, timeframe='today 12-m', geo='AT', gprop='')
data = pytrends.interest_over_time()

if not data.empty:
    data = data.drop(columns=["isPartial"])
    st.line_chart(data)
else:
    st.error("Keine Google-Trends-Daten gefunden. Eventuell API-Limit erreicht.")

# ==============================
# TRENDS DETAIL
# ==============================
st.subheader("📅 Durchschnittliches Suchinteresse (12 Monate)")
if not data.empty:
    avg_interest = data.mean().reset_index()
    avg_interest.columns = ["Keyword", "Ø Suchinteresse"]
    st.table(avg_interest.sort_values("Ø Suchinteresse", ascending=False))
