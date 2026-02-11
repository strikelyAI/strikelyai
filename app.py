import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import plotly.graph_objects as go
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# =========================
# DARK MODE TOGGLE
# =========================
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    bg = "#0f172a"
    card_bg = "#1e293b"
    text_color = "white"
else:
    bg = "#ffffff"
    card_bg = "#f8fafc"
    text_color = "#0f172a"

st.markdown(f"""
<style>
body {{ background-color: {bg}; color: {text_color}; }}

.block-container {{
    padding-top: 1.5rem;
}}

.card {{
    background: {card_bg};
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}}

div.stButton > button {{
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    font-weight: 700;
    border-radius: 12px;
    background-color: #0f172a;
    color: white;
    border: none;
}}

h2, h3 {{
    font-weight: 800;
}}
</style>
""", unsafe_allow_html=True)

st.title("⚽ STRIKELYAI")

# =========================
# DATA
# =========================
DATA_PATH = "datos/europeo.csv"

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    required = ["HomeTeam","AwayTeam","FTHG","FTAG"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Falta columna {col}")
    return df

df = cargar_datos(DATA_PATH)

# =========================
# MAPA LIGAS
# =========================
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

# =========================
# SELECTORES
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

liga = st.selectbox("🏆 LIGA", ligas)
df_liga = df[df["LIGA_NOMBRE"] == liga]

local = st.selectbox("🏠 EQUIPO LOCAL", sorted(df_liga["HomeTeam"].unique()))
visitante = st.selectbox("✈️ EQUIPO VISITANTE", sorted(df_liga["AwayTeam"].unique()))

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CUOTAS
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

cuota_local = st.text_input("Cuota Local")
cuota_empate = st.text_input("Cuota Empate")
cuota_visitante = st.text_input("Cuota Visitante")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MODELO POISSON
# =========================
def medias_equipo(df, equipo):
    gf = df[df["HomeTeam"] == equipo]["FTHG"].mean()
    gc = df[df["AwayTeam"] == equipo]["FTAG"].mean()
    return gf, gc

def probabilidades(df, local, visitante):
    gf_l, gc_l = medias_equipo(df, local)
    gf_v, gc_v = medias_equipo(df, visitante)

    lambda_l = (gf_l + gc_v)/2
    lambda_v = (gf_v + gc_l)/2

    p_l = p_e = p_v = 0

    for i in range(6):
        for j in range(6):
            p = poisson.pmf(i, lambda_l)*poisson.pmf(j, lambda_v)
            if i>j: p_l+=p
            elif i==j: p_e+=p
            else: p_v+=p

    total = p_l+p_e+p_v
    return p_l/total, p_e/total, p_v/total

def calcular_value(prob, cuota):
    if cuota == "":
        return None
    cuota = float(cuota.replace(",","."))
    justa = 1/prob
    return cuota>justa, justa

# =========================
# ANALIZAR
# =========================
if st.button("ANALIZAR PARTIDO"):

    if local == visitante:
        st.error("Selecciona equipos distintos")
    else:
        p_l, p_e, p_v = probabilidades(df_liga, local, visitante)

        # -------- PROBABILIDADES
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 PROBABILIDADES")

        st.progress(int(max(p_l,p_e,p_v)*100))

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Local","Empate","Visitante"],
            y=[p_l*100,p_e*100,p_v*100]
        ))
        fig.update_layout(
            template="plotly_dark" if dark_mode else "plotly_white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        st.write(f"Local: {p_l*100:.2f}%")
        st.write(f"Empate: {p_e*100:.2f}%")
        st.write(f"Visitante: {p_v*100:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)

        # -------- VALUE
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💰 VALUE")

        v_l = calcular_value(p_l, cuota_local)
        v_e = calcular_value(p_e, cuota_empate)
        v_v = calcular_value(p_v, cuota_visitante)

        mejores = []

        if v_l and v_l[0]:
            mejores.append(("Local", cuota_local, v_l[1]))
        if v_e and v_e[0]:
            mejores.append(("Empate", cuota_empate, v_e[1]))
        if v_v and v_v[0]:
            mejores.append(("Visitante", cuota_visitante, v_v[1]))

        if mejores:
            st.success(f"🔥 Mejor opción: {mejores[0][0]} (Cuota {mejores[0][1]} · Justa {mejores[0][2]:.2f})")
        else:
            st.info("No se detecta value claro.")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# AVISO LEGAL
# =========================
st.markdown("---")
st.caption("⚠️ StrikelyAI ofrece análisis estadístico basado en datos históricos. No garantiza resultados ni promueve apuestas irresponsables.")
