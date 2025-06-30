import pandas as pd
import sqlite3

# Nom de ton fichier Excel
excel_file = "data.xlsx"

# Charger le fichier Excel
xls = pd.ExcelFile(excel_file)

# Créer une base de données SQLite
conn = sqlite3.connect("data.db")

# Pour chaque feuille, créer une table
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    # Nettoyer le nom de la feuille pour l'utiliser comme nom de table
    table_name = sheet_name.strip().replace(" ", "_")
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Feuille '{sheet_name}' importée en table '{table_name}'.")

conn.close()
print("Conversion terminée.")
