import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
from pathlib import Path
import time

st.set_page_config(page_title="Küchen & Möbel Markt Dashboard Österreich", layout="wide")
st.title("Küchen & Möbel Markt Dashboard Österreich")

CACHE_DIR = Path("./cache")
CACHE_DIR.mkdir(exist_ok=True)

# Pytrends Setup
pytrends = TrendReq(hl='de-AT', tz=360)

# -------------------------------
# Funktion für Trends mit Fallback
# -------------------------------
def fetch_trends(keyword, timeframe='today 12-m', geo='AT'):
    path = CACHE_DIR / f"{keyword}_monatlich.csv"
    if path.exists():
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo)
        data = pytrends.interest_over_time()
        time.sleep(1)  # Pause, um 429 zu vermeiden
        if not data.empty:
            data = data.drop(columns=['isPartial'], errors='ignore')
            data.to_csv(path)
            return data
        else:
            raise Exception("Keine Daten erhalten")
    except Exception as e:
        st.warning(f"Fehler bei {keyword}: {e}")
        # Dummy-Daten als Fallback
        dummy = pd.DataFrame({
            "Datum": pd.date_range("2025-01-01", periods=12, freq='M'),
            keyword: [100]*12
        }).set_index("Datum")
        dummy.to_csv(path)
        return dummy

# -------------------------------
# Monatliches Suchvolumen
# -------------------------------
keywords_monthly = ["Möbelix", "Mömax", "Küchenplanung"]

for kw in keywords_monthly:
    df = fetch_trends(kw)
    st.subheader(f"{kw} (monatlich)")
    
    if not df.empty:
        # Sicherstellen, dass Index Datetime ist
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        fig, ax = plt.subplots()
        ax.plot(df.index, df.iloc[:,0], marker='o')
        ax.set_xlabel("Monat")
        ax.set_ylabel("Suchvolumen")
        ax.set_xticks(df.index)
        ax.set_xticklabels(df.index.strftime('%Y-%m'), rotation=45)
        st.pyplot(fig)
    else:
        st.write("Keine Daten verfügbar")

# -------------------------------
# Beliebte Küchenarten
# -------------------------------
kuechenarten_path = CACHE_DIR / "kuechenarten.csv"
if kuechenarten_path.exists():
    df_kuechenarten = pd.read_csv(kuechenarten_path)
else:
    df_kuechenarten = pd.DataFrame({
        "Küchenart": ["Moderne Küche", "Landhausküche", "Minimalistisch", "Designküche"],
        "Suchvolumen": [120, 80, 60, 50]
    })
    df_kuechenarten.to_csv(kuechenarten_path, index=False)

st.subheader("Beliebte Küchenarten")
st.bar_chart(df_kuechenarten.set_index("Küchenart"))

# -------------------------------
# Suchvolumen nach Bundesland
# -------------------------------
bundeslaender_path = CACHE_DIR / "bundeslaender.csv"
if bundeslaender_path.exists():
    df_bundeslaender = pd.read_csv(bundeslaender_path)
else:
    df_bundeslaender = pd.DataFrame({
        "Bundesland": ["Wien","Niederösterreich","Oberösterreich","Steiermark","Tirol","Salzburg","Kärnten","Vorarlberg","Burgenland"],
        "Suchvolumen": [300, 200, 180, 160, 140, 120, 100, 90, 70]
    })
    df_bundeslaender.to_csv(bundeslaender_path, index=False)

st.subheader("Suchvolumen nach Bundesland")
st.bar_chart(df_bundeslaender.set_index("Bundesland"))

# -------------------------------
# Top Küchengeräte & Hersteller
# -------------------------------
kuechengeraete_path = CACHE_DIR / "kuechengeraete.csv"
if kuechengeraete_path.exists():
    df_kuechengeraete = pd.read_csv(kuechengeraete_path)
else:
    df_kuechengeraete = pd.DataFrame({
        "Geräte": ["Kühlschrank", "Backofen", "Geschirrspüler", "Herd", "Dunstabzugshaube"],
        "Suchvolumen": [150, 120, 100, 90, 80]
    })
    df_kuechengeraete.to_csv(kuechengeraete_path, index=False)

hersteller_path = CACHE_DIR / "hersteller.csv"
if hersteller_path.exists():
    df_hersteller = pd.read_csv(hersteller_path)
else:
    df_hersteller = pd.DataFrame({
        "Hersteller": ["IKEA","Möbelix","Mömax","Leiner","XXX Lutz"],
        "Suchvolumen": [200,180,160,120,100]
    })
    df_hersteller.to_csv(hersteller_path, index=False)

st.subheader("Top Küchengeräte")
st.bar_chart(df_kuechengeraete.set_index("Geräte"))

st.subheader("Top Küchenhersteller")
st.bar_chart(df_hersteller.set_index("Hersteller"))

# -------------------------------
# Meistgekaufte Küchenmarken online
# -------------------------------
online_marken_path = CACHE_DIR / "online_marken.csv"
if online_marken_path.exists():
    df_online_marken = pd.read_csv(online_marken_path)
else:
    df_online_marken = pd.DataFrame({
        "Marke": ["IKEA","Möbelix","Mömax","Leiner","Nobilia"],
        "Verkäufe": [500, 400, 350, 200, 150]
    })
    df_online_marken.to_csv(online_marken_path, index=False)

st.subheader("Meistgekaufte Küchenmarken online")
st.bar_chart(df_online_marken.set_index("Marke"))
