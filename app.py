import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --- CONFIG ---
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# --- FUNKTIONEN ---
@st.cache_data
def load_data(filename):
    path = CACHE_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    else:
        st.warning(f"{filename} nicht gefunden. Bitte CSV-Datei erstellen.")
        return pd.DataFrame()

def plot_trend(df, column="Suchvolumen", title="Trend"):
    if df.empty:
        st.info("Keine Daten zum Anzeigen")
        return
    plt.figure(figsize=(10,5))
    plt.plot(pd.to_datetime(df['Datum']), df[column], marker='o')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt)

# --- DASHBOARD ---
st.title("Küchen & Möbel Markt Dashboard Österreich")

# 1️⃣ Keywords Übersicht
st.header("Suchvolumen Übersicht")
keywords = ["Möbelix", "Mömax", "Küchenplanung"]
for kw in keywords:
    df_kw = load_data(f"{kw}_monatlich.csv")
    st.subheader(f"{kw} (monatlich)")
    plot_trend(df_kw, column="Suchvolumen", title=f"{kw} Trend")

# 2️⃣ Küchenarten
st.header("Beliebte Küchenarten")
df_kuechen = load_data("kuechenarten.csv")
if not df_kuechen.empty:
    st.bar_chart(df_kuechen.set_index("Küchenart")["Suchvolumen"])

# 3️⃣ Bundesländer Analyse
st.header("Suchvolumen nach Bundesland")
df_bundesland = load_data("bundeslaender.csv")
if not df_bundesland.empty:
    st.bar_chart(df_bundesland.set_index("Bundesland")["Suchvolumen"])

# 4️⃣ Küchengeräte & Hersteller
st.header("Top Küchengeräte & Hersteller")
df_geraete = load_data("kuechengeraete.csv")
df_hersteller = load_data("hersteller.csv")
if not df_geraete.empty:
    st.subheader("Küchengeräte")
    st.bar_chart(df_geraete.set_index("Marke")["Suchvolumen"])
if not df_hersteller.empty:
    st.subheader("Hersteller")
    st.bar_chart(df_hersteller.set_index("Marke")["Suchvolumen"])

# 5️⃣ Meistgekaufte Marken online
st.header("Meistgekaufte Küchenmarken online")
df_online = load_data("online_marken.csv")
if not df_online.empty:
    st.bar_chart(df_online.set_index("Marke")["Käufe"])
