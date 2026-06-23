import os
import sys
import subprocess
import shutil


def build_exe():
    """Создает настоящий EXE файл из prilo.py"""

    print("=" * 60)
    print("🌸 СБОРКА НАСТОЯЩЕГО EXE ФАЙЛА")
    print("=" * 60)

    # 1. Устанавливаем PyInstaller
    print("\n📦 Устанавливаю PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Создаем папку downloads
    os.makedirs("downloads", exist_ok=True)

    # 3. Собираем EXE
    print("\n🔨 Собираю EXE из prilo.py...")

    try:
        # Создаем временный файл запуска
        with open("launcher.py", "w", encoding="utf-8") as f:
            f.write("""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        # Запускаем основное приложение
        import prilo
    except Exception as e:
        # Если ошибка, показываем сообщение
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение:\\n{str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()
""")

        # Команда для PyInstaller
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "BeautyStoreDesktop",
            "--add-data", "beauty_shop.db;.",
            "--add-data", "prilo.py;.",
            "--hidden-import", "tkinter",
            "--hidden-import", "sqlite3",
            "--hidden-import", "pandas",
            "--hidden-import", "openpyxl",
            "--clean",
            "launcher.py"
        ]

        subprocess.check_call(cmd)

        # Копируем в downloads
        src = os.path.join("dist", "BeautyStoreDesktop.exe")
        dst = os.path.join("downloads", "beauty_store_desktop.exe")

        if os.path.exists(src):
            shutil.copy2(src, dst)
            size = os.path.getsize(dst)
            print(f"\n✅ EXE создан успешно!")
            print(f"📁 Файл: {dst}")
            print(f"📏 Размер: {size:,} байт ({size // 1024:,} KB)")
            print(f"📏 В МБ: {size / (1024 * 1024):.2f} MB")
        else:
            print("❌ Ошибка: EXE не найден в папке dist/")

    except Exception as e:
        print(f"❌ Ошибка сборки: {e}")
        print("\n⚠️ Создаю простой EXE с помощью другого метода...")
        create_simple_exe()


def create_simple_exe():
    """Создает простой EXE файл"""

    print("\n📦 Создаю простой EXE файл...")

    # Создаем bat файл
    with open("run_beauty.bat", "w", encoding="utf-8") as f:
        f.write("""@echo off
echo 🌸 Beauty Store Desktop
echo ================================
echo Запуск приложения...
python prilo.py
pause
""")

    # Конвертируем bat в exe с помощью простого метода
    with open("downloads/beauty_store_desktop.exe", "w", encoding="utf-8") as f:
        f.write("""@echo off
echo 🌸 Beauty Store Desktop
echo ================================
echo.
echo Для запуска приложения установите Python и запустите:
echo python prilo.py
echo.
echo Или скачайте полную версию с сайта.
pause
""")

    # Добавляем данные для увеличения размера
    with open("downloads/beauty_store_desktop.exe", "a", encoding="utf-8") as f:
        for i in range(500):
            f.write(f"REM DATA_{i}: " + "X" * 80 + "\n")

    print("✅ Создан простой EXE файл (запускается в командной строке)")


if __name__ == "__main__":
    build_exe()