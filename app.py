# ============================
# IMPORTS
# ============================
import streamlit as st
import pandas as pd
import unicodedata
import re
import numpy as np
from scipy.stats import poisson

# ============================
# CONFIG STREAMLIT
# ============================
st.set_page_config(page_title="StrikelyAI", layout="centered")

st.title("⚽ StrikelyAI")
st.caption("Modelo Poisson · Probabilidades reales · Value")

# ============================
# NORMALIZACIÓN
# ============================

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return texto
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


ALIAS_EQUIPOS = {
    "real madrid": ["madrid", "realmadrid"],
    "barcelona": ["fc barcelona", "barca"],
    "atletico madrid": ["atletico"],
    "rayo vallecano": ["rayo"],
    "athletic club": ["bilbao"],
    "manchester united": ["man utd"],
    "manchester city": ["man city"],
    "bayern munich": ["bayern"],
    "psg": ["paris saint germain"],
}


def normalizar_equipo(nombre):
    nombre = normalizar_texto(nombre)
    for canonico, alias in ALIAS_EQUIPOS.items():
        if nombre == canonico or nombre in alias:
            return canonico
    return nombre


# ============================
# CARGA DE DATOS
# ============================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos/europeo.csv", parse_dates=["Date"])

    df["HomeTeam"] = df["HomeTeam"].apply(normalizar_equipo)
    df["AwayTeam"] = df["AwayTeam"].apply(normalizar_equipo)

    def detectar_temporada(fecha):
        return f"{fecha.year}/{fecha.year+1}" if fecha.month >= 7 else f"{fecha.year-1}/{fecha.year}"

    df["Season"] = df["Date"].apply(detectar_temporada)

    temporada_actual = sorted(df["Season"].unique())[-1]
    df_actual = df[df["Season"] == temporada_actual]

    return df, df_actual


df_hist, df_actual = cargar_datos()

# ============================
# SELECTOR DE LIGA
# ============================

ligas = sorted(df_actual["Div"].unique())
liga_sel = st.selectbox("🏆 Liga", ligas)

df_liga_actual = df_actual[df_actual["Div"] == liga_sel]
df_liga_hist = df_hist[df_hist["Div"] == liga_sel]

# ============================
# EQUIPOS
# ============================

equipos = sorted(set(df_liga_actual["HomeTeam"]).union(df_liga_actual["AwayTeam"]))

col1, col2 = st.columns(2)
with col1:
    local = st.selectbox("Equipo local", equipos)
with col2:
    visitante = st.selectbox("Equipo visitante", equipos)

# ============================
# CUOTAS
# ============================

st.subheader("💰 Cuotas (opcional)")
c1, c2, c3 = st.columns(3)
cuota_l = c1.text_input("Local")
cuota_e = c2.text_input("Empate")
cuota_v = c3.text_input("Visitante")


def parse_cuota(x):
    try:
        return float(x.replace(",", "."))
    except:
        return None


# ============================
# MODELO POISSON
# ============================

def goles_esperados(df, equipo, es_local=True):
    partidos = df[df["HomeTeam"] == equipo] if es_local else df[df["AwayTeam"] == equipo]
    if len(partidos) == 0:
        return 1.2
    goles = partidos["FTHG"] if es_local else partidos["FTAG"]
    return goles.mean()


def probabilidades_poisson(df, local, visitante, max_goles=5):
    lambda_l = goles_esperados(df, local, True)
    lambda_v = goles_esperados(df, visitante, False)

    p_local = p_empate = p_visit = 0

    for i in range(max_goles + 1):
        for j in range(max_goles + 1):
            p = poisson.pmf(i, lambda_l) * poisson.pmf(j, lambda_v)
            if i > j:
                p_local += p
            elif i == j:
                p_empate += p
            else:
                p_visit += p

    total = p_local + p_empate + p_visit
    return p_local / total, p_empate / total, p_visit / total


def value_bet(prob, cuota):
    if cuota is None or prob <= 0:
        return False, None
    justa = 1 / prob
    return cuota > justa, justa


# ============================
# ANÁLISIS
# ============================

if st.button("🔍 Analizar partido"):
    p_l, p_e, p_v = probabilidades_poisson(df_liga_hist, local, visitante)

    st.subheader("📊 Probabilidades (Poisson)")
    st.write(f"Local: **{p_l*100:.2f}%**")
    st.write(f"Empate: **{p_e*100:.2f}%**")
    st.write(f"Visitante: **{p_v*100:.2f}%**")

    st.subheader("💎 Value")
    for nombre, prob, cuota in [
        ("Local", p_l, parse_cuota(cuota_l)),
        ("Empate", p_e, parse_cuota(cuota_e)),
        ("Visitante", p_v, parse_cuota(cuota_v)),
    ]:
        ok, justa = value_bet(prob, cuota)
        if justa:
            st.write(f"{nombre}: cuota justa {justa:.2f} → {'🔥 VALUE' if ok else '❌'}")

st.markdown("---")
st.caption("⚠️ Uso informativo · No es consejo de inversión")
