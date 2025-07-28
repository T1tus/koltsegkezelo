import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Új mező hozzáadása a purchases táblához, ha még nincs
try:
    c.execute('ALTER TABLE purchases ADD COLUMN purchase_group_id TEXT')
    print("purchase_group_id oszlop hozzáadva.")
except sqlite3.OperationalError:
    print("purchase_group_id oszlop már létezik.")

conn.commit()
conn.close()