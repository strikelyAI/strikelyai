# unir_premier.py
import pandas as pd
import glob

# Carpeta donde están todos los CSV de la Premier
archivos_premier = r"C:\Users\Usuario\ANALISIS DEPORTIVO IA\datos\E0*.csv"

# Archivo final unido
output_csv = r"C:\Users\Usuario\ANALISIS DEPORTIVO IA\datos\premier.csv"

# Busca todos los CSV que empiecen con E0
files = glob.glob(archivos_premier)
print("Archivos encontrados:", files)

dfs = []

# Columnas que queremos mantener si existen
columnas_deseadas = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HC', 'AC', 'YC_H', 'YC_A']

for f in files:
    df = pd.read_csv(f)
    # Solo mantener las columnas que existen en este CSV
    columnas_existentes = [c for c in columnas_deseadas if c in df.columns]
    df = df[columnas_existentes]
    dfs.append(df)

if dfs:
    # Unir todos los DataFrames
    df_final = pd.concat(dfs, ignore_index=True)
    # Guardar CSV final
    df_final.to_csv(output_csv, index=False)
    print(f"CSV final Premier creado en: {output_csv}")
else:
    print("No se encontraron CSV para unir.")
