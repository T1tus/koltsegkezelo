import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('''
    ALTER TABLE purchases ADD COLUMN purchase_group_id INTEGER;
''')

conn.commit()
conn.close()

print("✅ Shops tábla létrehozva.")
