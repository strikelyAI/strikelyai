import pandas as pd
import glob

# Buscar todos los CSV en la carpeta datos
files = glob.glob(r"C:\Users\Usuario\ANALISIS DEPORTIVO IA\datos\*.csv")

# Leer todos y unirlos
all_data = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

# Guardar en un solo CSV
all_data.to_csv(r"C:\Users\Usuario\ANALISIS DEPORTIVO IA\datos\laliga.csv", index=False)
print("Todos los CSV unidos en laliga.csv")
