#!/usr/bin/env python3
# extract.py
# Извлекает последовательность битов по наличию пробела в конце строк и восстанавливает текст (cp1251).

import sys
import argparse
from pathlib import Path

def bits_from_lines(lines):
    for line in lines:
        # убрать окончания строк как и в embed
        if line.endswith('\r\n'):
            body = line[:-2]
        elif line.endswith('\n'):
            body = line[:-1]
        else:
            body = line
        # последний символ перед концом строки: если это пробел -> 1, иначе 0
        if len(body) > 0 and body[-1] == ' ':
            yield 1
        else:
            yield 0

def bits_to_bytes(bits):
    b = bytearray()
    current = 0
    cnt = 0
    for bit in bits:
        current = (current << 1) | bit
        cnt += 1
        if cnt == 8:
            b.append(current)
            current = 0
            cnt = 0
    return bytes(b)

def main():
    parser = argparse.ArgumentParser(description="Извлечь скрытый текст из текстового контейнера (метод: пробел в конце строки = 1).")
    parser.add_argument("-c", "--container", help="путь к файлу-контейнеру (текстовый)", required=False)
    parser.add_argument("-o", "--out", help="путь для сохранения извлечённого текста (опционально)", required=False)
    args = parser.parse_args()

    if not args.container:
        args.container = input("Путь к контейнеру для извлечения: ").strip()

    cont_path = Path(args.container)
    if not cont_path.exists():
        print("Ошибка: контейнер не найден:", cont_path)
        sys.exit(1)

    container_text = cont_path.read_text(encoding='utf-8', errors='surrogateescape')
    lines = container_text.splitlines(True)

    bit_gen = bits_from_lines(lines)

    # Сначала читаем первые 32 бита = 4 байта длины (big-endian)
    header_bits = []
    try:
        for _ in range(32):
            header_bits.append(next(bit_gen))
    except StopIteration:
        print("Ошибка: контейнер слишком маленький — нет даже 32 бит для длины сообщения.")
        sys.exit(1)

    # соберём 4 байта
    header_bytes = bytearray()
    cur = 0
    cnt = 0
    for bit in header_bits:
        cur = (cur << 1) | bit
        cnt += 1
        if cnt == 8:
            header_bytes.append(cur)
            cur = 0
            cnt = 0
    msg_len = int.from_bytes(bytes(header_bytes), byteorder='big', signed=False)

    if msg_len == 0:
        print("Извлечено сообщение нулевой длины.")
        sys.exit(0)

    # теперь читаем msg_len * 8 бит
    needed_bits = msg_len * 8
    msg_bits = []
    try:
        for _ in range(needed_bits):
            msg_bits.append(next(bit_gen))
    except StopIteration:
        print("Ошибка: в контейнере не хватило бит для полного сообщения (ожидалось", needed_bits, "бит).")
        sys.exit(1)

    # преобразуем в байты
    msg_bytes = bits_to_bytes(msg_bits)

    # пытаемся декодировать как cp1251
    try:
        msg_text = msg_bytes.decode('cp1251')
        encoding_used = 'cp1251'
    except Exception:
        msg_text = msg_bytes.decode('utf-8', errors='replace')
        encoding_used = 'utf-8 (fallback)'

    print("Извлечено сообщение (кодировка при декодировании):", encoding_used)
    print("Длина (байт):", msg_len)
    print("---- НАЧАЛО СООБЩЕНИЯ ----")
    print(msg_text)
    print("---- КОНЕЦ СООБЩЕНИЯ ----")

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(msg_text, encoding='utf-8', errors='surrogateescape')
        print("Сохранено в файл:", out_path)

if __name__ == "__main__":
    main()
