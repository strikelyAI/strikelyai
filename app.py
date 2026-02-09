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
# RUTAS
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datos" / "europeo.csv"

# =========================
# LOGOS
# =========================
logo = Image.open(BASE_DIR / "assets" / "logo.png")
st.image(logo, width=150)
st.markdown("## ⚽ **STRIKELYAI**")
st.caption("IA de predicción avanzada de fútbol europeo")

st.sidebar.image(logo, width=120)
st.sidebar.markdown("## ⚽ **STRIKELYAI**")
st.sidebar.warning("⚠️ App informativa. Juego responsable.")

# =========================
# MODO
# =========================
st.sidebar.markdown("### 🔐 **MODO DE ACCESO**")
modo = st.sidebar.radio(
    "",
    ["FREE", "PRO"],
    captions=["Acceso limitado", "Acceso completo"]
)

# =========================
# CARGA ROBUSTA DE DATOS
# =========================
@st.cache_data
def cargar_datos(ruta):
    df = pd.read_csv(ruta)
    df.columns = df.columns.str.strip()

    columnas_map = {
        "HomeTeam": ["HomeTeam", "home_team"],
        "AwayTeam": ["AwayTeam", "away_team"],
        "FTHG": ["FTHG", "HG", "home_goals"],
        "FTAG": ["FTAG", "AG", "away_goals"],
        "Div": ["Div", "League", "Division", "competition"],
        "Date": ["Date", "date"]
    }

    for col_std, alternativas in columnas_map.items():
        for alt in alternativas:
            if alt in df.columns:
                df[col_std] = df[alt]
                break

    df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Div"])
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df

df = cargar_datos(DATA_PATH)

# =========================
# MAPA DE LIGAS
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

df["Liga"] = df["Div"].map(MAPA_LIGAS).fillna(df["Div"])

# =========================
# SELECTORES
# =========================
st.markdown("### 🏆 **LIGA**")
liga = st.selectbox("", sorted(df["Liga"].unique()))

df_liga = df[df["Liga"] == liga]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏠 **EQUIPO LOCAL**")
    local = st.selectbox("", sorted(df_liga["HomeTeam"].unique()))

with col2:
    st.markdown("### ✈️ **EQUIPO VISITANTE**")
    visitante = st.selectbox("", sorted(df_liga["AwayTeam"].unique()))

st.markdown("---")

# =========================
# CUOTAS
# =========================
st.markdown("### 💸 **CUOTAS 1X2 (OPCIONAL)**")

c1, cx, c2 = st.columns(3)

with c1:
    cuota_local = st.text_input("LOCAL")

with cx:
    cuota_empate = st.text_input("EMPATE")

with c2:
    cuota_visitante = st.text_input("VISITANTE")

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
# VALUE BET
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
# ANALIZAR
# =========================
st.markdown("---")
if st.button("🔍 ANALIZAR PARTIDO"):
    p1, px, p2 = poisson_1x2(df_liga, local, visitante)

    st.markdown("## 📊 **PROBABILIDADES 1X2**")
    st.write(f"🏠 Local: **{p1*100:.2f}%**")
    st.write(f"➖ Empate: **{px*100:.2f}%**")
    st.write(f"✈️ Visitante: **{p2*100:.2f}%**")

    cuotas = {
        "Local": parse_cuota(cuota_local),
        "Empate": parse_cuota(cuota_empate),
        "Visitante": parse_cuota(cuota_visitante)
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
        st.info("ℹ️ No se detecta value en este partido.")
    else:
        picks = sorted(picks, key=lambda x: x[3], reverse=True)
        st.markdown("## 💰 **VALUE BET DETECTADO**")

        for i, p in enumerate(picks):
            if modo == "FREE" and (i > 0 or p[3] < 3):
                st.warning("🔒 Más picks disponibles en PRO")
                break

            estrellas = "⭐" * p[3]
            st.success(
                f"**{p[0].upper()}** | Cuota {p[1]} | Justa {p[2]:.2f} | Confianza {estrellas}"
            )
