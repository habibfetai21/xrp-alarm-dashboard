import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.title("Test-Dashboard")

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
fig, ax = plt.subplots()
ax.plot(df["x"], df["y"])
st.pyplot(fig)
