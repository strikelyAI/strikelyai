import pandas as pd

files = [
    "datos/ucl  (1).csv",
    "datos/ucl  (2).csv",
    "datos/ucl  (3).csv"
]

for f in files:
    print("\n==============================")
    print("ARCHIVO:", f)
    try:
        try:
            df = pd.read_csv(f)
        except:
            df = pd.read_csv(f, sep=";")

        print("COLUMNAS:")
        print(df.columns.tolist())

        print("\nPRIMERAS FILAS:")
        print(df.head(5))

    except Exception as e:
        print("ERROR AL LEER EL ARCHIVO:", e)
