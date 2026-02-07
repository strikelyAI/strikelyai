import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
CARPETA_DATOS = Path("datos")
SALIDA = Path("datos/europeo.csv")

# Mapeo flexible de columnas (ajústalo si hiciera falta)
COLUMN_MAP = {
    "Date": "Date",
    "HomeTeam": "HomeTeam",
    "AwayTeam": "AwayTeam",
    "FTHG": "FTHG",
    "FTAG": "FTAG",
}

dfs = []

# =========================
# PROCESAR CADA EXCEL
# =========================
for archivo in CARPETA_DATOS.glob("all-euro-data-*.xlsx"):
    season_raw = archivo.stem.replace("all-euro-data-", "")
    season = season_raw.replace("-", "/")

    print(f"\n📘 Procesando temporada {season}")

    xls = pd.ExcelFile(archivo)

    for hoja in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=hoja)

            # Comprobación mínima
            if not set(COLUMN_MAP.keys()).issubset(df.columns):
                print(f"⚠️  Hoja ignorada (faltan columnas): {hoja}")
                continue

            df = df[list(COLUMN_MAP.keys())].copy()
            df.rename(columns=COLUMN_MAP, inplace=True)

            df["League"] = hoja
            df["Season"] = season

            dfs.append(df)
            print(f"   ✔ {hoja} ({len(df)} partidos)")

        except Exception as e:
            print(f"❌ Error en hoja {hoja}: {e}")

# =========================
# UNIÓN FINAL
# =========================
if not dfs:
    raise RuntimeError("No se ha podido unir ningún archivo")

df_final = pd.concat(dfs, ignore_index=True)

df_final.to_csv(SALIDA, index=False, encoding="utf-8")

print("\n✅ Archivo europeo.csv creado correctamente")
print(f"📊 Total de partidos: {len(df_final)}")
print(f"🏆 Ligas: {df_final['League'].nunique()}")
print(f"📅 Temporadas: {df_final['Season'].nunique()}")
