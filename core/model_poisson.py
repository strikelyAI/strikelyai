import math

def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * lmbda**k) / math.factorial(k)

def calcular_probabilidades(df, local, visitante, ultimos=10):
    home = df[df["HomeTeam"] == local].tail(ultimos)
    away = df[df["AwayTeam"] == visitante].tail(ultimos)

    partidos = min(len(home), len(away))
    if partidos < 3:
        return None

    pesos = list(range(1, partidos + 1))
    lambda_home = (home["FTHG"].tail(partidos) * pesos).sum() / sum(pesos)
    lambda_away = (away["FTAG"].tail(partidos) * pesos).sum() / sum(pesos)

    pL = pE = pV = 0
    for i in range(6):
        for j in range(6):
            p = poisson_prob(lambda_home, i) * poisson_prob(lambda_away, j)
            if i > j:
                pL += p
            elif i == j:
                pE += p
            else:
                pV += p

    total = pL + pE + pV
    pL, pE, pV = pL/total, pE/total, pV/total

    if partidos >= 8:
        calidad = "Alta"
    elif partidos >= 5:
        calidad = "Media"
    else:
        calidad = "Baja"

    return {
        "Local": pL,
        "Empate": pE,
        "Visitante": pV,
        "lambda_home": lambda_home,
        "lambda_away": lambda_away,
        "partidos": partidos,
        "calidad": calidad
    }
