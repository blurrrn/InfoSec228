def decode_message(container_path, output_path):
    with open(container_path, 'r', encoding='windows-1251') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    bits = []
    for line in lines:
        if line.endswith(' '):
            bits.append('1')
        else:
            bits.append('0')

    message_bytes = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i + 8]
        if len(byte_bits) < 8:
            break
        byte = int(''.join(byte_bits), 2)
        if byte == 0:
            break
        message_bytes.append(byte)

    with open(output_path, 'wb') as f:
        f.write(bytes(message_bytes))


if __name__ == '__main__':
    container = input("Путь к контейнеру: ")
    output = input("Путь для извлеченного сообщения: ")
    decode_message(container, output)
    print("Сообщение извлечено!")

