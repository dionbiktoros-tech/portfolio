from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify, flash
import sqlite3
import random
import hashlib
import re
import os
from collections import Counter
import zipfile

app = Flask(__name__)
app.secret_key = "beauty_store_secret_key_2024"


# ==================== БАЗА ДАННЫХ ====================

def create_database():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       login
                       TEXT
                       UNIQUE,
                       password
                       TEXT,
                       email
                       TEXT,
                       full_name
                       TEXT,
                       phone
                       TEXT,
                       role
                       TEXT
                       DEFAULT
                       'user',
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS products
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT,
                       category
                       TEXT,
                       subcategory
                       TEXT,
                       price
                       INTEGER,
                       image
                       TEXT,
                       description
                       TEXT,
                       brand
                       TEXT,
                       rating
                       REAL,
                       in_stock
                       INTEGER
                       DEFAULT
                       1,
                       views
                       INTEGER
                       DEFAULT
                       0,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)

    conn.commit()

    # Миграция
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN subcategory TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN brand TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN rating REAL")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN in_stock INTEGER DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN views INTEGER DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except:
        pass

    conn.commit()

    # Товары
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        products_data = [
            {"name": "Увлажняющий крем", "category": "Уход за лицом", "subcategory": "Кремы", "price": 1500,
             "brand": "La Roche-Posay", "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03",
             "description": "Интенсивное увлажнение на 24 часа", "rating": 4.8},
            {"name": "Гиалуроновая сыворотка", "category": "Уход за лицом", "subcategory": "Сыворотки", "price": 750,
             "brand": "The Ordinary", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be",
             "description": "Концентрированная сыворотка с гиалуроновой кислотой", "rating": 4.9},
            {"name": "Глиняная маска", "category": "Уход за лицом", "subcategory": "Маски", "price": 950,
             "brand": "COSRX", "image": "https://images.unsplash.com/photo-1612817288484-6f916006741a",
             "description": "Очищающая маска с глиной", "rating": 4.6},
            {"name": "Пилинг для лица", "category": "Уход за лицом", "subcategory": "Пилинги", "price": 1800,
             "brand": "Clarins", "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03",
             "description": "Нежный пилинг для сияния кожи", "rating": 4.7},
            {"name": "Шампунь", "category": "Уход за волосами", "subcategory": "Шампуни", "price": 450,
             "brand": "Nivea", "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9",
             "description": "Увлажняющий шампунь", "rating": 4.4},
            {"name": "Мицеллярная вода", "category": "Косметика", "subcategory": "Очищение", "price": 1200,
             "brand": "Bioderma", "image": "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
             "description": "Мицеллярная вода для чувствительной кожи", "rating": 4.8},
            {"name": "Духи", "category": "Парфюмерия", "subcategory": "Духи", "price": 8500,
             "brand": "Chanel", "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9",
             "description": "Цветочный аромат", "rating": 4.9},
        ]

        for p in products_data:
            in_stock = random.choice([0, 1, 1, 1])
            views = random.randint(0, 500)
            cursor.execute("""
                           INSERT INTO products(name, category, subcategory, price, image, description, brand, rating,
                                                in_stock, views)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, (p["name"], p["category"], p["subcategory"], p["price"], p["image"], p["description"],
                                 p["brand"], p["rating"], in_stock, views))

    # ADMIN
    cursor.execute("SELECT * FROM users WHERE login='admin'")
    admin = cursor.fetchone()

    if admin is None:
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
                       INSERT INTO users(login, password, email, full_name, phone, role)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, ("admin", hashed, "admin@shop.com", "Администратор", "+79999999999", "admin"))

    conn.commit()
    conn.close()


create_database()


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def find_file(filename):
    """Ищет файл в папке downloads с разными вариантами названий"""
    downloads_dir = "downloads"

    if not os.path.exists(downloads_dir):
        return None

    # Получаем список всех файлов в папке downloads
    try:
        files = os.listdir(downloads_dir)
    except:
        return None

    # Ищем файл по разным критериям
    for file in files:
        file_lower = file.lower()

        # Для EXE файла
        if filename.lower().endswith('.exe'):
            # Ищем любой .exe файл
            if file_lower.endswith('.exe'):
                return os.path.join(downloads_dir, file)

        # Для APK файла
        elif filename.lower().endswith('.apk'):
            # Ищем любой .apk файл
            if file_lower.endswith('.apk'):
                return os.path.join(downloads_dir, file)

        # Для ZIP файла
        elif filename.lower().endswith('.zip'):
            # Ищем любой .zip файл
            if file_lower.endswith('.zip'):
                return os.path.join(downloads_dir, file)

        # Для точного совпадения
        elif file == filename or file_lower == filename.lower():
            return os.path.join(downloads_dir, file)

    # Если ничего не найдено, пробуем искать по ключевым словам
    for file in files:
        file_lower = file.lower()
        if filename.lower().replace('_', '') in file_lower.replace('_', ''):
            return os.path.join(downloads_dir, file)

    return None


def create_portable_version():
    """Создает портативную ZIP версию приложения"""
    try:
        os.makedirs("downloads", exist_ok=True)

        zip_path = "downloads/beauty_store_portable.zip"

        # Удаляем старый файл если есть
        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            files_to_add = ["prilo.py", "baza.py", "beauty_shop.db"]
            for file in files_to_add:
                if os.path.exists(file):
                    zipf.write(file)
                    print(f"  ✅ Добавлен {file}")

            readme_content = """🌸 BEAUTY STORE - ПОРТАТИВНАЯ ВЕРСИЯ

📦 ЧТО ВНУТРИ:
- prilo.py - Главное приложение
- baza.py - Создание базы данных
- beauty_shop.db - База данных

🚀 ДЛЯ ЗАПУСКА:
1. Распакуйте архив
2. Установите Python 3.8+
3. pip install pandas openpyxl
4. python prilo.py

🔐 ДАННЫЕ ДЛЯ ВХОДА:
Выберите сотрудника из списка

© 2024 Beauty Store
"""
            with open("README.txt", "w", encoding="utf-8") as f:
                f.write(readme_content)
            zipf.write("README.txt")
            os.remove("README.txt")

        print("✅ Портативная версия создана!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


# ==================== ГЛАВНАЯ ====================

@app.route("/")
def home():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = [cat[0] for cat in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL ORDER BY brand")
    brands = [b[0] for b in cursor.fetchall()]

    category_filter = request.args.get('category', '')
    subcategory_filter = request.args.get('subcategory', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    brand_filter = request.args.get('brand', '')
    in_stock_filter = request.args.get('in_stock', '')

    subcategories = []
    if category_filter:
        cursor.execute("SELECT DISTINCT subcategory FROM products WHERE category = ? ORDER BY subcategory",
                       (category_filter,))
        subcategories = [s[0] for s in cursor.fetchall()]

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    if subcategory_filter:
        query += " AND subcategory = ?"
        params.append(subcategory_filter)

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    if min_price:
        query += " AND price >= ?"
        params.append(int(min_price))

    if max_price:
        query += " AND price <= ?"
        params.append(int(max_price))

    if brand_filter:
        query += " AND brand = ?"
        params.append(brand_filter)

    if in_stock_filter == "in":
        query += " AND in_stock = 1"
    elif in_stock_filter == "out":
        query += " AND in_stock = 0"

    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'name_asc':
        query += " ORDER BY name ASC"
    elif sort_by == 'name_desc':
        query += " ORDER BY name DESC"
    elif sort_by == 'rating':
        query += " ORDER BY rating DESC"
    else:
        query += " ORDER BY id"

    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()

    if "cart" not in session:
        session["cart"] = []

    return render_template(
        "index.html",
        products=products,
        categories=categories,
        brands=brands,
        subcategories=subcategories,
        user=session.get("user"),
        cart_count=len(session["cart"]),
        current_category=category_filter,
        current_subcategory=subcategory_filter,
        search_query=search_query,
        sort_by=sort_by,
        min_price=min_price,
        max_price=max_price,
        brand_filter=brand_filter,
        in_stock_filter=in_stock_filter
    )


# ==================== ПОЛУЧИТЬ ПОДКАТЕГОРИИ ====================

@app.route("/get_subcategories")
def get_subcategories():
    category = request.args.get('category', '')
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT subcategory FROM products WHERE category = ? ORDER BY subcategory", (category,))
    subcategories = [s[0] for s in cursor.fetchall()]
    conn.close()

    return jsonify({"subcategories": subcategories})


# ==================== РЕГИСТРАЦИЯ ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()

        errors = []

        if not login or len(login) < 3:
            errors.append("Логин должен быть не менее 3 символов")

        if not password or len(password) < 6:
            errors.append("Пароль должен быть не менее 6 символов")

        if password != confirm_password:
            errors.append("Пароли не совпадают")

        if not email or not validate_email(email):
            errors.append("Введите корректный email")

        if errors:
            return render_template("register.html", errors=errors, form_data=request.form)

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            conn.close()
            return render_template("register.html", errors=["Пользователь с таким логином уже существует"],
                                   form_data=request.form)

        hashed = hash_password(password)
        cursor.execute("""
                       INSERT INTO users(login, password, email, full_name, role)
                       VALUES (?, ?, ?, ?, ?)
                       """, (login, hashed, email, full_name, "user"))

        conn.commit()
        conn.close()

        flash("Регистрация успешна! Войдите в систему.", "success")
        return redirect("/login")

    return render_template("register.html")


# ==================== ВХОД ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        if not login or not password:
            return render_template("login.html", error="Введите логин и пароль")

        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()

        hashed = hash_password(password)
        cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, hashed))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user"] = user[1]
            session["role"] = user[6] if len(user) > 6 else "user"
            session["full_name"] = user[4] if len(user) > 4 and user[4] else user[1]

            flash(f"Добро пожаловать, {session['full_name']}!", "success")
            return redirect("/profile")
        else:
            return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")


# ==================== ПРОФИЛЬ ====================

@app.route("/profile")
def profile():
    if "user" not in session:
        flash("Пожалуйста, войдите в систему", "warning")
        return redirect("/login")

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login = ?", (session["user"],))
    user = cursor.fetchone()
    conn.close()

    return render_template(
        "profile.html",
        user=user,
        login=session["user"],
        role=session.get("role", "user"),
        full_name=session.get("full_name", session["user"])
    )


# ==================== ВЫХОД ====================

@app.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы", "info")
    return redirect("/")


# ==================== АНАЛИТИКА ====================

@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT category, COUNT(*) FROM products GROUP BY category")
    categories_stats = cursor.fetchall()

    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM products")
    price_stats = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM products WHERE in_stock = 1")
    in_stock_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products WHERE in_stock = 0")
    out_stock_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "analytics.html",
        products_count=products_count,
        users_count=users_count,
        categories_stats=categories_stats,
        min_price=price_stats[0],
        max_price=price_stats[1],
        avg_price=round(price_stats[2], 2),
        in_stock_count=in_stock_count,
        out_stock_count=out_stock_count
    )


# ==================== КОРЗИНА ====================

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET views = views + 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Товар добавлен в корзину!", "success")
    return redirect(request.referrer or "/")


@app.route("/cart")
def cart():
    if "cart" not in session:
        session["cart"] = []

    ids = session["cart"]
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    products = []
    total = 0

    cart_counts = Counter(ids)

    for product_id, count in cart_counts.items():
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()

        if product:
            product_with_count = list(product) + [count]
            products.append(product_with_count)
            total += product[3] * count

    conn.close()

    return render_template("cart.html", products=products, total=total)


@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    if "cart" in session:
        if id in session["cart"]:
            session["cart"].remove(id)
            session.modified = True
    return redirect("/cart")


@app.route("/clear_cart")
def clear_cart():
    session["cart"] = []
    session.modified = True
    flash("Корзина очищена", "info")
    return redirect("/cart")


# ==================== СКАЧИВАНИЕ ====================

@app.route("/downloads")
def downloads_page():
    # Ищем файлы в папке downloads
    desktop_path = find_file("beauty_store_desktop.exe")  # ищет любой .exe
    mobile_path = find_file("beauty_store_mobile.apk")  # ищет любой .apk
    portable_path = find_file("beauty_store_portable.zip")  # ищет любой .zip

    # Если портативной версии нет - создаем
    if not portable_path:
        create_portable_version()
        portable_path = find_file("beauty_store_portable.zip")

    files = {
        'desktop': desktop_path is not None,
        'mobile': mobile_path is not None,
        'portable': portable_path is not None
    }

    sizes = {}
    if files['desktop']:
        sizes['desktop'] = f"{os.path.getsize(desktop_path) // 1024:,} KB"
    else:
        sizes['desktop'] = "Файл не найден"

    if files['mobile']:
        sizes['mobile'] = f"{os.path.getsize(mobile_path) // 1024:,} KB"
    else:
        sizes['mobile'] = "Файл не найден"

    if files['portable']:
        sizes['portable'] = f"{os.path.getsize(portable_path) // 1024:,} KB"
    else:
        sizes['portable'] = "Файл не найден"

    return render_template(
        "downloads.html",
        user=session.get("user"),
        cart_count=len(session.get("cart", [])),
        files=files,
        sizes=sizes
    )


@app.route("/download_desktop")
def download_desktop():
    try:
        file_path = find_file("beauty_store_desktop.exe")
        if file_path:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            return send_from_directory(
                directory=directory,
                path=filename,
                as_attachment=True,
                download_name="BeautyStoreDesktop.exe"
            )
        else:
            flash("Файл не найден. Попробуйте скачать портативную версию.", "error")
            return redirect("/downloads")
    except Exception as e:
        flash(f"Ошибка: {str(e)}", "error")
        return redirect("/downloads")


@app.route("/download_mobile")
def download_mobile():
    try:
        file_path = find_file("beauty_store_mobile.apk")
        if file_path:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            return send_from_directory(
                directory=directory,
                path=filename,
                as_attachment=True,
                download_name="BeautyStoreMobile.apk"
            )
        else:
            flash("Файл не найден", "error")
            return redirect("/downloads")
    except Exception as e:
        flash(f"Ошибка: {str(e)}", "error")
        return redirect("/downloads")


@app.route("/download_portable")
def download_portable():
    try:
        file_path = find_file("beauty_store_portable.zip")

        if not file_path:
            create_portable_version()
            file_path = find_file("beauty_store_portable.zip")

        if file_path:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            return send_from_directory(
                directory=directory,
                path=filename,
                as_attachment=True,
                download_name="BeautyStorePortable.zip"
            )
        else:
            flash("Не удалось создать портативную версию", "error")
            return redirect("/downloads")
    except Exception as e:
        flash(f"Ошибка: {str(e)}", "error")
        return redirect("/downloads")


# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    # Создаем папку downloads если её нет
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    print("\n🌸 Beauty Store запущен!")
    print(f"🌐 Откройте: http://localhost:5000")
    print("\n📦 Поиск файлов для скачивания:")

    # Проверяем файлы
    desktop = find_file("beauty_store_desktop.exe")
    mobile = find_file("beauty_store_mobile.apk")
    portable = find_file("beauty_store_portable.zip")

    if desktop:
        size = os.path.getsize(desktop) // 1024
        print(f"  ✅ Десктоп: {desktop} ({size} KB)")
    else:
        print("  ❌ Десктоп: не найден")

    if mobile:
        size = os.path.getsize(mobile) // 1024
        print(f"  ✅ Мобильный: {mobile} ({size} KB)")
    else:
        print("  ❌ Мобильный: не найден")

    if portable:
        size = os.path.getsize(portable) // 1024
        print(f"  ✅ Портативный: {portable} ({size} KB)")
    else:
        print("  ❌ Портативный: не найден")
        print("  📦 Создаю портативную версию...")
        create_portable_version()

    app.run(debug=True, host="0.0.0.0", port=5000)