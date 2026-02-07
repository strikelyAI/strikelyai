# =======================
# STRIKELYAI — APP FINAL
# =======================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
from engine import *

# =======================
# CONFIG
# =======================
st.set_page_config(
    page_title="StrikelyAI",
    page_icon="assets/icono.png",
    layout="centered"
)

# =======================
# LOGO BASE64
# =======================
def load_logo(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = load_logo("assets/logo.png")

# =======================
# SIDEBAR
# =======================
st.sidebar.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{logo_b64}" style="width:110px;">
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.title("StrikelyAI")

# =======================
# ESTILOS
# =======================
st.markdown("""
<style>
.stApp { background:#020617; color:white; font-family:Inter; }
section[data-testid="stSidebar"] { background:#0F172A; }
.panel { background:#0F172A; padding:28px; border-radius:18px; }
.metric-card { background:#020617; padding:18px; border-radius:14px; text-align:center; }
.metric-card h3 { color:#22C55E; }
small { color:#94A3B8; }
.stButton>button {
    background:#22C55E; color:white; border-radius:10px; font-weight:600;
}
.stButton>button:hover { background:#16A34A; }

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.08)!important;
    border:1px solid rgba(148,163,184,.35)!important;
    border-radius:10px!important;
}
div[data-baseweb="select"]:hover > div,
div[data-baseweb="input"]:hover > div {
    border-color:#22C55E!important;
}
</style>
""", unsafe_allow_html=True)

# =======================
# HEADER
# =======================
st.title("StrikelyAI")
st.markdown("### Análisis estadístico · Probabilidades reales · Value automático")

# =======================
# DATA
# =======================
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

ligas = {
    "LaLiga": "datos/laliga.csv",
    "Premier League": "datos/premier.csv",
    "Champions League": "datos/champions.csv"
}

liga = st.selectbox("🏆 Competición", ligas.keys())
df = load_csv(ligas[liga])
equipos = sorted(set(df["HomeTeam"]).union(df["AwayTeam"]))

# =======================
# INPUTS
# =======================
st.markdown('<div class="panel">', unsafe_allow_html=True)
local = st.selectbox("Equipo local", equipos)
visitante = st.selectbox("Equipo visitante", equipos)

if local == visitante:
    st.stop()

c1 = st.text_input("Cuota victoria local")
cx = st.text_input("Cuota empate")
c2 = st.text_input("Cuota victoria visitante")

# =======================
# ANALIZAR
# =======================
if st.button("🔍 Analizar partido"):

    lh, la = calcular_lambdas(df, local, visitante)
    p1, px, p2 = probabilidades_1x2(lh, la)
    probs = {"Local": p1, "Empate": px, "Visitante": p2}
    favorito = max(probs, key=probs.get)

    tab1, tab2, tab3 = st.tabs(["📌 Resumen", "📊 Probabilidades", "💡 Recomendación"])

    with tab1:
        st.markdown(f"**Favorito según el modelo:** 🟢 **{favorito}**")
        cols = st.columns(3)
        for i, k in enumerate(probs):
            cols[i].markdown(
                f"""
                <div class="metric-card">
                    <h3>{k}</h3>
                    <b>{probs[k]*100:.1f}%</b>
                </div>
                """,
                unsafe_allow_html=True
            )

    with tab2:
        labels = list(probs.keys())
        values = [v*100 for v in probs.values()]
        colors = ["#22C55E", "#94A3B8", "#3B82F6"]
        fig, ax = plt.subplots()
        bars = ax.bar(labels, values, color=colors)
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+1,
                    f"{b.get_height():.1f}%", ha="center")
        ax.set_ylim(0,100)
        st.pyplot(fig)

    with tab3:
        cuotas = {"Local": c1, "Empate": cx, "Visitante": c2}
        values = []

        for k, c in cuotas.items():
            if c.strip():
                cuota = float(c.replace(",", "."))
                value = calcular_value(probs[k], cuota)
                if value is not None:
                    values.append((k, value, cuota))

        fuertes = [v for v in values if v[1] >= 0.10]
        aceptables = [v for v in values if 0 < v[1] < 0.10]

        if fuertes:
            best = max(fuertes, key=lambda x: x[1])
            st.success(
                f"🔥 **Recomendación principal:** {best[0]}\n\n"
                f"Cuota: {best[2]} · Value: **+{best[1]*100:.1f}%**"
            )

        if aceptables:
            st.info("⚖️ Otras opciones con value:")
            for o in aceptables:
                st.write(f"- {o[0]} → +{o[1]*100:.1f}%")

        if not fuertes and not aceptables:
            st.warning("❌ No se detecta value claro en este partido.")

st.markdown("</div>", unsafe_allow_html=True)

st.caption("© StrikelyAI · Uso responsable")
