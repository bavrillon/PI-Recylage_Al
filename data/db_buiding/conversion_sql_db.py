import sqlite3
import os

# Nom du fichier SQL à importer
sql_file = os.path.join(os.path.dirname(__file__),'skeleton_db.sql') 

# Nom du fichier SQLite à créer
db_file = 'data.db'

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
