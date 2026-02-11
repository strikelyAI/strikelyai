import streamlit as st
import pandas as pd
import numpy as np
from math import exp, factorial

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="StrikelyAI",
    layout="centered"
)

# ==========================================
# ESTILO VISUAL PREMIUM
# ==========================================

st.markdown("""
<style>
body { background-color: #ffffff; }
h1, h2, h3 { color: #0A1F44; font-weight: 800; }
.block-container { padding-top: 2rem; }
.stSelectbox label, .stTextInput label { font-weight: 700; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CARGA DE DATOS ROBUSTA
# ==========================================

DATA_PATH = "datos/europeo.csv"

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path)
    
    required = ["HomeTeam","AwayTeam","FTHG","FTAG"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Falta columna obligatoria: {col}")
    
    if "Div" not in df.columns:
        df["Div"] = "Liga Desconocida"
        
    return df.dropna(subset=["HomeTeam","AwayTeam","FTHG","FTAG"])

df = cargar_datos(DATA_PATH)

# ==========================================
# MAPA LIGAS
# ==========================================

MAPA_LIGAS = {
    "E0": "Premier League",
    "SP1": "La Liga",
    "D1": "Bundesliga",
    "I1": "Serie A",
    "F1": "Ligue 1",
    "N1": "Eredivisie",
    "P1": "Liga Portugal"
}

df["LIGA_NOMBRE"] = df["Div"].map(MAPA_LIGAS).fillna(df["Div"])

# ==========================================
# FUNCIONES MODELO
# ==========================================

def poisson(lmbda, k):
    return (lmbda**k * exp(-lmbda)) / factorial(k)

def calcular_forma(df, equipo, local=True):
    ultimos = df[(df["HomeTeam"] == equipo) | (df["AwayTeam"] == equipo)].tail(5)
    puntos = 0
    for _, row in ultimos.iterrows():
        if row["HomeTeam"] == equipo:
            if row["FTHG"] > row["FTAG"]: puntos += 3
            elif row["FTHG"] == row["FTAG"]: puntos += 1
        else:
            if row["FTAG"] > row["FTHG"]: puntos += 3
            elif row["FTAG"] == row["FTHG"]: puntos += 1
    return puntos / 15

def modelo_probabilidades(df_liga, local, visitante):
    media_local = df_liga[df_liga["HomeTeam"] == local]["FTHG"].mean()
    media_visit = df_liga[df_liga["AwayTeam"] == visitante]["FTAG"].mean()
    
    forma_local = calcular_forma(df_liga, local)
    forma_visit = calcular_forma(df_liga, visitante)
    
    lambda_local = media_local * (1 + forma_local*0.3)
    lambda_visit = media_visit * (1 + forma_visit*0.3)
    
    max_goles = 5
    prob_local = 0
    prob_empate = 0
    prob_visit = 0
    
    for i in range(max_goles):
        for j in range(max_goles):
            p = poisson(lambda_local,i) * poisson(lambda_visit,j)
            if i > j: prob_local += p
            elif i == j: prob_empate += p
            else: prob_visit += p
    
    total = prob_local + prob_empate + prob_visit
    return prob_local/total, prob_empate/total, prob_visit/total, lambda_local, lambda_visit

def value_bet(prob, cuota):
    justa = 1 / prob
    return cuota > justa, justa

# ==========================================
# INTERFAZ
# ==========================================

st.title("⚽ STRIKELYAI")

liga = st.selectbox("🏆 LIGA", sorted(df["LIGA_NOMBRE"].unique()), key="liga_select")

df_liga = df[df["LIGA_NOMBRE"] == liga]

local = st.selectbox("🏠 EQUIPO LOCAL", sorted(df_liga["HomeTeam"].unique()), key="local_select")
visitante = st.selectbox("✈️ EQUIPO VISITANTE", sorted(df_liga["AwayTeam"].unique()), key="visit_select")

st.markdown("### 💰 CUOTAS")

cuota_local = st.number_input("Cuota Local", min_value=1.01, value=1.80)
cuota_empate = st.number_input("Cuota Empate", min_value=1.01, value=3.50)
cuota_visit = st.number_input("Cuota Visitante", min_value=1.01, value=4.00)

if st.button("🔍 ANALIZAR PARTIDO"):
    
    prob_l, prob_e, prob_v, xg_l, xg_v = modelo_probabilidades(df_liga, local, visitante)
    
    st.markdown("## 📊 PROBABILIDADES")
    st.write(f"Local: {prob_l*100:.2f}%")
    st.write(f"Empate: {prob_e*100:.2f}%")
    st.write(f"Visitante: {prob_v*100:.2f}%")
    
    st.markdown("## 🎯 xG ESTIMADO")
    st.write(f"xG Local: {xg_l:.2f}")
    st.write(f"xG Visitante: {xg_v:.2f}")
    
    val_l, justa_l = value_bet(prob_l, cuota_local)
    val_e, justa_e = value_bet(prob_e, cuota_empate)
    val_v, justa_v = value_bet(prob_v, cuota_visit)
    
    st.markdown("## 💎 VALUE BET")
    
    if val_l:
        st.success(f"🔥 VALUE LOCAL (Justa {justa_l:.2f})")
    if val_e:
        st.success(f"🔥 VALUE EMPATE (Justa {justa_e:.2f})")
    if val_v:
        st.success(f"🔥 VALUE VISITANTE (Justa {justa_v:.2f})")
    
    if not any([val_l,val_e,val_v]):
        st.warning("No hay value claro en este partido.")

# ==========================================
# AVISO LEGAL
# ==========================================

st.markdown("---")
st.caption("⚠️ StrikelyAI es una herramienta estadística. No garantiza resultados. Apostar implica riesgo.")
