#!/usr/bin/env python3
"""
Простая парольная система (студенческий стиль).
Запуск:
    python password_app.py              # спросит путь к файлу пароля
или
    python password_app.py /path/to/hash.txt

Файл пароля:
 - Если его нет — программа завершает работу (по условию).
 - Если в файле содержится строка MAGIC  -> первый запуск: просит новый пароль, проверяет сложность, сохраняет хэш.
 - Если в файле содержится BLOCKED -> программа заблокирована.
 - Иначе в файле хранится число — хэш пароля. Программа требует ввод пароля, до 3 попыток.
   Если попытки исчерпаны — записывает BLOCKED.
Хэш: читаем поток байт, разбиваем на 16-битные слова (big-endian: первый байт = старший),
      если не хватает байта — дополняем нулём, затем XOR всех 16-битных слов.
"""

import sys
from pathlib import Path

MAGIC = "MAGIC"
BLOCKED = "BLOCKED"
MAX_ATTEMPTS = 3
MIN_LENGTH = 6


def xor16_hash_bytes(data: bytes) -> int:
    """Вычисляет хэш по алгоритму: читаем как поток байт, парой формируем 16-битное слово (big-endian),
    если последний байт один — дополняем нулём, XOR всех слов -> возвращаем целое (0..65535)."""
    h = 0
    n = len(data)
    i = 0
    while i < n:
        high = data[i]
        low = data[i + 1] if (i + 1) < n else 0
        word = (high << 8) | low
        h ^= word
        i += 2
    # Обрежем в 16 бит для явности (не обязательно, но показывает семантику)
    return h & 0xFFFF


def hash_from_file(path: Path) -> int:
    """Считает тот же XOR-хэш из содержимого бинарного файла."""
    h = 0
    with path.open("rb") as f:
        while True:
            b1 = f.read(1)
            if not b1:
                break
            b2 = f.read(1)
            high = b1[0]
            low = b2[0] if b2 else 0
            word = (high << 8) | low
            h ^= word
    return h & 0xFFFF


def hash_from_password_str(password: str) -> int:
    """Формируем байтовый поток от строки (utf-8) и считаем xor16 хэш."""
    b = password.encode("utf-8")
    return xor16_hash_bytes(b)


def check_password_complexity(password: str) -> bool:
    """Проверяет сложность:
    - не менее MIN_LENGTH символов
    - оценивает категории: латиница нижний/верх, кириллица нижний/верх, цифра/спецсимвол
    Требуем минимум 5 категорий (как в примере на Java) — строгая проверка.
    """
    if len(password) < MIN_LENGTH:
        return False

    has_latin_lower = False
    has_latin_upper = False
    has_cyrillic_lower = False
    has_cyrillic_upper = False
    has_digit_or_sign = False

    for ch in password:
        code = ord(ch)
        # латиница
        if 'a' <= ch <= 'z':
            has_latin_lower = True
        elif 'A' <= ch <= 'Z':
            has_latin_upper = True
        # кириллица (основной диапазон)
        elif '\u0430' <= ch <= '\u044f':  # а–я
            has_cyrillic_lower = True
        elif '\u0410' <= ch <= '\u042f':  # А–Я
            has_cyrillic_upper = True
        # цифры или прочие знаки (не буквы и не пробелы)
        elif ch.isdigit() or (not ch.isalnum()):
            has_digit_or_sign = True
        else:
            # другие символы (например, диакритика) можно отнести к "знакам"
            if not ch.isalnum():
                has_digit_or_sign = True

    count = sum([has_latin_lower, has_latin_upper,
                 has_cyrillic_lower, has_cyrillic_upper, has_digit_or_sign])
    return count >= 5


def read_password_file_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def write_password_file_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def ask(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def main():
    # Получаем путь к файлу пароля: аргумент командной строки или спрашиваем у пользователя
    if len(sys.argv) >= 2:
        pwd_path = Path(sys.argv[1])
    else:
        user_input = ask("Укажите полный путь к файлу пароля (например C:\\folder\\hash.txt или /home/user/hash.txt): ").strip()
        if not user_input:
            print("Путь не указан — завершаю работу.")
            return
        pwd_path = Path(user_input)

    # Если файла нет — по условию программа прекращает работу
    if not pwd_path.exists():
        print(f"Файл пароля не найден по указанному пути: {pwd_path}")
        print("Создайте файл и запишите в него MAGIC (заглавными) для первого запуска, затем перезапустите программу.")
        return

    # Читаем содержимое файла как текст (файл с хэшем хранится как текст с числом или MAGIC/BLOCKED)
    content = read_password_file_text(pwd_path)

    if content == MAGIC:
        # Первый запуск: требуется создание пароля
        print("Первый запуск: создаём пароль.")
        new_pass = ask("Введите новый пароль: ")
        if not check_password_complexity(new_pass):
            print(f"Пароль не прошёл проверку сложности. Требуется минимум {MIN_LENGTH} символов "
                  "и разнообразие символов (латиница, кириллица, регистр, цифры/знаки).")
            return
        new_hash = hash_from_password_str(new_pass)
        write_password_file_text(pwd_path, str(new_hash))
        print("Пароль установлен и хэш сохранён в файл.")
        return

    if content == BLOCKED:
        print("Программа заблокирована (в файле стоит метка BLOCKED).")
        return

    # Ожидаем, что в файле хранится хэш (число). Если нет — сообщаем об ошибке.
    try:
        stored_hash = int(content)
    except ValueError:
        print("Содержимое файла пароля не распознано (не MAGIC, не BLOCKED, не число).")
        print("Завершаю работу во избежание небезопасных действий.")
        return

    # Запрашиваем пароль до MAX_ATTEMPTS раз
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        attempt_pass = ask("Введите пароль: ")
        computed = hash_from_password_str(attempt_pass)
        if computed == stored_hash:
            print("Доступ разрешён — хэши совпали.")
            # Здесь можно добавить основную работу программы
            return
        else:
            attempts -= 1
            print(f"Неверный пароль. Осталось попыток: {attempts}")

    # Если вышли из цикла — блокируем
    write_password_file_text(pwd_path, BLOCKED)
    print("Превышено число попыток. Программа заблокирована (в файл записано BLOCKED).")


if __name__ == "__main__":
    main()
