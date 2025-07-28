import sqlite3

DB = 'data.db'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Ellenőrizzük, hogy az oszlopok már léteznek-e, hogy ne dobjon hibát
def column_exists(table, column):
    c.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in c.fetchall()]
    return column in columns

if not column_exists('shops', 'location'):
    c.execute("ALTER TABLE shops ADD COLUMN location TEXT DEFAULT ''")

if not column_exists('shops', 'note'):
    c.execute("ALTER TABLE shops ADD COLUMN note TEXT DEFAULT ''")

conn.commit()
conn.close()

print("A shops tábla sikeresen bővítve lett location és note oszlopokkal.")
