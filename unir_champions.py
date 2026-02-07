import pandas as pd
import os

RUTA = "datos"
dfs = []

# =========
# ARCHIVO 2 (API style)
# =========
f2 = os.path.join(RUTA, "ucl  (2).csv")
df2 = pd.read_csv(f2)

df2 = df2.rename(columns={
    "home_team": "HomeTeam",
    "away_team": "AwayTeam",
    "home_goals": "FTHG",
    "away_goals": "FTAG",
    "date": "Date"
})

df2 = df2[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]]
dfs.append(df2)

# =========
# ARCHIVO 3 (score tipo 1–3)
# =========
f3 = os.path.join(RUTA, "ucl  (3).csv")
df3 = pd.read_csv(f3)

# Separar score "1–3"
df3[["FTHG", "FTAG"]] = df3["score"].str.replace("–", "-").str.split("-", expand=True)
df3["FTHG"] = pd.to_numeric(df3["FTHG"])
df3["FTAG"] = pd.to_numeric(df3["FTAG"])

df3 = df3.rename(columns={
    "home_team": "HomeTeam",
    "away_team": "AwayTeam",
    "date": "Date"
})

df3 = df3[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]]
dfs.append(df3)

# =========
# UNIÓN FINAL
# =========
champions = pd.concat(dfs, ignore_index=True)

# Limpiar nulos
champions = champions.dropna()

# Guardar
champions.to_csv(os.path.join(RUTA, "champions.csv"), index=False)

print("✅ champions.csv creado correctamente")
print("Filas totales:", len(champions))
print(champions.head())
