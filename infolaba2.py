#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import sys
import getpass

MAGIC_TOKEN = "MAGIC"
BLOCKED_TOKEN = "BLOCKED"
MIN_LENGTH = 6
REQUIRED_CATEGORY_COUNT = 5


def xor_hash_from_bytes(data: bytes) -> int:
    result = 0
    n = len(data)
    i = 0
    while i < n:
        b1 = data[i]
        b2 = data[i + 1] if (i + 1) < n else 0
        word = (b1 << 8) | b2
        result ^= word
        i += 2
    return result


def hash_from_text(text: str, encoding: str = "utf-8") -> int:
    b = text.encode(encoding)
    return xor_hash_from_bytes(b)


def check_password_complexity(password: str) -> (bool, str):
    if len(password) < MIN_LENGTH:
        return False, f"Пароль слишком короткий (нужно >= {MIN_LENGTH} символов)."

    has_latin_lower = any('a' <= ch <= 'z' for ch in password)
    has_latin_upper = any('A' <= ch <= 'Z' for ch in password)
    has_cyrillic_lower = any((0x0400 <= ord(ch) <= 0x04FF) and ch.islower() for ch in password)
    has_cyrillic_upper = any((0x0400 <= ord(ch) <= 0x04FF) and ch.isupper() for ch in password)
    has_digit_or_sign = any(ch.isdigit() or (not ch.isalnum()) for ch in password)

    count = sum([has_latin_lower, has_latin_upper,
                 has_cyrillic_lower, has_cyrillic_upper,
                 has_digit_or_sign])

    if count < REQUIRED_CATEGORY_COUNT:
        return False, (
            "Пароль не содержит достаточного числа категорий символов.\n"
            "Требуется сочетание: латиница (ниж/верх), кириллица (ниж/верх), цифры/знаки — "
            f"не менее {REQUIRED_CATEGORY_COUNT} из этих категорий."
        )

    return True, "OK"


def read_password_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def write_password_file(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Простая парольная система (учебное задание).")
    parser.add_argument("file", nargs="?", help="Путь к файлу пароля (hash-файл).")
    args = parser.parse_args()

    if args.file:
        file_path = Path(args.file)
    else:
        raw = input("Укажите путь к файлу пароля (например C:\\\\... или /home/...): ").strip()
        if raw == "":
            print("Путь не указан. Завершение.")
            sys.exit(1)
        file_path = Path(raw)

    if not file_path.exists():
        print(f"Файл пароля не найден: {file_path}")
        print("По условию задания программа завершает работу при отсутствии файла пароля.")
        print("Создайте файл с текстом 'MAGIC' в нём, чтобы выполнить первый запуск.")
        sys.exit(1)

    try:
        content = read_password_file(file_path)
    except Exception as e:
        print("Ошибка чтения файла:", e)
        sys.exit(1)

    if content == MAGIC_TOKEN:
        print("Первый запуск: файл содержит магическое слово. Установите новый пароль.")
        new_pass = getpass.getpass("Введите новый пароль: ")

        ok, msg = check_password_complexity(new_pass)
        if not ok:
            print("Ошибка сложности пароля:", msg)
            sys.exit(1)

        h = hash_from_text(new_pass)
        write_password_file(file_path, str(h))
        print("Пароль установлен — хеш записан в файл. Запуск завершён успешно.")

    elif content == BLOCKED_TOKEN:
        print("Система заблокирована (в файле стоит метка BLOCKED). Обратитесь к администратору.")
        sys.exit(1)

    else:
        try:
            stored_hash = int(content)
        except ValueError:
            print("Файл пароля содержит некорректные данные (не MAGIC, не BLOCKED и не число).")
            sys.exit(1)

        attempts = 3
        while attempts > 0:
            attempt_pass = getpass.getpass("Введите пароль: ")
            if hash_from_text(attempt_pass) == stored_hash:
                print("Доступ разрешён — хеш совпал. Продолжаем работу.")
                return
            attempts -= 1
            print(f"Неверный пароль. Осталось попыток: {attempts}")

        write_password_file(file_path, BLOCKED_TOKEN)
        print("Превышено число попыток. Файл помечен как BLOCKED. Программа завершает работу.")
        sys.exit(1)


if __name__ == "__main__":
    main()
