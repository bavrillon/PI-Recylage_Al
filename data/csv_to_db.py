import os
import sqlite3
import pandas as pd

csv_folder = os.path.join(os.path.dirname(__file__), "tables_csv")
db_path = os.path.join(os.path.dirname(__file__), "data.db")

conn = sqlite3.connect(db_path)

for filename in os.listdir(csv_folder):
    if filename.endswith(".csv"):
        table = filename.replace(".csv", "")
        df = pd.read_csv(os.path.join(csv_folder, filename))
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"{table} importée.")

conn.close()




