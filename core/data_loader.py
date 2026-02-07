import pandas as pd
import streamlit as st

@st.cache_data
def cargar_csv(ruta):
    return pd.read_csv(ruta)
