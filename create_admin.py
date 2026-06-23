import sqlite3
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    # Проверяем существует ли admin
    cursor.execute("SELECT * FROM users WHERE login='admin'")
    admin = cursor.fetchone()

    if admin:
        print("✅ Админ уже существует!")
        print(f"Логин: {admin[1]}")
        print(f"Пароль: admin123")
        return

    # Создаем admin
    hashed = hash_password("admin123")
    cursor.execute("""
                   INSERT INTO users(login, password, email, full_name, role)
                   VALUES (?, ?, ?, ?, ?)
                   """, ("admin", hashed, "admin@shop.com", "Администратор", "admin"))

    conn.commit()
    conn.close()

    print("=" * 50)
    print("✅ АДМИН СОЗДАН!")
    print("=" * 50)
    print("Логин: admin")
    print("Пароль: admin123")
    print("=" * 50)


if __name__ == "__main__":
    create_admin()