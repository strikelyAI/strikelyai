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
# ESTILOS
# =========================
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.stSelectbox label, .stTextInput label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO
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
# DETECTAR COLUMNA DE LIGA
# =========================
def detectar_columna_liga(df):
    for col in ["League", "Div", "competition", "Comp", "Liga"]:
        if col in df.columns:
            return col
    return None

col_liga = detectar_columna_liga(df)

if col_liga is None:
    st.error("❌ No se pudo detectar la columna de liga.")
    st.write(df.columns.tolist())
    st.stop()

# =========================
# MAPA DE LIGAS (UX)
# =========================
MAPA_LIGAS = {
    "E0": "Premier League (Inglaterra)",
    "E1": "Championship (Inglaterra)",
    "E2": "League One (Inglaterra)",
    "E3": "League Two (Inglaterra)",
    "EC": "Conference League (Inglaterra)",
    "SP1": "LaLiga (España)",
    "SP2": "LaLiga Hypermotion (España)",
    "D1": "Bundesliga (Alemania)",
    "D2": "2. Bundesliga (Alemania)",
    "I1": "Serie A (Italia)",
    "I2": "Serie B (Italia)",
    "F1": "Ligue 1 (Francia)",
    "F2": "Ligue 2 (Francia)",
    "SC0": "Scottish Premiership",
    "SC1": "Scottish Championship",
    "SC2": "Scottish League One",
    "SC3": "Scottish League Two",
    "N1": "Eredivisie (Países Bajos)",
    "B1": "Jupiler Pro League (Bélgica)",
    "P1": "Primeira Liga (Portugal)",
    "T1": "Süper Lig (Turquía)",
    "G1": "Super League (Grecia)"
}

ligas_codigo = sorted(df[col_liga].dropna().unique())

ligas_legibles = {
    MAPA_LIGAS.get(cod, cod): cod
    for cod in ligas_codigo
}

liga_mostrada = st.selectbox(
    "🏆 Selecciona la liga",
    list(ligas_legibles.keys())
)

liga_seleccionada = ligas_legibles[liga_mostrada]
df_liga = df[df[col_liga] == liga_seleccionada]

# =========================
# SELECTOR DE EQUIPOS
# =========================
equipos = sorted(
    pd.concat([df_liga["HomeTeam"], df_liga["AwayTeam"]]).dropna().unique()
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
# MODELO BASE (FORMA + GOLES)
# =========================
def calcular_probabilidades(df, local, visitante):
    home = df[df["HomeTeam"] == local].tail(20)
    away = df[df["AwayTeam"] == visitante].tail(20)

    if len(home) < 5 or len(away) < 5:
        return 0.45, 0.25, 0.30

    g_local = home["FTHG"].mean()
    g_visit = away["FTAG"].mean()

    total = g_local + g_visit
    if total == 0:
        return 0.45, 0.25, 0.30

    p_local = g_local / total
    p_visit = g_visit / total
    p_emp = max(0.15, 1 - p_local - p_visit)

    s = p_local + p_emp + p_visit
    return p_local/s, p_emp/s, p_visit/s

# =========================
# BOTÓN PRINCIPAL
# =========================
if st.button("⚽ Analizar partido", use_container_width=True):

    p_local, p_emp, p_visit = calcular_probabilidades(
        df_liga, equipo_local, equipo_visitante
    )

    st.subheader("📊 Probabilidades 1X2")
    st.write(f"🏠 Local: **{p_local*100:.2f}%**")
    st.write(f"➖ Empate: **{p_emp*100:.2f}%**")
    st.write(f"✈️ Visitante: **{p_visit*100:.2f}%**")

    # =========================
    # VALUE BET
    # =========================
    st.subheader("🔥 Value Bet")

    def value(prob, cuota):
        if prob <= 0 or cuota is None:
            return None
        justa = 1 / prob
        return cuota > justa, justa

    opciones = [
        ("Local", p_local, cuota_local),
        ("Empate", p_emp, cuota_empate),
        ("Visitante", p_visit, cuota_visitante)
    ]

    values = []
    for nombre, prob, cuota in opciones:
        res = value(prob, cuota)
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
