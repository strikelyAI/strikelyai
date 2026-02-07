# =========================
# StrikelyAI — app.py
# =========================

import streamlit as st
import pandas as pd
from PIL import Image

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# =========================
# ESTILOS
# =========================
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.stSelectbox label, .stTextInput label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
logo = Image.open("assets/logo.png")
st.image(logo, width=170)
st.title("StrikelyAI")
st.caption("Recomendaciones inteligentes basadas en valor estadístico")

st.divider()

# =========================
# DATOS
# =========================
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos/europeo.csv")

df = cargar_datos()

def detectar_columna_liga(df):
    for col in ["League", "Div", "competition", "Comp"]:
        if col in df.columns:
            return col
    return None

col_liga = detectar_columna_liga(df)
if not col_liga:
    st.error("No se detectó columna de liga")
    st.stop()

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
    "B1": "Jupiler Pro League",
    "T1": "Süper Lig",
    "G1": "Super League"
}

ligas_cod = sorted(df[col_liga].unique())
ligas_ui = {MAPA_LIGAS.get(l, l): l for l in ligas_cod}

liga_ui = st.selectbox("🏆 Liga", list(ligas_ui.keys()))
liga = ligas_ui[liga_ui]

df_liga = df[df[col_liga] == liga]

# =========================
# EQUIPOS
# =========================
equipos = sorted(
    pd.concat([df_liga["HomeTeam"], df_liga["AwayTeam"]]).unique()
)

c1, c2 = st.columns(2)
with c1:
    local = st.selectbox("🏠 Local", equipos)
with c2:
    visitante = st.selectbox("✈️ Visitante", [e for e in equipos if e != local])

st.divider()

# =========================
# CUOTAS
# =========================
st.subheader("💰 Cuotas (opcional)")
c1, c2, c3 = st.columns(3)

def parse(x):
    try:
        return float(x.replace(",", "."))
    except:
        return None

cuota_l = parse(c1.text_input("Local", ""))
cuota_e = parse(c2.text_input("Empate", ""))
cuota_v = parse(c3.text_input("Visitante", ""))

# =========================
# MODELO SIMPLE + FORMA
# =========================
def probs(df, local, visitante):
    h = df[df["HomeTeam"] == local].tail(20)
    a = df[df["AwayTeam"] == visitante].tail(20)

    if len(h) < 5 or len(a) < 5:
        return 0.45, 0.25, 0.30, 0.3

    gl = h["FTHG"].mean()
    gv = a["FTAG"].mean()

    total = gl + gv
    if total == 0:
        return 0.45, 0.25, 0.30, 0.3

    p_l = gl / total
    p_v = gv / total
    p_e = max(0.15, 1 - p_l - p_v)

    s = p_l + p_e + p_v
    confianza = min(1, (len(h)+len(a)) / 40)

    return p_l/s, p_e/s, p_v/s, confianza

# =========================
# ANALIZAR
# =========================
if st.button("⚽ Analizar partido", use_container_width=True):

    p_l, p_e, p_v, conf = probs(df_liga, local, visitante)

    st.subheader("📊 Probabilidades")
    st.write(f"Local: **{p_l*100:.1f}%**")
    st.write(f"Empate: **{p_e*100:.1f}%**")
    st.write(f"Visitante: **{p_v*100:.1f}%**")

    # =========================
    # RECOMENDACIÓN
    # =========================
    st.subheader("🔥 Recomendación StrikelyAI")

    opciones = [
        ("Local", p_l, cuota_l),
        ("Empate", p_e, cuota_e),
        ("Visitante", p_v, cuota_v),
    ]

    values = []
    for nombre, prob, cuota in opciones:
        if cuota and prob >= 0.15:
            justa = 1 / prob
            value_pct = (cuota - justa) / justa
            if value_pct >= 0.05:
                values.append((nombre, cuota, justa, value_pct))

    if values:
        values.sort(key=lambda x: x[3], reverse=True)
        mejor = values[0]

        st.success(
            f"🥇 **{mejor[0]}** · Cuota {mejor[1]:.2f} · "
            f"Justa {mejor[2]:.2f} · "
            f"Value **{mejor[3]*100:.1f}%**"
        )

        if len(values) > 1:
            st.markdown("**Otras opciones con value:**")
            for v in values[1:]:
                st.write(
                    f"• {v[0]} → {v[3]*100:.1f}%"
                )
    else:
        st.info("No se detecta value claro según criterios conservadores.")

    st.caption(f"Confianza del modelo: {conf*100:.0f}%")

# =========================
# AVISO
# =========================
st.divider()
st.caption(
    "⚠️ StrikelyAI es una herramienta de apoyo estadístico. "
    "No garantiza resultados ni sustituye el criterio del usuario."
)
