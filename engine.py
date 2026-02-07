# =======================
# STRIKELYAI — ENGINE
# =======================

import numpy as np
import pandas as pd
from scipy.stats import poisson

# =======================
# PARÁMETROS INDUSTRIA
# =======================
LAMBDA_MIN = 0.4
LAMBDA_MAX = 3.0

EMPATE_MIN = 0.15
EMPATE_MAX = 0.30

CUOTA_MIN = 1.20
CUOTA_MAX = 15.00

# =======================
# HELPERS
# =======================
def clamp(x, low, high):
    return max(low, min(high, x))

# =======================
# LAMBDAS POISSON
# =======================
def calcular_lambdas(df, local, visitante):
    partidos_local = df[df["HomeTeam"] == local]
    partidos_visit = df[df["AwayTeam"] == visitante]

    if len(partidos_local) < 5 or len(partidos_visit) < 5:
        return 1.2, 1.0  # fallback prudente

    goles_local = partidos_local["FTHG"].mean()
    goles_visit = partidos_visit["FTAG"].mean()

    lh = clamp(goles_local, LAMBDA_MIN, LAMBDA_MAX)
    la = clamp(goles_visit, LAMBDA_MIN, LAMBDA_MAX)

    return lh, la

# =======================
# PROBABILIDADES 1X2
# =======================
def probabilidades_1x2(lh, la):
    max_goals = 6
    prob_local = prob_empate = prob_visit = 0.0

    for i in range(max_goals):
        for j in range(max_goals):
            p = poisson.pmf(i, lh) * poisson.pmf(j, la)
            if i > j:
                prob_local += p
            elif i == j:
                prob_empate += p
            else:
                prob_visit += p

    # Blindaje empate
    prob_empate = clamp(prob_empate, EMPATE_MIN, EMPATE_MAX)

    # Normalizar
    total = prob_local + prob_empate + prob_visit
    prob_local /= total
    prob_empate /= total
    prob_visit /= total

    return prob_local, prob_empate, prob_visit

# =======================
# VALUE BET
# =======================
def calcular_value(prob, cuota):
    if cuota < CUOTA_MIN or cuota > CUOTA_MAX:
        return None
    return prob * cuota - 1
