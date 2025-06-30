import sqlite3


conn = sqlite3.connect('data.db')
cursor = conn.cursor()

##### Rajoute la colonne id dans la table alloy #####
# Vérifier si la colonne 'id' existe déjà
cursor.execute("PRAGMA table_info(alloy);")
columns = [col[1] for col in cursor.fetchall()]
if 'id' not in columns:
    cursor.execute("ALTER TABLE alloy ADD COLUMN id INTEGER;")
    print("Colonne 'id' ajoutée.")
else:
    print("Colonne 'id' existe déjà.")

# Remplir la colonne id avec des valeurs uniques (1, 2, 3, ...)
cursor.execute("SELECT rowid FROM alloy")
rows = cursor.fetchall()
for idx, (rowid,) in enumerate(rows, start=1):
    cursor.execute("UPDATE alloy SET id = ? WHERE rowid = ?", (idx, rowid))

conn.commit()
conn.close()

