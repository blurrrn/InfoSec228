#!/usr/bin/env python3
# hide.py
# Простой студенческий стиль, cp1251 (Windows-1251) кодировка для текста сообщения

import os
import sys
import argparse
from pathlib import Path

def text_to_bits(msg_bytes):
    for b in msg_bytes:
        for i in range(7, -1, -1):
            yield (b >> i) & 1

def int_to_4bytes_be(n):
    return n.to_bytes(4, byteorder='big', signed=False)

def embed_bits_into_lines(lines, bits):
    # lines: list of strings (each may end with \n or not). Возвращает новые строки.
    out_lines = []
    bit_iter = iter(bits)
    for line in lines:
        # preserve original line ending (\n or ''):
        if line.endswith('\r\n'):
            body = line[:-2]
            ending = '\r\n'
        elif line.endswith('\n'):
            body = line[:-1]
            ending = '\n'
        else:
            body = line
            ending = ''
        try:
            bit = next(bit_iter)
        except StopIteration:
            # больше битов нет — оставляем строку как есть
            out_lines.append(body + ending)
            continue
        # если бит == 1 -> дописываем один пробел в конец строки (перед окончанием)
        if bit == 1:
            body = body + ' '
        out_lines.append(body + ending)
    # если bits не закончились — недостаточно строк
    try:
        next(bit_iter)
        raise ValueError("Недостаточно строк в контейнере для размещения всех битов.")
    except StopIteration:
        pass
    return out_lines

def main():
    parser = argparse.ArgumentParser(description="Спрятать текст в текстовом контейнере (метод: пробел в конце строки = 1).")
    parser.add_argument("-c", "--container", help="путь к файлу-контейнеру (текстовый)", required=False)
    parser.add_argument("-m", "--message", help="путь к файлу с сообщением (текст) или сам текст, если --inline", required=False)
    parser.add_argument("-o", "--out", help="путь для выходного контейнера (не перезаписывать исходный)", required=False)
    parser.add_argument("--inline", action="store_true", help="если указано, --message интерпретируется как сам текст (не файл)")
    args = parser.parse_args()

    # интерактивный ввод, если не переданы аргументы
    if not args.container:
        args.container = input("Путь к контейнеру (текстовый файл): ").strip()
    if not args.message:
        args.message = input("Путь к файлу с сообщением или сам текст (используйте --inline чтобы передать текст): ").strip()
    if not args.out:
        default_out = None

    cont_path = Path(args.container)
    if not cont_path.exists():
        print("Ошибка: контейнер не найден по пути:", cont_path)
        sys.exit(1)

    if args.inline:
        message_text = args.message
    else:
        msg_path = Path(args.message)
        if not msg_path.exists():
            print("Ошибка: файл с сообщением не найден:", msg_path)
            sys.exit(1)
        # читаем файл сообщения как текст (попытаемся cp1251)
        raw = msg_path.read_bytes()
        # попробуем декодировать в cp1251; если не получится — используем utf-8 как fallback
        try:
            message_text = raw.decode('cp1251')
        except Exception:
            message_text = raw.decode('utf-8', errors='replace')

    # кодируем сообщение в байты cp1251 (8-bit requirement). Если символы не мапятся — используем replace.
    try:
        message_bytes = message_text.encode('cp1251')
        encoding_used = 'cp1251'
    except Exception:
        message_bytes = message_text.encode('cp1251', errors='replace')
        encoding_used = 'cp1251 (with replacement)'

    msg_len = len(message_bytes)
    if msg_len == 0:
        print("Пустое сообщение — ничего не делаю.")
        sys.exit(1)

    # читаем контейнер (сохраняем окончания строк)
    container_text = cont_path.read_text(encoding='utf-8', errors='surrogateescape')
    # splitlines(True) сохраняет окончания строк
    lines = container_text.splitlines(True)

    # составляем поток битов: сначала 4 байта длины (big-endian), затем биты сообщения
    header = int_to_4bytes_be(msg_len)
    all_bytes = header + message_bytes
    bits = list(text_to_bits(all_bytes))
    needed = len(bits)
    available = len(lines)
    if available < needed:
        print(f"Ошибка: в контейнере строк {available}, требуется {needed} для размещения сообщения ({msg_len} байт).")
        sys.exit(1)

    # выполняем встраивание
    try:
        new_lines = embed_bits_into_lines(lines, bits)
    except ValueError as e:
        print("Ошибка при встраивании:", e)
        sys.exit(1)

    # выбираем путь вывода
    if args.out:
        out_path = Path(args.out)
    else:
        # если исходный контейнер называется name.ext -> name_steg.ext
        p = cont_path
        out_name = p.stem + "_steg" + p.suffix
        out_path = p.with_name(out_name)

    # запрещаем перезаписывать тот же файл контейнера (правило задания)
    if out_path.resolve() == cont_path.resolve():
        # если совпадают, изменим имя
        out_path = cont_path.with_name(cont_path.stem + "_steg" + cont_path.suffix)

    # сохраняем (используем utf-8 для контейнера, сохраняя тот же стиль ошибок)
    out_path.write_text(''.join(new_lines), encoding='utf-8', errors='surrogateescape')

    print("Сообщение скрыто успешно.")
    print("Размер сообщения (байт):", msg_len)
    print("Кодировка сообщения при встраивании:", encoding_used)
    print("Выходной файл контейнера:", out_path)

if __name__ == "__main__":
    main()
