import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS purchase_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER NOT NULL,
    purchase_date TEXT NOT NULL,
    note TEXT,
    FOREIGN KEY (shop_id) REFERENCES shops(id)
)
''')

conn.commit()
conn.close()

print("✅ purchases_group tábla sikeresen létrehozva a data.db-ben.")
