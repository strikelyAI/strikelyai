import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from scipy.stats import poisson
from PIL import Image
import matplotlib.pyplot as plt

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="wide"
)

# =========================
# LOGOS
# =========================
logo = Image.open("assets/logo.png")
st.image(logo, width=150)
st.title("StrikelyAI")
st.caption("Predicción inteligente de fútbol europeo")

st.sidebar.image(logo, width=120)
st.sidebar.markdown("### StrikelyAI")

# =========================
# MODO USUARIO
# =========================
st.sidebar.markdown("## 🔐 Modo de acceso")
modo = st.sidebar.radio(
    "Selecciona tu plan",
    ["FREE", "PRO"],
    captions=["Acceso limitado", "Acceso completo"]
)

st.sidebar.warning(
    "⚠️ App informativa. No garantiza resultados. Juego responsable."
)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos/europeo.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Div"])

df = cargar_datos()

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
    "G1": "Super League Grecia"
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

def parse(x):
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
            if i > j: p1 += p
            elif i == j: px += p
            else: p2 += p
    t = p1 + px + p2
    return p1/t, px/t, p2/t

# =========================
# VALUE + CONFIANZA
# =========================
def value_bet(prob, cuota):
    if cuota is None or prob <= 0:
        return False, None
    justa = 1 / prob
    return cuota > justa, justa

def confianza(prob, cuota, justa):
    edge = (cuota - justa) / justa
    if edge > 0.25 and prob > 0.6: return 5
    if edge > 0.18: return 4
    if edge > 0.12: return 3
    if edge > 0.06: return 2
    return 1

# =========================
# ANALIZAR
# =========================
if st.button("Analizar partido"):
    p1, px, p2 = poisson_1x2(df_liga, local, visitante)

    st.subheader("📊 Probabilidades")
    st.write(f"Local: {p1*100:.2f}%")
    st.write(f"Empate: {px*100:.2f}%")
    st.write(f"Visitante: {p2*100:.2f}%")

    cuotas = {
        "Local": parse(c1),
        "Empate": parse(cx),
        "Visitante": parse(c2)
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
            if modo == "FREE" and i > 0:
                st.warning("🔒 Más picks disponibles en PRO")
                break
            if modo == "FREE" and p[3] < 3:
                continue

            estrellas = "⭐" * p[3]
            st.success(
                f"{p[0]} | Cuota {p[1]} | Justa {p[2]:.2f} | Confianza {estrellas}"
            )

# =========================
# DASHBOARD (SOLO PRO)
# =========================
st.markdown("---")
st.header("📈 Dashboard")

if modo == "FREE":
    st.info("🔒 Dashboard completo disponible en PRO")
else:
    ruta = "datos/picks.csv"
    if os.path.exists(ruta):
        hist = pd.read_csv(ruta)

        tab1, tab2 = st.tabs(["📊 Resultados", "📈 ROI"])

        with tab1:
            st.bar_chart(hist["resultado"].value_counts())

        with tab2:
            hist["acumulado"] = hist["beneficio"].cumsum()
            st.line_chart(hist["acumulado"])
    else:
        st.info("Aún no hay histórico suficiente.")
