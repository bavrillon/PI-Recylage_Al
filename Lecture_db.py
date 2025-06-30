import sqlite3

# Connexion à la base
conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

# Liste des tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables :", tables)

# Pour chaque table, afficher les colonnes
for table_name in tables:
    table = table_name[0]
    print(f"\nStructure de la table '{table}' :")
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()
    for col in columns:
        print(col)

conn.close()
