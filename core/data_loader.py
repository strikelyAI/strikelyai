import pandas as pd

def cargar_datos(ruta):
    df = pd.read_csv(ruta)

    # Normalizar columnas clave
    columnas_necesarias = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "Div", "Season"]
    for col in columnas_necesarias:
        if col not in df.columns:
            df[col] = None

    return df
