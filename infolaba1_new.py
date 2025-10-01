import os
import json

def ask_path():
    #запрос и поиск каталога
    path = input("Введите путь к каталогу: ").strip()
    if not os.path.exists(path):
        print("Путь не найден.")
        return None
    if not os.path.isdir(path):
        print("Это не каталог.")
        return None
    return os.path.abspath(path)

def create_hashfile(filepath):
    # считаем хэш
    h = 0
    with open(filepath, "rb") as f:
        while True:
            b1 = f.read(1)
            if not b1:
                break
            b2 = f.read(1)
            if not b2:
                b2 = b"\x00"  # дополняем нулями
            num = (b1[0] << 8) | b2[0]  # соединяем в 16 бит
            h ^= num
    return h

def scan_dir(root, ignore_file):
    # проходим по каталогу и собираем хэши
    hashes = {}
    for current_dir, _, files in os.walk(root):
        for name in files:
            filepath = os.path.join(current_dir, name)
            if os.path.abspath(filepath) == ignore_file:
                continue  # пропускаем файл с хэшами
            rel_path = os.path.relpath(filepath, root)
            try:
                hashes[rel_path] = create_hashfile(filepath)
            except Exception as e:
                print(f"Ошибка при чтении {rel_path}: {e}")
    return hashes

def main():
    root = ask_path()
    if not root:
        return

    hash_file = os.path.join(root, "hash.json")

    if not os.path.exists(hash_file):
        # первый запуск
        print("Файл hash.json не найден. создание...")
        hashes = scan_dir(root, hash_file)
        with open(hash_file, "w", encoding="utf-8") as f:
            json.dump(hashes, f, ensure_ascii=False, indent=4)
        print(f"Хэши сохранены для {len(hashes)} файлов.")
    else:
        # повторный запуск
        print("Файл hash.json найден, проверяем...")
        with open(hash_file, "r", encoding="utf-8") as f:
            old_hashes = json.load(f)

        new_hashes = scan_dir(root, hash_file)

        changed = False

        # проверка на удалённые или изменённые
        for path, old_h in old_hashes.items():
            if path not in new_hashes:
                print("Файл удалён:", path)
                changed = True
            elif new_hashes[path] != old_h:
                print("Файл изменён:", path)
                changed = True

        # проверка на новые файлы
        for path in new_hashes:
            if path not in old_hashes:
                print("Файл добавлен:", path)
                changed = True

        if not changed:
            print("Каталог соответствует файлу с хэшами, изменений нет.")

        print("Завершено ^.^")

if __name__ == "__main__":
    main()
