import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Récupérer la liste des tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    print(f"Traitement de la table : {table}")
    
    # Vérifier si la colonne 'id' existe déjà
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'id' not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN id INTEGER;")
        print(f"Colonne 'id' ajoutée à la table {table}.")
        
        # Remplir la colonne id avec des valeurs uniques
        cursor.execute(f"SELECT rowid FROM {table}")
        rows = cursor.fetchall()
        for idx, (rowid,) in enumerate(rows, start=1):
            cursor.execute(f"UPDATE {table} SET id = ? WHERE rowid = ?", (idx, rowid))
    else:
        print(f"La colonne 'id' existe déjà dans la table {table}.")

conn.commit()
conn.close()
