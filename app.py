import streamlit as st
import pandas as pd
from pathlib import Path

# ===============================
# CONFIG PÁGINA
# ===============================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# ===============================
# LOGO
# ===============================
st.image("assets/logo.png", width=180)
st.markdown("## ⚽ STRIKELYAI — IA DE ANÁLISIS FUTBOLÍSTICO")

st.markdown("---")

# ===============================
# CARGA DE DATOS
# ===============================
DATA_PATH = Path("datos/europeo.csv")

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)

    # Normalizar nombres de columnas
    df.columns = [c.strip() for c in df.columns]

    # Detectar columna de liga
    if "Div" in df.columns:
        df["LIGA"] = df["Div"]
    elif "League" in df.columns:
        df["LIGA"] = df["League"]
    elif "Competition" in df.columns:
        df["LIGA"] = df["Competition"]
    else:
        df["LIGA"] = "EUROPEAN LEAGUE"

    # Columnas mínimas obligatorias
    required = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "LIGA"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Falta la columna obligatoria: {col}")

    return df.dropna(subset=["HomeTeam", "AwayTeam"])

df = cargar_datos(DATA_PATH)

# ===============================
# SELECTOR DE LIGA
# ===============================
st.markdown("### 🏆 LIGA")
ligas = sorted(df["LIGA"].unique())
liga_sel = st.selectbox(
    "SELECCIONA LA LIGA",
    ligas,
    key="liga_selector"
)

df_liga = df[df["LIGA"] == liga_sel]

# ===============================
# SELECTOR DE EQUIPOS
# ===============================
st.markdown("### 🏠 EQUIPO LOCAL")
equipo_local = st.selectbox(
    "LOCAL",
    sorted(df_liga["HomeTeam"].unique()),
    key="local_selector"
)

st.markdown("### ✈️ EQUIPO VISITANTE")
equipo_visitante = st.selectbox(
    "VISITANTE",
    sorted(df_liga["AwayTeam"].unique()),
    key="visitante_selector"
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
# BOTÓN PRINCIPAL
# ===============================
if st.button("📊 ANALIZAR PARTIDO"):

    cuota_1 = parse_cuota(c1)
    cuota_x = parse_cuota(cx)
    cuota_2 = parse_cuota(c2)

    # Datos históricos del enfrentamiento
    hist = df_liga[
        (df_liga["HomeTeam"] == equipo_local) &
        (df_liga["AwayTeam"] == equipo_visitante)
    ]

    total = len(hist)

    if total == 0:
        st.warning("⚠️ No hay datos históricos directos. Usando media de liga.")
        total = len(df_liga)

        p1 = (df_liga["FTHG"] > df_liga["FTAG"]).mean()
        px = (df_liga["FTHG"] == df_liga["FTAG"]).mean()
        p2 = (df_liga["FTHG"] < df_liga["FTAG"]).mean()
    else:
        p1 = (hist["FTHG"] > hist["FTAG"]).mean()
        px = (hist["FTHG"] == hist["FTAG"]).mean()
        p2 = (hist["FTHG"] < hist["FTAG"]).mean()

    # Normalizar
    s = p1 + px + p2
    p1, px, p2 = p1/s, px/s, p2/s

    st.markdown("## 📊 PROBABILIDADES 1X2")
    st.write(f"🏠 **Local:** {p1*100:.2f}%")
    st.write(f"🤝 **Empate:** {px*100:.2f}%")
    st.write(f"✈️ **Visitante:** {p2*100:.2f}%")

    # ===============================
    # VALUE BET
    # ===============================
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
        res = value(prob, cuota)
        if res:
            hay, justa = res
            st.write(
                f"{nombre}: Cuota justa {justa:.2f} → "
                f"{'🔥 VALUE' if hay else '❌ SIN VALUE'}"
            )

    st.markdown("---")
    st.caption("⚠️ Aviso: Esta app es solo informativa. No es consejo de apuesta.")
