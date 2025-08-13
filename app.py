# dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Dashboard: Baubranche & Suchinteresse Österreich")

# 1. Zinssatz-Modul (Platzhalterdaten)
st.header("Banken & Zinssätze")
df_zinsen = pd.DataFrame({
    "Kategorie": ["EURIBOR (3M)", "Variable Bauzinsen", "Fixzinsen (25 J.)"],
    "Zinssatz (%)": [1.99, 3.24, 3.35]  # Platzhalter (Stand: circa 2025) 
})
st.table(df_zinsen)

# 2. Baubranche-Marktentwicklung (Platzhalter)
st.header("Baubranche Marktentwicklung (Österreich)")
df_bau = pd.DataFrame({
    "Jahr": [2023, 2024, 2025],
    "Produktion Veränderung (%)": [None, -4.4, 0.4]  # FIEC-Daten
})
st.line_chart(df_bau.set_index("Jahr"))

# 3. Google-Suchvolumen (Platzhalter)
st.header("Google-Suchvolumen (Österreich)")

df_search = pd.DataFrame({
    "Keyword": ["Möbelix", "Mömax", "Küchenplanung"],
    "Schätz-Suchanfragen/Monat": [None, None, None]  # Platzhalter
})
st.bar_chart(df_search.set_index("Keyword"))

# 4. Interaktive Filter (Demo)
st.sidebar.header("Filter & Optionen")
kw = st.sidebar.multiselect("Wähle Keywords aus:", df_search["Keyword"].tolist(), default=["Möbelix", "Mömax"])
st.write(f"Aktuell ausgewählte Keywords: {', '.join(kw)}")

# 5. Quellen und Fußnoten
st.write("""
**Hinweise & Quellen:**  
- Zinssätze: EURIBOR, variable & fixe Baukreditzinsen (z. B. durchblicker, Infina)  
- Baubranche: FIEC-Statistik (-4,4 % in 2024, leichte Erholung +0,4 % in 2025)  
- Suchvolumen: Platzhalter – genaue Daten über Google Ads Keyword Planner oder SEO-Tools  
""")
