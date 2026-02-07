# =========================
# StrikelyAI — app.py
# =========================

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# =========================
# ESTILOS BÁSICOS
# =========================
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stSelectbox label, .stTextInput label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO + HEADER
# =========================
logo = Image.open("assets/logo.png")
st.image(logo, width=180)
st.title("StrikelyAI")
st.caption("Análisis inteligente de probabilidades de fútbol europeo")

st.divider()

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos/europeo.csv")

df = cargar_datos()

# =========================
# DETECCIÓN AUTOMÁTICA DE LIGA
# =========================
def detectar_columna_liga(df):
    posibles = ["League", "Div", "competition", "Comp", "Liga"]
    for col in posibles:
        if col in df.columns:
            return col
    return None

col_liga = detectar_columna_liga(df)

if col_liga is None:
    st.error("❌ No se ha podido detectar la columna de liga en el dataset.")
    st.write("Columnas disponibles:", df.columns.tolist())
    st.stop()

# =========================
# SELECTOR DE LIGA
# =========================
ligas = sorted(df[col_liga].dropna().unique())
liga_seleccionada = st.selectbox("🏆 Selecciona la liga", ligas)

df_liga = df[df[col_liga] == liga_seleccionada]

# =========================
# SELECTOR DE EQUIPOS
# =========================
equipos = sorted(
    pd.concat([df_liga["HomeTeam"], df_liga["AwayTeam"]]).unique()
)

col1, col2 = st.columns(2)

with col1:
    equipo_local = st.selectbox("🏠 Equipo local", equipos)

with col2:
    equipo_visitante = st.selectbox(
        "✈️ Equipo visitante",
        [e for e in equipos if e != equipo_local]
    )

st.divider()

# =========================
# CUOTAS (OPCIONALES)
# =========================
st.subheader("💰 Cuotas (opcional)")

c1, c2, c3 = st.columns(3)

with c1:
    cuota_local = st.text_input("Local", placeholder="1.85")

with c2:
    cuota_empate = st.text_input("Empate", placeholder="3.40")

with c3:
    cuota_visitante = st.text_input("Visitante", placeholder="4.20")

def parse_cuota(x):
    if not x:
        return None
    try:
        return float(x.replace(",", "."))
    except:
        return None

cuota_local = parse_cuota(cuota_local)
cuota_empate = parse_cuota(cuota_empate)
cuota_visitante = parse_cuota(cuota_visitante)

# =========================
# MODELO SIMPLE (BASE)
# =========================
def calcular_probabilidades(df, local, visitante):
    partidos_local = df[df["HomeTeam"] == local].tail(20)
    partidos_visitante = df[df["AwayTeam"] == visitante].tail(20)

    if len(partidos_local) < 5 or len(partidos_visitante) < 5:
        return 0.45, 0.25, 0.30

    goles_local = partidos_local["FTHG"].mean()
    goles_visitante = partidos_visitante["FTAG"].mean()

    total = goles_local + goles_visitante
    if total == 0:
        return 0.45, 0.25, 0.30

    prob_local = goles_local / total
    prob_visitante = goles_visitante / total
    prob_empate = max(0.15, 1 - prob_local - prob_visitante)

    # Normalización
    s = prob_local + prob_empate + prob_visitante
    return prob_local/s, prob_empate/s, prob_visitante/s

# =========================
# BOTÓN PRINCIPAL
# =========================
if st.button("⚽ Analizar partido", use_container_width=True):

    p_local, p_empate, p_visitante = calcular_probabilidades(
        df_liga, equipo_local, equipo_visitante
    )

    st.subheader("📊 Probabilidades 1X2")
    st.write(f"🏠 Local: **{p_local*100:.2f}%**")
    st.write(f"➖ Empate: **{p_empate*100:.2f}%**")
    st.write(f"✈️ Visitante: **{p_visitante*100:.2f}%**")

    # =========================
    # VALUE BET
    # =========================
    st.subheader("🔥 Value Bet")

    def evaluar_value(prob, cuota):
        if prob <= 0 or cuota is None:
            return None
        cuota_justa = 1 / prob
        return cuota > cuota_justa, cuota_justa

    opciones = [
        ("Local", p_local, cuota_local),
        ("Empate", p_empate, cuota_empate),
        ("Visitante", p_visitante, cuota_visitante)
    ]

    values = []

    for nombre, prob, cuota in opciones:
        res = evaluar_value(prob, cuota)
        if res:
            es_value, justa = res
            if es_value:
                values.append((nombre, cuota, justa))

    if values:
        mejor = max(values, key=lambda x: x[1] - x[2])
        st.success(
            f"✅ Mejor opción: **{mejor[0]}** "
            f"(Cuota {mejor[1]:.2f} · Justa {mejor[2]:.2f})"
        )
    else:
        st.info("ℹ️ No se detecta value claro con las cuotas introducidas.")

# =========================
# AVISO
# =========================
st.divider()
st.caption(
    "⚠️ StrikelyAI es una herramienta de análisis estadístico. "
    "No garantiza resultados ni sustituye el criterio del usuario."
)
