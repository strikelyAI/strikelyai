import streamlit as st
import pandas as pd
from pathlib import Path

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# ======================================================
# MODO CLARO / OSCURO
# ======================================================
modo = st.toggle("🌙 Modo oscuro", value=False)

if modo:
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# LOGO + TÍTULO
# ======================================================
st.image("assets/logo.png", width=180)
st.markdown("## ⚽ **STRIKELYAI**")
st.markdown("### IA de análisis y probabilidades de fútbol")
st.markdown("---")

# ======================================================
# MAPA DE LIGAS
# ======================================================
MAPA_LIGAS = {
    "E0": "Premier League (Inglaterra)",
    "E1": "Championship (Inglaterra)",
    "E2": "League One (Inglaterra)",
    "E3": "League Two (Inglaterra)",
    "SP1": "LaLiga (España)",
    "SP2": "LaLiga Hypermotion (España)",
    "D1": "Bundesliga (Alemania)",
    "D2": "2. Bundesliga (Alemania)",
    "I1": "Serie A (Italia)",
    "I2": "Serie B (Italia)",
    "F1": "Ligue 1 (Francia)",
    "F2": "Ligue 2 (Francia)",
    "N1": "Eredivisie (Países Bajos)",
    "P1": "Primeira Liga (Portugal)",
    "B1": "Jupiler Pro League (Bélgica)",
    "SC0": "Premiership (Escocia)",
    "SC1": "Championship (Escocia)",
    "SC2": "League One (Escocia)",
    "SC3": "League Two (Escocia)",
    "T1": "Süper Lig (Turquía)",
    "G1": "Super League (Grecia)"
}

# ======================================================
# CARGA DE DATOS (ROBUSTA)
# ======================================================
DATA_PATH = Path("datos/europeo.csv")

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    posibles = ["Div", "League", "LeagueCode", "Competition"]
    col_liga = next((c for c in posibles if c in df.columns), None)

    if col_liga is None:
        st.error("❌ No se encontró columna de liga en el dataset")
        st.stop()

    df["LIGA_CODIGO"] = df[col_liga].astype(str)
    df["LIGA"] = df["LIGA_CODIGO"].map(MAPA_LIGAS).fillna(df["LIGA_CODIGO"])

    df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])
    return df

df = cargar_datos(DATA_PATH)

# ======================================================
# SELECTOR DE LIGA
# ======================================================
st.markdown("### 🏆 **LIGA**")
liga = st.selectbox(
    "Selecciona la liga",
    sorted(df["LIGA"].unique()),
    key="liga_selector"
)

df_liga = df[df["LIGA"] == liga]

# ======================================================
# SELECTOR DE EQUIPOS
# ======================================================
st.markdown("### 🏠 **EQUIPO LOCAL**")
local = st.selectbox(
    "Local",
    sorted(df_liga["HomeTeam"].unique()),
    key="local_selector"
)

st.markdown("### ✈️ **EQUIPO VISITANTE**")
visitante = st.selectbox(
    "Visitante",
    sorted(df_liga["AwayTeam"].unique()),
    key="visitante_selector"
)

# ======================================================
# CUOTAS
# ======================================================
st.markdown("---")
st.markdown("### 💰 **CUOTAS (opcional)**")

c1 = st.text_input("Victoria Local")
cx = st.text_input("Empate")
c2 = st.text_input("Victoria Visitante")

def parse_cuota(x):
    try:
        return float(x.replace(",", "."))
    except:
        return None

# ======================================================
# BOTÓN DE ANÁLISIS
# ======================================================
if st.button("📊 ANALIZAR PARTIDO"):

    cuota_1 = parse_cuota(c1)
    cuota_x = parse_cuota(cx)
    cuota_2 = parse_cuota(c2)

    base = df_liga

    p1 = (base["FTHG"] > base["FTAG"]).mean()
    px = (base["FTHG"] == base["FTAG"]).mean()
    p2 = (base["FTHG"] < base["FTAG"]).mean()

    total = p1 + px + p2
    if total == 0:
        st.error("No hay datos suficientes para calcular probabilidades")
        st.stop()

    p1, px, p2 = p1/total, px/total, p2/total

    st.markdown("## 📊 **PROBABILIDADES 1X2**")
    st.write(f"🏠 Local: **{p1*100:.2f}%**")
    st.write(f"🤝 Empate: **{px*100:.2f}%**")
    st.write(f"✈️ Visitante: **{p2*100:.2f}%**")

    st.markdown("## 🔥 **VALUE BET**")

    def value(prob, cuota):
        if cuota is None or prob <= 0:
            return None
        justa = 1 / prob
        return cuota > justa, justa

    for nombre, prob, cuota in [
        ("LOCAL", p1, cuota_1),
        ("EMPATE", px, cuota_x),
        ("VISITANTE", p2, cuota_2),
    ]:
        r = value(prob, cuota)
        if r:
            hay, justa = r
            st.write(
                f"**{nombre}** → Cuota justa {justa:.2f} "
                f"{'🔥 VALUE' if hay else '❌ SIN VALUE'}"
            )

# ======================================================
# AVISO LEGAL
# ======================================================
st.markdown("---")
st.caption(
    "⚠️ **Aviso legal**: StrikelyAI es una herramienta informativa basada en datos "
    "históricos. No constituye consejo de inversión ni recomendación de apuestas. "
    "El uso de esta aplicación es responsabilidad exclusiva del usuario."
)
