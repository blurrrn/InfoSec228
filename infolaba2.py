import sys
from pathlib import Path

magic = "hello"
block = "STOP"

def hash_from_password(password: str) -> int:
    data = password.encode("utf-8")
    h = 0
    i = 0
    n = len(data)
    while i < n:
        b1 = data[i]
        b2 = data[i + 1] if (i + 1) < n else 0
        num = (b1 << 8) | b2
        h ^= num
        i += 2
    return h

def check_password_complexity(password: str) -> bool:
    if len(password) < 6:
        return False

    has_latin_lower = False
    has_latin_upper = False
    has_cyrillic_lower = False
    has_cyrillic_upper = False
    has_digit_or_sign = False

    for ch in password:
        #латиница
        if 'a' <= ch <= 'z':
            has_latin_lower = True
        elif 'A' <= ch <= 'Z':
            has_latin_upper = True
        #кириллица
        elif '\u0430' <= ch <= '\u044f':  #а–я
            has_cyrillic_lower = True
        elif '\u0410' <= ch <= '\u042f':  #А–Я
            has_cyrillic_upper = True
        #цифры или прочие знаки
        elif ch.isdigit() or (not ch.isalnum()):
            has_digit_or_sign = True

    count = sum([has_latin_lower, has_latin_upper,
                 has_cyrillic_lower, has_cyrillic_upper, has_digit_or_sign])
    return count == 5

def ask(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def main():
    #получение пути к файлу
    if len(sys.argv) >= 2:
        pwd_path = Path(sys.argv[1])
    else:
        user_input = ask("Укажите путь к файлу: ").strip()
        if not user_input:
            print("Путь не указан. Завершение работы...")
            return
        pwd_path = Path(user_input)

    if not pwd_path.exists():
        print(f"Файл не найден по указанному пути: {pwd_path}")
        print("завершение работы...")
        return

    # читаем содержимое файла как текст
    content = pwd_path.read_text(encoding="utf-8").strip()

    if content == magic:
        print("создание пароля...")
        # new_pass = ask("Введите новый пароль: ")
        # if not check_password_complexity(new_pass):
        #     print(f"Пароль не прошёл проверку сложности. Требуется минимум 6 символов "
        #           "и разнообразие символов (латиница, кириллица, регистр, цифры/знаки)")
        #     return
        # new_hash = hash_from_password(new_pass)
        # pwd_path.write_text(str(new_hash), encoding="utf-8")
        # print("Пароль установлен и его хэш сохранён в файл.")
        #
        # return
        while True:
            new_pass = ask("Введите новый пароль: ")
            if not new_pass:
                print("Пустой пароль не допускается.")
                continue

            if check_password_complexity(new_pass):
                new_hash = hash_from_password(new_pass)
                pwd_path.write_text(str(new_hash), encoding="utf-8")
                print("Пароль установлен и хэш сохранён в файл.")
                break
            else:
                print(f"Пароль не прошёл проверку сложности. Требуется минимум 6 символов "
                      "и разнообразие символов (латиница, кириллица, регистр, цифры/знаки).")
                print("Попробуйте ещё раз.")
        return

    if content == block:
        print("Доступ заблокирован.")
        return

    #ожидается что в файле хранится хэш (число)
    try:
        stored_hash = int(content)
    except ValueError:
        print("Содержимое файла  не распознано")
        print("Завершение работы...")
        return


    attempts = 3
    while attempts > 0:
        attempt_pass = ask("Введите пароль: ")
        computed = hash_from_password(attempt_pass)
        if computed == stored_hash:
            print("Доступ разрешён")
            return
        else:
            attempts -= 1
            print(f"Неверный пароль. Осталось попыток: {attempts}")

    # вышли из цикла и тогда блокируем
    pwd_path.write_text(block, encoding="utf-8")
    print("Превышено число попыток. Программа заблокирована")


if __name__ == "__main__":
    main()
