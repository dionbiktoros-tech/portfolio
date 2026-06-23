import os
import zipfile


def create_portable():
    os.makedirs("downloads", exist_ok=True)

    with zipfile.ZipFile("downloads/beauty_store_portable.zip", "w") as zipf:
        for file in ["prilo.py", "baza.py", "beauty_shop.db"]:
            if os.path.exists(file):
                zipf.write(file)
                print(f"✅ Добавлен {file}")

        readme = """🌸 BEAUTY STORE - ПОРТАТИВНАЯ ВЕРСИЯ

Для запуска:
1. Распакуйте архив
2. Установите Python 3.8+
3. pip install pandas openpyxl
4. python prilo.py

Данные для входа: выберите сотрудника из списка
"""
        with open("README.txt", "w", encoding="utf-8") as f:
            f.write(readme)
        zipf.write("README.txt")
        os.remove("README.txt")

    print("✅ Портативная версия создана!")


if __name__ == "__main__":
    create_portable()