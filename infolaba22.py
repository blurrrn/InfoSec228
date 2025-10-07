#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import getpass, sys

MAGIC = "MAGIC"
BLOCKED = "BLOCKED"

def xor_hash(text):
    data = text.encode("utf-8")
    h = 0
    for i in range(0, len(data), 2):
        b1 = data[i]
        b2 = data[i+1] if i+1 < len(data) else 0
        h ^= (b1 << 8) | b2
    return h

def check_complexity(p):
    if len(p) < 6: return False
    has = [
        any('a' <= c <= 'z' for c in p),
        any('A' <= c <= 'Z' for c in p),
        any(0x0400 <= ord(c) <= 0x04FF and c.islower() for c in p),
        any(0x0400 <= ord(c) <= 0x04FF and c.isupper() for c in p),
        any(c.isdigit() or not c.isalnum() for c in p)
    ]
    return sum(has) >= 5

path = input("Укажите путь к файлу пароля: ").strip()
if not path:
    print("Не указан путь."); sys.exit()
f = Path(path)

if not f.exists():
    print("Файл не найден. Создайте файл с текстом MAGIC.")
    sys.exit()

try:
    content = f.read_text(encoding="utf-8").strip()
except Exception as e:
    print("Ошибка чтения файла:", e)
    sys.exit()

if content == MAGIC:
    print("Первый запуск. Установите пароль.")
    p = getpass.getpass("Введите новый пароль: ")
    if not check_complexity(p):
        print("Пароль не соответствует требованиям.")
        sys.exit()
    f.write_text(str(xor_hash(p)), encoding="utf-8")
    print("Пароль сохранён.")
elif content == BLOCKED:
    print("Система заблокирована.")
else:
    try:
        stored = int(content)
    except:
        print("Некорректное содержимое файла.")
        sys.exit()
    for i in range(3, 0, -1):
        p = getpass.getpass(f"Введите пароль (осталось {i} попыток): ")
        if xor_hash(p) == stored:
            print("Доступ разрешён."); sys.exit()
        print("Неверный пароль.")
    f.write_text(BLOCKED, encoding="utf-8")
    print("Система заблокирована.")
