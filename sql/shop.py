import sqlite3

class Shop:
    def __init__(self, db_name="shop.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, family TEXT, phone TEXT, email TEXT, is_active INTEGER DEFAULT 1)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, city TEXT, detail TEXT, postal_code TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, brand TEXT, price REAL, stock INTEGER)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id INTEGER, quantity INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(product_id) REFERENCES products(id))''')
        self.conn.commit()

    # --- User Methods ---
    def add_user(self, n, f, p, e):
        self.cursor.execute("INSERT INTO users (name, family, phone, email) VALUES (?,?,?,?)", (n, f, p, e))
        self.conn.commit()
    
    def get_all_users(self):
        return self.cursor.execute("SELECT id, name, family, phone, email FROM users WHERE is_active = 1").fetchall()

    def get_user(self, uid):
        return self.cursor.execute("SELECT id, name, family, phone, email FROM users WHERE id = ? AND is_active = 1", (uid,)).fetchone()
    
    def search_users(self, keyword):
        query = "SELECT id, name, family, phone, email FROM users WHERE (name LIKE ? OR family LIKE ? OR phone LIKE ?) AND is_active = 1"
        pattern = f"%{keyword}%"
        return self.cursor.execute(query, (pattern, pattern, pattern)).fetchall()

    def update_user(self, uid, n, f, p, e):
        self.cursor.execute("UPDATE users SET name=?, family=?, phone=?, email=? WHERE id=?", (n, f, p, e, uid))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_user(self, uid):
        self.cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (uid,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # --- Address Methods ---
    def add_address(self, uid, city, detail, postal_code):
        self.cursor.execute("INSERT INTO addresses (user_id, city, detail, postal_code) VALUES (?,?,?,?)", (uid, city, detail, postal_code))
        self.conn.commit()

    def get_user_addresses(self, uid):
        return self.cursor.execute("SELECT * FROM addresses WHERE user_id = ?", (uid,)).fetchall()

    def update_address(self, aid, city, detail, postal_code):
        self.cursor.execute("UPDATE addresses SET city=?, detail=?, postal_code=? WHERE id=?", (city, detail, postal_code, aid))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_address(self, aid):
        self.cursor.execute("DELETE FROM addresses WHERE id = ?", (aid,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # --- Product & Category Methods ---
    def add_product(self, name, category, brand, price, stock):
        self.cursor.execute("INSERT INTO products (name, category, brand, price, stock) VALUES (?,?,?,?,?)", (name, category, brand, price, stock))
        self.conn.commit()

    def get_all_products(self):
        return self.cursor.execute('SELECT * FROM products').fetchall()

    def get_product(self, pid):
        return self.cursor.execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()

    def get_categories(self):
        res = self.cursor.execute('SELECT DISTINCT category FROM products').fetchall()
        return [row[0] for row in res]

    def get_products_by_category(self, category):
        return self.cursor.execute('SELECT * FROM products WHERE category = ?', (category,)).fetchall()

    def search_products(self, keyword):
        query = "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? OR brand LIKE ?"
        pattern = f"%{keyword}%"
        return self.cursor.execute(query, (pattern, pattern, pattern)).fetchall()

    def update_product(self, pid, name, category, brand, price, stock):
        self.cursor.execute('UPDATE products SET name = ?, category = ?, brand = ?, price = ?, stock = ? WHERE id = ?', (name, category, brand, price, stock, pid))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_stock(self, pid, qty):
        self.cursor.execute('UPDATE products SET stock = stock + ? WHERE id = ?', (qty, pid))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_low_stock(self, threshold=5):
        return self.cursor.execute('SELECT * FROM products WHERE stock <= ?', (threshold,)).fetchall()

    def delete_product(self, pid):
        self.cursor.execute('DELETE FROM products WHERE id = ?', (pid,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # --- Order & Invoice Methods ---
    def add_order(self, uid, pid, qty):
        self.cursor.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (?,?,?)", (uid, pid, qty))
        self.conn.commit()

    def get_user_invoice(self, uid):
        query = '''SELECT p.name, o.quantity, p.price, (o.quantity * p.price) as line_total
                   FROM orders o JOIN products p ON o.product_id = p.id WHERE o.user_id = ?'''
        return self.cursor.execute(query, (uid,)).fetchall()

    def get_invoice_total(self, uid):
        query = '''SELECT SUM(o.quantity * p.price) 
                   FROM orders o JOIN products p ON o.product_id = p.id WHERE o.user_id = ?'''
        res = self.cursor.execute(query, (uid,)).fetchone()
        return res[0] if res[0] is not None else 0
