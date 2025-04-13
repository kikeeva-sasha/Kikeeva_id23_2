import heapq
import base64
from collections import defaultdict


class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1

    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(node, prefix='', code_map=None):
    if code_map is None:
        code_map = {}
    if node.char is not None:
        code_map[node.char] = prefix
    else:
        build_codes(node.left, prefix + '0', code_map)
        build_codes(node.right, prefix + '1', code_map)
    return code_map


def encode_text(text, code_map):
    return ''.join(code_map[c] for c in text)


def decode_text(bits, code_map):
    reversed_map = {v: k for k, v in code_map.items()}
    buffer = ''
    result = ''
    for bit in bits:
        buffer += bit
        if buffer in reversed_map:
            result += reversed_map[buffer]
            buffer = ''
    return result


def bits_to_bytes(bits):
    padding = (8 - len(bits) % 8) % 8
    bits += '0' * padding
    byte_data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        byte_data.append(int(byte, 2))
    return bytes(byte_data), padding


def bytes_to_bits(byte_data, padding):
    bits = ''.join(f'{byte:08b}' for byte in byte_data)
    return bits[:-padding] if padding else bits


def xor_encrypt(data, key):
    key_bytes = key.encode()
    return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])


def main():
    while True:
        action = input("Что вы хотите сделать? (1 - зашифровать, 2 - расшифровать, 3 - выйти): ")

        if action == "1":
            text = input("Введите текст для шифрования: ")
            key = input("Введите ключ (XOR): ")

            tree = build_huffman_tree(text)
            codes = build_codes(tree)
            encoded_bits = encode_text(text, codes)
            byte_data, padding = bits_to_bytes(encoded_bits)
            encrypted = xor_encrypt(byte_data, key)
            encoded_base64 = base64.b64encode(encrypted).decode()

            # Добавим padding к base64 через :
            encoded_with_padding = f"{encoded_base64}:{padding}"

            print("\nЗАШИФРОВАННЫЕ ДАННЫЕ:")
            print(f"Base64 + Padding: {encoded_with_padding}")
            print(f"Коды Хаффмана: {codes}")

        elif action == "2":
            encoded_input = input("Введите зашифрованный текст (Base64:Padding): ")
            key = input("Введите ключ (XOR): ")
            huffman_codes_str = input("Введите коды Хаффмана (например, {'H': '00', 'e': '01', ...}): ")

            # Разделяем base64 и padding
            try:
                encoded_base64, padding_str = encoded_input.strip().split(":")
                padding = int(padding_str)
            except ValueError:
                print("Ошибка: неверный формат. Используйте Base64:Padding")
                continue

            huffman_codes = eval(huffman_codes_str)

            encrypted_bytes = base64.b64decode(encoded_base64)
            decrypted_bytes = xor_encrypt(encrypted_bytes, key)
            bits = bytes_to_bits(decrypted_bytes, padding)
            decoded_text = decode_text(bits, huffman_codes)

            print("\n✅ Расшифрованный текст:", decoded_text)

        elif action == "3":
            print("Завершаю программу...")
            break

        else:
            print("Некорректный ввод. Пожалуйста, выберите 1, 2 или 3.")


if __name__ == "__main__":
    main()

