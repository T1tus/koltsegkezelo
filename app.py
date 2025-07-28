# app.py

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
DB = 'data.db'

@app.route('/shops', methods=['GET', 'POST'])
def shops():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form.get('location', '')
        note = request.form.get('note', '')
        try:
            c.execute('INSERT INTO shops (name, location, note) VALUES (?, ?, ?)', (name, location, note))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # ha már létezik ilyen bolt, nem adja hozzá újra

    c.execute('SELECT * FROM shops ORDER BY name')
    shops = c.fetchall()
    conn.close()
    return render_template('shops.html', shops=shops)

@app.route('/shops/edit/<int:shop_id>', methods=['GET', 'POST'])
def edit_shop(shop_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        note = request.form['note']
        c.execute('UPDATE shops SET name=?, location=?, note=? WHERE id=?', (name, location, note, shop_id))
        conn.commit()
        conn.close()
        return redirect(url_for('shops'))

    c.execute('SELECT * FROM shops WHERE id=?', (shop_id,))
    shop = c.fetchone()
    conn.close()
    return render_template('edit_shop.html', shop=shop)


@app.route('/shops/delete/<int:shop_id>', methods=['POST'])
def delete_shop(shop_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('DELETE FROM shops WHERE id=?', (shop_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('shops'))


# Adatbázis inicializálása
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                category TEXT,
                amount REAL,
                date TEXT,
                note TEXT
            )
        ''')
    print("Adatbázis készen áll.")

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/transactions')
def transactions():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM transactions ORDER BY date DESC")
        rows = c.fetchall()

    # Egyenleg számítása
    c.execute("SELECT type, amount FROM transactions")
    transactions = c.fetchall()
    balance = 0
    for t_type, amount in transactions:
        if t_type == "bevétel":
            balance += amount
        elif t_type == "kiadás":
            balance -= amount
   
    # Aktuális dátum átadása a sablonnak    
    today = datetime.now().strftime('%y-%m-%d')
    return render_template('transactions.html', rows=rows, balance=balance, today=today)


@app.route('/add', methods=['POST'])
def add():
    t_type = request.form['type']
    category = request.form['category']
    amount = float(request.form['amount'])
    date = request.form['date']
    note = request.form.get('note', '')
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO transactions (type, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
                  (t_type, category, amount, date, note))
        conn.commit()
    return redirect('/transactions')


@app.route('/vasarlasok')
def vasarlasok():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Lekérdezzük a vásárlási csoportokat, boltokkal együtt
    c.execute('''
        SELECT 
            p.purchase_group_id,
            s.name AS shop_name,
            s.location,
            s.note,
            p.purchase_date,
            SUM(p.total_price) AS total_sum
        FROM purchases p
        JOIN shops s ON p.shop_id = s.id
        GROUP BY p.purchase_group_id
        ORDER BY p.purchase_date DESC, p.purchase_group_id DESC
    ''')
    grouped = c.fetchall()

    # Minden csoporthoz lekérdezzük a termékeket
    details = {}
    for row in grouped:
        group_id = row['purchase_group_id']
        c.execute('''
            SELECT 
                product_name,
                quantity,
                unit_price,
                is_discounted,
                discounted_price,
                total_price
            FROM purchases
            WHERE purchase_group_id = ?
        ''', (group_id,))
        details[group_id] = c.fetchall()

    conn.close()

    return render_template('vasarlasok.html', grouped_purchases=grouped, all_details=details)




@app.route('/vasarlasok/uj', methods=['GET', 'POST'])
def uj_vasarlas():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Boltok lekérdezése a legördülő listához
    c.execute('SELECT id, name FROM shops')
    shops = c.fetchall()

    if request.method == 'POST':
        shop_id = request.form['shop_id']
        purchase_date = request.form['purchase_date']

        # 1. Beszúrunk egy új purchase_group_id-t a vásárlás azonosítására
        purchase_group_id = str(uuid.uuid4())
        

        # 2. Tömbként kérjük le a tételek adatait
        product_names = request.form.getlist('product_name[]')
        unit_prices = request.form.getlist('unit_price[]')
        quantities = request.form.getlist('quantity[]')
        is_discounteds = request.form.getlist('is_discounted[]')
        discounted_prices = request.form.getlist('discounted_price[]')

        # 3. Végigmegyünk a tételeken és mindegyiket beszúrjuk a purchases táblába
        for i in range(len(product_names)):
            product_name = product_names[i]
            unit_price = float(unit_prices[i])
            quantity = int(quantities[i])
            is_discounted = 1 if i < len(is_discounteds) and is_discounteds[i] == 'on' else 0
            discounted_price = discounted_prices[i] if i < len(discounted_prices) and discounted_prices[i] != '' else None
            discounted_price = float(discounted_price) if discounted_price else None

            total_price = (discounted_price if is_discounted and discounted_price else unit_price) * quantity

            c.execute('''
                INSERT INTO purchases 
                (shop_id, product_name, unit_price, quantity, total_price, is_discounted, discounted_price, purchase_date, purchase_group_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (shop_id, product_name, unit_price, quantity, total_price, is_discounted, discounted_price, purchase_date, purchase_group_id))

        conn.commit()
        conn.close()
        return redirect('/vasarlasok')

    conn.close()
    return render_template('uj_vasarlas.html', shops=shops)



@app.context_processor
def inject_now():
    return {'now': datetime.now}


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
