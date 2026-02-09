import streamlit as st
import pandas as pd
from pathlib import Path

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

st.image("assets/logo.png", width=180)
st.markdown("## ⚽ STRIKELYAI — IA DE ANÁLISIS FUTBOLÍSTICO")
st.markdown("---")

# ===============================
# MAPA DE LIGAS
# ===============================
MAPA_LIGAS = {
    "E0": "Premier League (Inglaterra)",
    "E1": "Championship (Inglaterra)",
    "E2": "League One (Inglaterra)",
    "E3": "League Two (Inglaterra)",
    "EC": "Conference (Inglaterra)",

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

# ===============================
# CARGA DE DATOS
# ===============================
DATA_PATH = Path("datos/europeo.csv")

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    if "Div" not in df.columns:
        raise ValueError("El CSV no contiene la columna Div")

    df["LIGA_CODIGO"] = df["Div"]
    df["LIGA"] = df["Div"].map(MAPA_LIGAS).fillna(df["Div"])

    return df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])

df = cargar_datos(DATA_PATH)

# ===============================
# SELECTOR DE LIGA
# ===============================
st.markdown("### 🏆 LIGA")
ligas = sorted(df["LIGA"].unique())
liga_sel = st.selectbox("SELECCIONA LA LIGA", ligas)

df_liga = df[df["LIGA"] == liga_sel]

# ===============================
# SELECTOR DE EQUIPOS
# ===============================
st.markdown("### 🏠 EQUIPO LOCAL")
local = st.selectbox(
    "LOCAL",
    sorted(df_liga["HomeTeam"].unique()),
    key="local"
)

st.markdown("### ✈️ EQUIPO VISITANTE")
visitante = st.selectbox(
    "VISITANTE",
    sorted(df_liga["AwayTeam"].unique()),
    key="visitante"
)

st.markdown("---")

# ===============================
# CUOTAS
# ===============================
st.markdown("### 💰 CUOTAS (OPCIONAL)")
c1 = st.text_input("Victoria Local")
cx = st.text_input("Empate")
c2 = st.text_input("Victoria Visitante")

def parse_cuota(x):
    try:
        return float(x.replace(",", "."))
    except:
        return None

# ===============================
# ANALIZAR
# ===============================
if st.button("📊 ANALIZAR PARTIDO"):

    cuota_1 = parse_cuota(c1)
    cuota_x = parse_cuota(cx)
    cuota_2 = parse_cuota(c2)

    hist = df_liga[
        (df_liga["HomeTeam"] == local) &
        (df_liga["AwayTeam"] == visitante)
    ]

    if len(hist) == 0:
        base = df_liga
    else:
        base = hist

    p1 = (base["FTHG"] > base["FTAG"]).mean()
    px = (base["FTHG"] == base["FTAG"]).mean()
    p2 = (base["FTHG"] < base["FTAG"]).mean()

    s = p1 + px + p2
    p1, px, p2 = p1/s, px/s, p2/s

    st.markdown("## 📊 PROBABILIDADES 1X2")
    st.write(f"🏠 **Local:** {p1*100:.2f}%")
    st.write(f"🤝 **Empate:** {px*100:.2f}%")
    st.write(f"✈️ **Visitante:** {p2*100:.2f}%")

    st.markdown("## 🔥 VALUE BET")

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
                f"{nombre}: Cuota justa {justa:.2f} → "
                f"{'🔥 VALUE' if hay else '❌ SIN VALUE'}"
            )

    st.caption("⚠️ Uso informativo. No es consejo de apuesta.")
