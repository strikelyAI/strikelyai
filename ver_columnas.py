import pandas as pd
from pathlib import Path

CARPETA_TEMPORADAS = Path("datos/temporadas")

for archivo in CARPETA_TEMPORADAS.glob("*.xlsx"):
    print(f"\n📘 ARCHIVO: {archivo.name}")
    xls = pd.ExcelFile(archivo)

    for hoja in xls.sheet_names:
        print(f"\n  📄 HOJA: {hoja}")
        df = pd.read_excel(xls, sheet_name=hoja)
        print("  Columnas encontradas:")
        print(" ", list(df.columns))
        break  # solo la primera hoja para no saturar
    break      # solo el primer archivo
