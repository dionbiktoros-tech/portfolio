import sqlite3

conn = sqlite3.connect(
    "shop.db",
    check_same_thread=False
)

cur = conn.cursor()

# Пользователи
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
""")

# Товары
cur.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL,
    quantity INTEGER
)
""")

# Корзина
cur.execute("""
CREATE TABLE IF NOT EXISTS cart(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_login TEXT,
    product_name TEXT,
    price REAL,
    quantity INTEGER
)
""")

# Заказы
cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_login TEXT,
    total REAL,
    order_date TEXT
)
""")

# Админ по умолчанию
cur.execute("""
INSERT OR IGNORE INTO users
(login,password,role)
VALUES
('admin','admin123','admin')
""")

# Товары по умолчанию
cur.execute("SELECT COUNT(*) FROM products")

if cur.fetchone()[0] == 0:

    products = [

        ("Крем для лица",
         "Уход за лицом",
         1200,
         50),

        ("Шампунь",
         "Уход за волосами",
         900,
         80),

        ("Бальзам",
         "Уход за волосами",
         750,
         60),

        ("Сыворотка",
         "Уход за лицом",
         1800,
         30),

        ("Тоник",
         "Уход за лицом",
         650,
         70),

        ("Маска для волос",
         "Уход за волосами",
         1400,
         40)
    ]

    cur.executemany("""
    INSERT INTO products
    (name,category,price,quantity)
    VALUES (?,?,?,?)
    """, products)

conn.commit()