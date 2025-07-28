import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER,
    product_name TEXT NOT NULL,
    unit_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    is_discounted INTEGER DEFAULT 0,
    discounted_price REAL,
    purchase_date TEXT NOT NULL,
    FOREIGN KEY (shop_id) REFERENCES shops(id)
)
''')

conn.commit()
conn.close()

print("✅ purchases tábla sikeresen létrehozva a data.db-ben.")
