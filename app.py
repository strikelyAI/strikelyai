import streamlit as st
import pandas as pd
from PIL import Image
import math

# =======================
# CONFIGURACIÓN PÁGINA
# =======================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# =======================
# LOGO
# =======================
logo = Image.open("assets/logo.png")
st.image(logo, width=180)
st.title("StrikelyAI")
st.caption("IA de probabilidad y value betting · Fútbol europeo")

st.markdown("---")

# =======================
# CARGA DE DATOS
# =======================
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos/europeo.csv")

df = cargar_datos()

# =======================
# DETECCIÓN COLUMNAS
# =======================
def detectar_columna(posibles):
    for c in posibles:
        if c in df.columns:
            return c
    return None

col_liga = detectar_columna(["Div", "League", "division"])
col_local = detectar_columna(["HomeTeam", "home_team"])
col_visitante = detectar_columna(["AwayTeam", "away_team"])
col_goles_local = detectar_columna(["FTHG", "home_goals"])
col_goles_visitante = detectar_columna(["FTAG", "away_goals"])
col_fecha = detectar_columna(["Date", "date"])

if not all([col_liga, col_local, col_visitante]):
    st.error("❌ El CSV no tiene columnas mínimas requeridas")
    st.stop()

# =======================
# MAPA DEFINITIVO DE LIGAS
# =======================
MAPA_LIGAS = {
    "E0": "Premier League",
    "E1": "Championship",
    "E2": "League One",
    "E3": "League Two",

    "SP1": "LaLiga",
    "SP2": "LaLiga Hypermotion",

    "D1": "Bundesliga",
    "D2": "2. Bundesliga",

    "I1": "Serie A",
    "I2": "Serie B",

    "F1": "Ligue 1",
    "F2": "Ligue 2",

    "N1": "Eredivisie",
    "P1": "Primeira Liga",
    "B1": "Jupiler Pro League",
    "T1": "Süper Lig",
    "G1": "Super League Grecia",
    "SC0": "Scottish Premiership",

    "EC": "Champions League"
}

# =======================
# SELECTOR DE LIGA LIMPIO
# =======================
ligas_cod = sorted(df[col_liga].dropna().unique())

ligas_ui = {
    MAPA_LIGAS[c]: c
    for c in ligas_cod
    if c in MAPA_LIGAS
}

if not ligas_ui:
    st.error("❌ No se encontraron ligas válidas")
    st.stop()

liga_ui = st.selectbox("🏆 Liga", list(ligas_ui.keys()))
liga = ligas_ui[liga_ui]

df_liga = df[df[col_liga] == liga]

# =======================
# SELECTORES DE EQUIPOS
# =======================
equipos = sorted(
    set(df_liga[col_local].unique())
    | set(df_liga[col_visitante].unique())
)

equipo_local = st.selectbox("🏠 Equipo local", equipos)
equipo_visitante = st.selectbox("✈️ Equipo visitante", equipos)

st.markdown("---")

# =======================
# INPUT CUOTAS
# =======================
st.subheader("💰 Cuotas (opcional)")

cuota_local = st.text_input("Cuota victoria local")
cuota_empate = st.text_input("Cuota empate")
cuota_visitante = st.text_input("Cuota victoria visitante")

def parse_cuota(x):
    try:
        return float(x.replace(",", "."))
    except:
        return None

cuota_local = parse_cuota(cuota_local)
cuota_empate = parse_cuota(cuota_empate)
cuota_visitante = parse_cuota(cuota_visitante)

# =======================
# FUNCIÓN POISSON SIMPLE
# =======================
def media_goles(equipo, es_local=True):
    if es_local:
        goles = df_liga[df_liga[col_local] == equipo][col_goles_local]
    else:
        goles = df_liga[df_liga[col_visitante] == equipo][col_goles_visitante]
    return goles.mean()

def poisson_prob(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

# =======================
# BOTÓN PRINCIPAL
# =======================
if st.button("🔍 Analizar partido"):
    if equipo_local == equipo_visitante:
        st.warning("⚠️ Los equipos deben ser distintos")
        st.stop()

    lambda_local = media_goles(equipo_local, True)
    lambda_visitante = media_goles(equipo_visitante, False)

    prob_local = prob_empate = prob_visitante = 0

    for i in range(6):
        for j in range(6):
            p = poisson_prob(lambda_local, i) * poisson_prob(lambda_visitante, j)
            if i > j:
                prob_local += p
            elif i == j:
                prob_empate += p
            else:
                prob_visitante += p

    total = prob_local + prob_empate + prob_visitante
    prob_local /= total
    prob_empate /= total
    prob_visitante /= total

    st.subheader("📊 Probabilidades 1X2")
    st.write(f"🏠 Local: **{prob_local*100:.2f}%**")
    st.write(f"➖ Empate: **{prob_empate*100:.2f}%**")
    st.write(f"✈️ Visitante: **{prob_visitante*100:.2f}%**")

    # =======================
    # VALUE BET
    # =======================
    st.subheader("🔥 Value Bet")

    def evaluar(prob, cuota):
        if cuota is None or prob <= 0:
            return None
        justa = 1 / prob
        return cuota > justa, justa

    for nombre, prob, cuota in [
        ("Local", prob_local, cuota_local),
        ("Empate", prob_empate, cuota_empate),
        ("Visitante", prob_visitante, cuota_visitante),
    ]:
        res = evaluar(prob, cuota)
        if res:
            es_value, justa = res
            st.write(
                f"{nombre}: cuota justa {justa:.2f} → "
                f"{'🔥 VALUE' if es_value else '❌ Sin value'}"
            )

    st.markdown("---")
    st.caption("ℹ️ Análisis informativo. No constituye recomendación de apuesta.")
