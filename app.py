import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import poisson
from PIL import Image

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="wide"
)

# =========================
# RUTAS SEGURAS
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datos" / "europeo.csv"

# =========================
# LOGOS
# =========================
logo = Image.open(BASE_DIR / "assets" / "logo.png")
st.image(logo, width=150)
st.title("StrikelyAI")
st.caption("IA de predicción avanzada de fútbol europeo")

st.sidebar.image(logo, width=120)
st.sidebar.markdown("### ⚽ StrikelyAI")

st.sidebar.warning(
    "⚠️ App informativa. No garantiza resultados. Juego responsable."
)

# =========================
# MODO USUARIO
# =========================
modo = st.sidebar.radio(
    "Modo de acceso",
    ["FREE", "PRO"],
    captions=["Acceso limitado", "Acceso completo"]
)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos(ruta):
    df = pd.read_csv(ruta)
    df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
    return df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Div"])

df = cargar_datos(DATA_PATH)

# =========================
# MAPA DE LIGAS (NOMBRES REALES)
# =========================
MAPA_LIGAS = {
    "E0": "Premier League",
    "SP1": "LaLiga",
    "D1": "Bundesliga",
    "I1": "Serie A",
    "F1": "Ligue 1",
    "N1": "Eredivisie",
    "P1": "Primeira Liga",
    "SC0": "Scottish Premiership",
    "B1": "Jupiler Pro League",
    "T1": "Süper Lig",
    "G1": "Super League Greece"
}

df["Liga"] = df["Div"].map(MAPA_LIGAS)
df = df.dropna(subset=["Liga"])

# =========================
# SELECTORES
# =========================
liga = st.selectbox("Liga", sorted(df["Liga"].unique()))
df_liga = df[df["Liga"] == liga]

local = st.selectbox("Equipo local", sorted(df_liga["HomeTeam"].unique()))
visitante = st.selectbox("Equipo visitante", sorted(df_liga["AwayTeam"].unique()))

c1 = st.text_input("Cuota Local")
cx = st.text_input("Cuota Empate")
c2 = st.text_input("Cuota Visitante")

def parse_cuota(x):
    try:
        return float(x.replace(",", "."))
    except:
        return None

# =========================
# MODELO POISSON
# =========================
def poisson_1x2(df, h, a):
    hdf = df[df["HomeTeam"] == h]
    adf = df[df["AwayTeam"] == a]

    if len(hdf) < 5 or len(adf) < 5:
        return 0.33, 0.34, 0.33

    lh = hdf["FTHG"].mean()
    la = adf["FTAG"].mean()

    p1 = px = p2 = 0
    for i in range(6):
        for j in range(6):
            p = poisson.pmf(i, lh) * poisson.pmf(j, la)
            if i > j:
                p1 += p
            elif i == j:
                px += p
            else:
                p2 += p

    total = p1 + px + p2
    return p1 / total, px / total, p2 / total

# =========================
# VALUE BET + CONFIANZA
# =========================
def value_bet(prob, cuota):
    if cuota is None or prob <= 0:
        return False, None
    justa = 1 / prob
    return cuota > justa, justa

def confianza(prob, cuota, justa):
    edge = (cuota - justa) / justa
    if edge > 0.25 and prob > 0.6:
        return 5
    if edge > 0.18:
        return 4
    if edge > 0.12:
        return 3
    if edge > 0.06:
        return 2
    return 1

# =========================
# ANALIZAR PARTIDO
# =========================
if st.button("Analizar partido"):
    p1, px, p2 = poisson_1x2(df_liga, local, visitante)

    st.subheader("📊 Probabilidades 1X2")
    st.write(f"Local: {p1*100:.2f}%")
    st.write(f"Empate: {px*100:.2f}%")
    st.write(f"Visitante: {p2*100:.2f}%")

    cuotas = {
        "Local": parse_cuota(c1),
        "Empate": parse_cuota(cx),
        "Visitante": parse_cuota(c2)
    }

    probs = {
        "Local": p1,
        "Empate": px,
        "Visitante": p2
    }

    picks = []
    for k in probs:
        val, justa = value_bet(probs[k], cuotas[k])
        if val:
            conf = confianza(probs[k], cuotas[k], justa)
            picks.append((k, cuotas[k], justa, conf))

    if not picks:
        st.info("No se detecta value en este partido.")
    else:
        picks = sorted(picks, key=lambda x: x[3], reverse=True)

        st.markdown("## 💰 Picks con value")
        for i, p in enumerate(picks):
            if modo == "FREE" and (i > 0 or p[3] < 3):
                st.warning("🔒 Más picks disponibles en PRO")
                break

            estrellas = "⭐" * p[3]
            st.success(
                f"{p[0]} | Cuota {p[1]} | Justa {p[2]:.2f} | Confianza {estrellas}"
            )
