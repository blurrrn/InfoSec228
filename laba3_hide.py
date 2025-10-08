def encode_message(container_path, message_path, output_path):
    with open(message_path, 'rb') as f:
        message = f.read()

    bits = []
    for byte in message:
        bits.extend(f'{byte:08b}')

    with open(container_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(bits) > len(lines):
        raise ValueError("Контейнер слишком мал для сообщения")

    result = []
    for i, line in enumerate(lines):
        line = line.rstrip('\n')
        if i < len(bits) and bits[i] == '1':
            line += ' '
        result.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))


if __name__ == '__main__':
    container = input("Путь к контейнеру: ")
    message = input("Путь к сообщению: ")
    output = input("Путь для результата: ")
    encode_message(container, message, output)
    print("Сообщение скрыто!")

