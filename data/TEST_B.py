from db_tools import Database

db = Database("data_TEST_B.db")

############# CREATION DB #################

import sqlite3
import os
"""
# Nom du fichier SQL à importer
sql_file = os.path.join(os.path.dirname(__file__),'TEST_skeleton_db.sql') 

# Nom du fichier SQLite à créer
db_file = os.path.join(os.path.dirname(__file__),'data_TEST_B.db')

# Lire le contenu du fichier SQL
with open(sql_file, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Créer une base de données SQLite et exécuter le script
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.executescript(sql_script)
conn.commit()
conn.close()

print(f"La base de données SQLite a été créée avec succès dans le fichier '{db_file}'.")

"""

############# MODIF DB_TEST.db ##########

import pandas as pd

csv_folder = os.path.join(os.path.dirname(__file__), "TEST_tables_csv")
db_path = os.path.join(os.path.dirname(__file__), "data_TEST_B.db")

conn = sqlite3.connect(db_path)

for filename in os.listdir(csv_folder):
    if filename.endswith(".csv"):
        table = filename.replace(".csv", "").replace(" ", "_")
        df = pd.read_csv(os.path.join(csv_folder, filename), sep=";")
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"{table} importée.")
conn.close()


############# TEST ##########

test = db.optimise_utilisation_scrap('PAR', 1, 0)

print(test)