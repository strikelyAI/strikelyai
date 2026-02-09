import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path

# ======================
# CONFIGURACIÓN GENERAL
# ======================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# ======================
# MODO OSCURO / CLARO
# ======================
modo_oscuro = st.sidebar.toggle("🌙 MODO OSCURO", value=False)

if modo_oscuro:
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        h1, h2, h3, h4, label { color: #FAFAFA; }
        div[data-baseweb="select"] > div { background-color: #1E222B; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; color: #0E1117; }
        h1, h2, h3, h4, label { color: #0E1117; }
        </style>
    """, unsafe_allow_html=True)

# ======================
# LOGO
# ======================
logo_path = Path("assets/logo.png")
if logo_path.exists():
    logo = Image.open(logo_path)
    st.image(logo, width=220)

st.markdown("<h1 style='text-align:center;'>⚽ STRIKELYAI</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ======================
# CARGA DE DATOS
# ======================
DATA_PATH = "datos/europeo.csv"

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    columnas_necesarias = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Div"]
    columnas_existentes = [c for c in columnas_necesarias if c in df.columns]
    return df.dropna(subset=columnas_existentes)

df = cargar_datos(DATA_PATH)

# ======================
# MAPEO DE LIGAS
# ======================
MAPA_LIGAS = {
    "E0": "Premier League 🇬🇧",
    "SP1": "LaLiga 🇪🇸",
    "D1": "Bundesliga 🇩🇪",
    "I1": "Serie A 🇮🇹",
    "F1": "Ligue 1 🇫🇷",
    "N1": "Eredivisie 🇳🇱",
    "P1": "Primeira Liga 🇵🇹",
    "SC0": "Scotland Premiership 🏴",
    "B1": "Jupiler Pro League 🇧🇪",
    "T1": "Süper Lig 🇹🇷",
    "G1": "Super League Greece 🇬🇷"
}

df["LIGA_NOMBRE"] = df["Div"].map(MAPA_LIGAS)
df = df.dropna(subset=["LIGA_NOMBRE"])

# ======================
# SELECTORES
# ======================
st.markdown("## 🏆 LIGA")
liga_nombre = st.selectbox(
    "",
    sorted(df["LIGA_NOMBRE"].unique()),
    key="liga_selector"
)

liga_div = [k for k, v in MAPA_LIGAS.items() if v == liga_nombre][0]
df_liga = df[df["Div"] == liga_div]

st.markdown("## 🏠 EQUIPO LOCAL")
local = st.selectbox(
    "",
    sorted(df_liga["HomeTeam"].unique()),
    key="local_selector"
)

st.markdown("## ✈️ EQUIPO VISITANTE")
visitante = st.selectbox(
    "",
    sorted(df_liga["AwayTeam"].unique()),
    key="visitante_selector"
)

# ======================
# CUOTAS
# ======================
st.markdown("## 💰 CUOTAS")
c1 = st.text_input("Victoria local")
cx = st.text_input("Empate")
c2 = st.text_input("Victoria visitante")

# ======================
# BOTÓN ANALIZAR
# ======================
if st.button("🔍 ANALIZAR PARTIDO"):
    st.markdown("### 📊 PROBABILIDADES (MODELO BASE)")
    st.write("⚠️ Modelo inicial — se irá refinando")

    prob_local = 0.45
    prob_empate = 0.25
    prob_visitante = 0.30

    st.metric("🏠 Local", f"{prob_local*100:.1f}%")
    st.metric("➖ Empate", f"{prob_empate*100:.1f}%")
    st.metric("✈️ Visitante", f"{prob_visitante*100:.1f}%")

    def value(prob, cuota):
        try:
            cuota = float(cuota.replace(",", "."))
            justa = round(1 / prob, 2)
            return cuota > justa, justa
        except:
            return False, None

    st.markdown("### 🔥 VALUE BETS")
    for nombre, prob, cuota in [
        ("Local", prob_local, c1),
        ("Empate", prob_empate, cx),
        ("Visitante", prob_visitante, c2),
    ]:
        hay, justa = value(prob, cuota)
        if justa:
            st.write(f"**{nombre}** → Cuota justa {justa} {'🔥 VALUE' if hay else '❌ NO VALUE'}")

    st.markdown("---")
    st.caption("🔞 +18 | Herramienta informativa. Juega con responsabilidad.")
