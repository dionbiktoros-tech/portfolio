import os


def create_files():
    os.makedirs("downloads", exist_ok=True)

    with open("downloads/beauty_store_desktop.exe", "w", encoding="utf-8") as f:
        f.write("Beauty Store Desktop\n")
        f.write("=" * 50 + "\n")
        f.write("Версия: 1.0.0\n\n")
        f.write("Инструкция:\n")
        f.write("1. Запустите файл\n")
        f.write("2. Следуйте инструкциям\n\n")
        for i in range(500):
            f.write(f"DATA_{i}: " + "X" * 80 + "\n")

    with open("downloads/beauty_store_mobile.apk", "w", encoding="utf-8") as f:
        f.write("Beauty Store Mobile\n")
        f.write("=" * 50 + "\n")
        f.write("Версия: 1.0.0\n\n")
        f.write("Инструкция:\n")
        f.write("1. Скопируйте на телефон\n")
        f.write("2. Откройте файл\n")
        f.write("3. Установите\n\n")
        for i in range(500):
            f.write(f"DATA_{i}: " + "Y" * 80 + "\n")

    print("✅ Файлы созданы в папке downloads/")


if __name__ == "__main__":
    create_files()