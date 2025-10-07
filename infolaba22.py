#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import getpass, sys, os

MAGIC = "MAGIC"
BLOCKED = "BLOCKED"

def xor_hash(s):
    b = s.encode("utf-8")
    h = 0
    for i in range(0, len(b), 2):
        h ^= (b[i] << 8) | (b[i+1] if i+1 < len(b) else 0)
    return h

def strong(p):
    if len(p) < 6: return False
    has = [
        any('a' <= c <= 'z' for c in p),
        any('A' <= c <= 'Z' for c in p),
        any(0x0400 <= ord(c) <= 0x04FF and c.islower() for c in p),
        any(0x0400 <= ord(c) <= 0x04FF and c.isupper() for c in p),
        any(c.isdigit() or not c.isalnum() for c in p)
    ]
    return sum(has) >= 5

os.system('cls' if os.name == 'nt' else 'clear')
print("="*40)
print("   ПРОСТАЯ ПАРОЛЬНАЯ СИСТЕМА")
print("="*40)

path = input("Введите путь к файлу пароля: ").strip()
if not path:
    print("❌ Не указан путь."); sys.exit()
f = Path(path)

if not f.exists():
    print("\n⚠️  Файл не найден.")
    print("Создайте файл с текстом MAGIC и запустите снова.")
    sys.exit()

try:
    content = f.read_text(encoding="utf-8").strip()
except:
    print("Ошибка чтения файла."); sys.exit()

if content == MAGIC:
    print("\n🔑 Первый запуск системы.")
    p = getpass.getpass("Введите новый пароль: ")
    if not strong(p):
        print("❌ Пароль слишком простой! Используйте разные символы.")
        sys.exit()
    f.write_text(str(xor_hash(p)), encoding="utf-8")
    print("✅ Пароль сохранён! Перезапустите программу.")
elif content == BLOCKED:
    print("\n🚫 Система заблокирована. Обратитесь к администратору.")
else:
    try:
        saved = int(content)
    except:
        print("❌ Файл повреждён."); sys.exit()
    for i in range(3, 0, -1):
        p = getpass.getpass(f"Введите пароль ({i} попыток): ")
        if xor_hash(p) == saved:
            print("\n✅ Доступ разрешён! Добро пожаловать.")
            sys.exit()
        print("❌ Неверный пароль.\n")
    f.write_text(BLOCKED, encoding="utf-8")
    print("🚫 Три ошибки. Система заблоки
