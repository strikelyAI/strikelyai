import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from PIL import Image
import os

# ================================
# CONFIG
# ================================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# ================================
# ESTILO PREMIUM APP
# ================================
st.markdown("""
<style>
body { background-color: #ffffff; }

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}

div.stButton > button {
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    font-weight: 700;
    border-radius: 12px;
    background-color: #0f172a;
    color: white;
    border: none;
}

div.stButton > button:hover {
    background-color: #1e293b;
}

h2, h3 {
    font-weight: 800;
    letter-spacing: 0.5px;
}
</style>

<meta name="theme-color" content="#0f172a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
""", unsafe_allow_html=True)

# ================================
# LOGO
# ================================
if os.path.exists("assets/logo.png"):
    logo = Image.open("assets/logo.png")
    st.image(logo, width=220)

st.title("STRIKELYAI")

# ================================
# CARGA DATOS
# ================================
DATA_PATH = "datos/europeo.csv"

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    columnas_necesarias = ["HomeTeam","AwayTeam","FTHG","FTAG"]
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"Falta columna {col} en el CSV")
    return df

df = cargar_datos(DATA_PATH)

# ================================
# MAPA LIGAS
# ================================
MAPA_LIGAS = {
    "E0":"Premier League",
    "SP1":"La Liga",
    "D1":"Bundesliga",
    "I1":"Serie A",
    "F1":"Ligue 1",
    "P1":"Primeira Liga",
    "N1":"Eredivisie",
    "B1":"Belgian Pro League",
    "SC0":"Scottish Premiership",
    "T1":"Turkish Super Lig",
    "G1":"Greek Super League"
}

if "Div" in df.columns:
    df["LIGA_NOMBRE"] = df["Div"].map(MAPA_LIGAS).fillna(df["Div"])
else:
    df["LIGA_NOMBRE"] = "Liga"

ligas = sorted(df["LIGA_NOMBRE"].unique())

# ================================
# SELECTOR LIGA
# ================================
st.markdown('<div class="card">', unsafe_allow_html=True)
liga = st.selectbox("🏆 LIGA", ligas, key="liga_selector")
df_liga = df[df["LIGA_NOMBRE"] == liga]
st.markdown('</div>', unsafe_allow_html=True)

# ================================
# SELECTOR EQUIPOS
# ================================
st.markdown('<div class="card">', unsafe_allow_html=True)

local = st.selectbox(
    "🏠 EQUIPO LOCAL",
    sorted(df_liga["HomeTeam"].unique()),
    key="local_selector"
)

visitante = st.selectbox(
    "✈️ EQUIPO VISITANTE",
    sorted(df_liga["AwayTeam"].unique()),
    key="visitante_selector"
)

st.markdown('</div>', unsafe_allow_html=True)

# ================================
# CUOTAS
# ================================
st.markdown('<div class="card">', unsafe_allow_html=True)

cuota_local = st.text_input("Cuota Local")
cuota_empate = st.text_input("Cuota Empate")
cuota_visitante = st.text_input("Cuota Visitante")

st.markdown('</div>', unsafe_allow_html=True)

# ================================
# FUNCIONES MODELO
# ================================
def calcular_poisson(df, equipo):
    goles_favor = df[df["HomeTeam"] == equipo]["FTHG"].mean()
    goles_contra = df[df["AwayTeam"] == equipo]["FTAG"].mean()
    return goles_favor, goles_contra

def calcular_probabilidades(df, local, visitante):
    gf_local, gc_local = calcular_poisson(df, local)
    gf_visit, gc_visit = calcular_poisson(df, visitante)

    lambda_local = (gf_local + gc_visit) / 2
    lambda_visit = (gf_visit + gc_local) / 2

    prob_local = 0
    prob_empate = 0
    prob_visit = 0

    for i in range(6):
        for j in range(6):
            p = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visit)
            if i > j:
                prob_local += p
            elif i == j:
                prob_empate += p
            else:
                prob_visit += p

    total = prob_local + prob_empate + prob_visit
    return prob_local/total, prob_empate/total, prob_visit/total

def value(prob, cuota):
    if cuota == "":
        return None
    cuota = float(cuota.replace(",","."))
    justa = 1/prob
    return cuota > justa, justa

# ================================
# ANALIZAR
# ================================
if st.button("ANALIZAR PARTIDO"):

    if local == visitante:
        st.error("Selecciona equipos distintos")
    else:
        p_local, p_empate, p_visit = calcular_probabilidades(df_liga, local, visitante)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 PROBABILIDADES")
        st.write(f"Local: {p_local*100:.2f}%")
        st.write(f"Empate: {p_empate*100:.2f}%")
        st.write(f"Visitante: {p_visit*100:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💰 VALUE")

        v_local = value(p_local, cuota_local)
        v_empate = value(p_empate, cuota_empate)
        v_visit = value(p_visit, cuota_visitante)

        if v_local:
            st.write(f"Local → {'🔥 VALUE' if v_local[0] else '❌ NO VALUE'} (Justa {v_local[1]:.2f})")
        if v_empate:
            st.write(f"Empate → {'🔥 VALUE' if v_empate[0] else '❌ NO VALUE'} (Justa {v_empate[1]:.2f})")
        if v_visit:
            st.write(f"Visitante → {'🔥 VALUE' if v_visit[0] else '❌ NO VALUE'} (Justa {v_visit[1]:.2f})")

        st.markdown('</div>', unsafe_allow_html=True)

# ================================
# AVISO LEGAL
# ================================
st.markdown("---")
st.caption("⚠️ Aviso: StrikelyAI ofrece análisis estadístico. No garantiza resultados ni promueve apuestas irresponsables.")
