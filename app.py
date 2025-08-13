import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --- Ordner für Cache/CSV-Dateien ---
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# --- Dummy-Daten erstellen, falls CSVs nicht existieren ---
dummy_files = {
    "Möbelix_monatlich.csv": {
        "Datum":["2025-01","2025-02","2025-03","2025-04","2025-05"],
        "Suchvolumen":[1200,1350,1500,1600,1550]
    },
    "Mömax_monatlich.csv": {
        "Datum":["2025-01","2025-02","2025-03","2025-04","2025-05"],
        "Suchvolumen":[900,950,1100,1200,1250]
    },
    "Küchenplanung_monatlich.csv": {
        "Datum":["2025-01","2025-02","2025-03","2025-04","2025-05"],
        "Suchvolumen":[2000,2100,2200,2300,2400]
    },
    "kuechenarten.csv": {
        "Küchenart":["Moderne Küche","Landhausküche","Designküche","Kompaktküche"],
        "Suchvolumen":[1500,1200,900,600]
    },
    "bundeslaender.csv": {
        "Bundesland":["Wien","Niederösterreich","Oberösterreich","Steiermark","Salzburg","Tirol","Vorarlberg","Kärnten","Burgenland"],
        "Suchvolumen":[2000,1500,1300,1100,900,800,700,600,500]
    },
    "kuechengeraete.csv": {
        "Marke":["Bosch","Siemens","AEG","Miele","Samsung"],
        "Suchvolumen":[1200,1100,900,800,700]
    },
    "hersteller.csv": {
        "Marke":["Nobilia","Häcker","Leicht","Poggenpohl"],
        "Suchvolumen":[1500,1300,900,600]
    },
    "online_marken.csv": {
        "Marke":["Nobilia","Häcker","Leicht","Poggenpohl"],
        "Käufe":[500,400,300,200]
    }
}

# Dateien anlegen, wenn sie noch nicht existieren
for filename, data in dummy_files.items():
    path = CACHE_DIR / filename
    if not path.exists():
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)

# --- Streamlit Dashboard ---
st.title("Küchenmarkt Dashboard Österreich")

st.header("1️⃣ Monatliches Suchvolumen")
def plot_monatlich(file, title):
    df = pd.read_csv(CACHE_DIR / file)
    st.subheader(title)
    fig, ax = plt.subplots()
    ax.plot(df['Datum'], df['Suchvolumen'], marker='o')
    ax.set_xlabel("Monat")
    ax.set_ylabel("Suchvolumen")
    ax.set_xticklabels(df['Datum'], rotation=45)
    st.pyplot(fig)

plot_monatlich("Möbelix_monatlich.csv", "Möbelix (monatlich)")
plot_monatlich("Mömax_monatlich.csv", "Mömax (monatlich)")
plot_monatlich("Küchenplanung_monatlich.csv", "Küchenplanung (monatlich)")

st.header("2️⃣ Beliebte Küchenarten")
df_kuechenarten = pd.read_csv(CACHE_DIR / "kuechenarten.csv")
fig, ax = plt.subplots()
ax.bar(df_kuechenarten['Küchenart'], df_kuechenarten['Suchvolumen'], color='skyblue')
ax.set_ylabel("Suchvolumen")
ax.set_xticklabels(df_kuechenarten['Küchenart'], rotation=45)
st.pyplot(fig)

st.header("3️⃣ Suchvolumen nach Bundesland")
df_bundeslaender = pd.read_csv(CACHE_DIR / "bundeslaender.csv")
fig, ax = plt.subplots()
ax.bar(df_bundeslaender['Bundesland'], df_bundeslaender['Suchvolumen'], color='orange')
ax.set_ylabel("Suchvolumen")
ax.set_xticklabels(df_bundeslaender['Bundesland'], rotation=45)
st.pyplot(fig)

st.header("4️⃣ Top Küchengeräte & Hersteller")
df_geraete = pd.read_csv(CACHE_DIR / "kuechengeraete.csv")
st.subheader("Küchengeräte")
fig, ax = plt.subplots()
ax.bar(df_geraete['Marke'], df_geraete['Suchvolumen'], color='green')
ax.set_ylabel("Suchvolumen")
ax.set_xticklabels(df_geraete['Marke'], rotation=45)
st.pyplot(fig)

df_hersteller = pd.read_csv(CACHE_DIR / "hersteller.csv")
st.subheader("Küchenhersteller")
fig, ax = plt.subplots()
ax.bar(df_hersteller['Marke'], df_hersteller['Suchvolumen'], color='purple')
ax.set_ylabel("Suchvolumen")
ax.set_xticklabels(df_hersteller['Marke'], rotation=45)
st.pyplot(fig)

st.header("5️⃣ Meistgekaufte Küchenmarken online")
df_online = pd.read_csv(CACHE_DIR / "online_marken.csv")
fig, ax = plt.subplots()
ax.bar(df_online['Marke'], df_online['Käufe'], color='red')
ax.set_ylabel("Anzahl Käufe")
ax.set_xticklabels(df_online['Marke'], rotation=45)
st.pyplot(fig)
