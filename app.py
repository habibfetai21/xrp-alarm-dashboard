import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from pytrends.request import TrendReq
import time

st.title("Küchen & Möbel Markt Dashboard Österreich")

# --- Ordner für CSV-Dateien ---
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# --- Google Trends Setup ---
pytrends = TrendReq(hl='de-AT', tz=360)

def fetch_trends(keyword, timeframe='today 12-m', geo='AT'):
    """Ruft Google Trends-Daten ab, speichert als CSV"""
    path = CACHE_DIR / f"{keyword}_monatlich.csv"
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo)
        data = pytrends.interest_over_time()
        if not data.empty:
            data = data.drop(columns=['isPartial'])
            data.to_csv(path)
            return data
        else:
            return pd.DataFrame({"Datum": [], "Suchvolumen": []})
    except Exception as e:
        st.warning(f"Fehler bei {keyword}: {e}")
        # Falls Fehler, CSV mit Dummy-Daten erzeugen
        dummy = pd.DataFrame({
            "Datum": pd.date_range("2025-01-01", periods=12, freq='M').strftime('%Y-%m'),
            "Suchvolumen": [100]*12
        })
        dummy.to_csv(path, index=False)
        return dummy

# --- Keywords ---
keywords_monthly = ["Möbelix", "Mömax", "Küchenplanung"]

# --- Monatliche Trends laden ---
st.header("Suchvolumen Übersicht")
for kw in keywords_monthly:
    df = fetch_trends(kw)
    st.subheader(f"{kw} (monatlich)")
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(df.index, df.iloc[:,0], marker='o')
        ax.set_xlabel("Monat")
        ax.set_ylabel("Suchvolumen")
        ax.set_xticklabels(df.index.strftime('%Y-%m'), rotation=45)
        st.pyplot(fig)
    else:
        st.write("Keine Daten verfügbar")

# --- Beliebte Küchenarten ---
st.header("Beliebte Küchenarten")
kuechenarten_file = CACHE_DIR / "kuechenarten.csv"
if not kuechenarten_file.exists():
    df = pd.DataFrame({
        "Küchenart": ["Moderne Küche","Landhausküche","Designküche","Kompaktküche"],
        "Suchvolumen": [1500,1200,900,600]
    })
    df.to_csv(kuechenarten_file, index=False)
else:
    df = pd.read_csv(kuechenarten_file)
st.bar_chart(df.set_index("Küchenart"))

# --- Suchvolumen nach Bundesland ---
st.header("Suchvolumen nach Bundesland")
bundeslaender_file = CACHE_DIR / "bundeslaender.csv"
if not bundeslaender_file.exists():
    df = pd.DataFrame({
        "Bundesland": ["Wien","Niederösterreich","Oberösterreich","Steiermark","Salzburg","Tirol","Vorarlberg","Kärnten","Burgenland"],
        "Suchvolumen": [2000,1500,1300,1100,900,800,700,600,500]
    })
    df.to_csv(bundeslaender_file, index=False)
else:
    df = pd.read_csv(bundeslaender_file)
st.bar_chart(df.set_index("Bundesland"))

# --- Küchengeräte & Hersteller ---
st.header("Top Küchengeräte & Hersteller")

# Küchengeräte
kuechengeraete_file = CACHE_DIR / "kuechengeraete.csv"
if not kuechengeraete_file.exists():
    df = pd.DataFrame({
        "Marke": ["Bosch","Siemens","AEG","Miele","Samsung"],
        "Suchvolumen": [1200,1100,900,800,700]
    })
    df.to_csv(kuechengeraete_file, index=False)
else:
    df = pd.read_csv(kuechengeraete_file)
st.subheader("Küchengeräte")
st.bar_chart(df.set_index("Marke"))

# Hersteller
hersteller_file = CACHE_DIR / "hersteller.csv"
if not hersteller_file.exists():
    df = pd.DataFrame({
        "Marke": ["Nobilia","Häcker","Leicht","Poggenpohl"],
        "Suchvolumen": [1500,1300,900,600]
    })
    df.to_csv(hersteller_file, index=False)
else:
    df = pd.read_csv(hersteller_file)
st.subheader("Hersteller")
st.bar_chart(df.set_index("Marke"))

# --- Meistgekaufte Küchenmarken online ---
st.header("Meistgekaufte Küchenmarken online")
online_file = CACHE_DIR / "online_marken.csv"
if not online_file.exists():
    df = pd.DataFrame({
        "Marke": ["Nobilia","Häcker","Leicht","Poggenpohl"],
        "Käufe": [500,400,300,200]
    })
    df.to_csv(online_file, index=False)
else:
    df = pd.read_csv(online_file)
st.bar_chart(df.set_index("Marke"))
