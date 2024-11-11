from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Database setup function
def initialize_db():
    if not os.path.exists('inventory_db.sqlite'):
        conn = sqlite3.connect('inventory_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                supplier TEXT,
                status TEXT DEFAULT 'active',
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("Database and table created successfully.")

# Call the database setup function when app.py starts
initialize_db()

# Database connection helper function
def connect_db():
    return sqlite3.connect('inventory_db.sqlite')

# Routes

# Home page to display items
@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE status = 'active'")
    items = cursor.fetchall()
    conn.close()
    return render_template('index.html', items=items)

# Add a new item
@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    description = request.form['description']
    quantity = request.form['quantity']
    price = request.form['price']
    supplier = request.form['supplier']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, description, quantity, price, supplier) VALUES (?, ?, ?, ?, ?)",
                   (name, description, quantity, price, supplier))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Move item to recycle bin
@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET status = 'recycle' WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Display items in recycle bin
@app.route('/recycle-bin')
def recycle_bin():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE status = 'recycle'")
    items = cursor.fetchall()
    conn.close()
    return render_template('recycle_bin.html', items=items)

# Restore item from recycle bin
@app.route('/restore/<int:item_id>')
def restore_item(item_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET status = 'active' WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('recycle_bin'))

@app.route('/permanently_delete/<int:item_id>', methods=['POST'])
def permanently_delete(item_id):
    # Connect to the correct database and delete from the 'items' table
    conn = sqlite3.connect('inventory_db.sqlite')  # Make sure it's using the correct database file
    c = conn.cursor()

    # DELETE the item from the 'items' table, not 'inventory'
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()  # Commit the delete to the database
    conn.close()

    # Redirect to the recycle bin page after deletion
    return redirect(url_for('recycle_bin'))


if __name__ == '__main__':
    app.run(debug=True)
