# create_downloads.py
import os


def create_files():
    os.makedirs("downloads", exist_ok=True)

    # EXE
    with open("downloads/beauty_store_desktop.exe", "w", encoding="utf-8") as f:
        f.write("BEAUTY STORE DESKTOP\n")
        f.write("=" * 50 + "\n")
        f.write("Версия: 1.0.0\n\n")
        f.write("Установка: запустите файл\n\n")
        for i in range(1000):
            f.write(f"DATA_{i}: " + "X" * 80 + "\n")

    # APK
    with open("downloads/beauty_store_mobile.apk", "w", encoding="utf-8") as f:
        f.write("BEAUTY STORE MOBILE\n")
        f.write("=" * 50 + "\n")
        f.write("Версия: 1.0.0\n\n")
        f.write("Установка: скопируйте на телефон\n\n")
        for i in range(1000):
            f.write(f"DATA_{i}: " + "Y" * 80 + "\n")

    print("✅ Файлы созданы!")


if __name__ == "__main__":
    create_files()