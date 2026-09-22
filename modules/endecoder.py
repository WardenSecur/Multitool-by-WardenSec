import base64
import binascii
import urllib.parse
import html
import sys
import json
import hashlib
import os
import readline


try:
    from colorama import init, Fore
    init(autoreset=True)
except ImportError:
    Fore = None

# AES через cryptography, если установлен
try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_AES = True
except ImportError:
    HAS_AES = False


# ------------------ БЕЗ КЛЮЧА ------------------

def encode_no_key(text):
    raw = text.encode("utf-8")
    results = {}
    results["Base64"] = base64.b64encode(raw).decode()
    results["Base64 URL-safe"] = base64.urlsafe_b64encode(raw).decode()
    results["Base32"] = base64.b32encode(raw).decode()
    results["Base16 (Hex)"] = binascii.hexlify(raw).decode()
    results["URL"] = urllib.parse.quote(text)
    results["HTML"] = html.escape(text)
    results["ROT13"] = text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
    ))
    results["Binary"] = " ".join(format(b, "08b") for b in raw)
    results["Octal"] = " ".join(format(b, "03o") for b in raw)
    results["Decimal"] = " ".join(str(b) for b in raw)
    results["Unicode escape"] = text.encode("unicode_escape").decode()
    results["JSON escape"] = json.dumps(text)[1:-1]
    results["Reverse"] = text[::-1]
    return results


def decode_no_key(text):
    results = {}
    t = text.strip()

    decoders = [
        ("Base64", lambda x: base64.b64decode(x + "=" * (-len(x) % 4))),
        ("Base64 URL-safe", lambda x: base64.urlsafe_b64decode(x + "=" * (-len(x) % 4))),
        ("Base32", lambda x: base64.b32decode(x + "=" * (-len(x) % 8))),
        ("Base16 (Hex)", lambda x: binascii.unhexlify(x.replace(" ", ""))),
        ("URL", lambda x: urllib.parse.unquote(x)),
        ("HTML", lambda x: html.unescape(x)),
        ("ROT13", lambda x: x.translate(str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
        ))),
        ("Unicode escape", lambda x: x.encode().decode("unicode_escape")),
        ("JSON escape", lambda x: json.loads('"' + x + '"')),
    ]

    for name, func in decoders:
        try:
            r = func(t)
            if isinstance(r, bytes):
                r = r.decode("utf-8", errors="replace")
            results[name] = str(r)
        except Exception:
            pass

    if all(c in "01 " for c in t):
        try:
            bits = t.replace(" ", "")
            if len(bits) % 8 == 0:
                results["Binary"] = "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
        except Exception:
            pass

    if all(c in "01234567 " for c in t):
        try:
            results["Octal"] = "".join(chr(int(p, 8)) for p in t.split())
        except Exception:
            pass

    if all(c.isdigit() or c == " " for c in t):
        try:
            parts = t.split()
            if all(0 <= int(p) <= 255 for p in parts):
                results["Decimal"] = "".join(chr(int(p)) for p in parts)
        except Exception:
            pass

    results["Reverse"] = t[::-1]
    return results


# ------------------ С КЛЮЧОМ ------------------

def xor_crypt(data, key):
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(key, str):
        key = key.encode("utf-8")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def vigenere_encrypt(text, key):
    result = []
    key = key.lower()
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shift = ord(key[ki % len(key)]) - ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def vigenere_decrypt(text, key):
    result = []
    key = key.lower()
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shift = ord(key[ki % len(key)]) - ord('a')
            result.append(chr((ord(ch) - base - shift) % 26 + base))
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def caesar_encrypt(text, shift):
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)


def aes_key_from_password(password):
    # Fernet требует 32-байтный ключ в base64
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def aes_encrypt(text, password):
    if not HAS_AES:
        return None
    key = aes_key_from_password(password)
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()


def aes_decrypt(text, password):
    if not HAS_AES:
        return None
    key = aes_key_from_password(password)
    f = Fernet(key)
    try:
        return f.decrypt(text.encode()).decode()
    except InvalidToken:
        return None
    except Exception:
        return None


def encode_with_key(text):
    key = input("Введи ключ/пароль: ").strip()
    if not key:
        print("[-] Ключ пустой.")
        return

    results = {}

    # XOR — вывод в hex и base64
    x = xor_crypt(text, key)
    results["XOR (hex)"] = x.hex()
    results["XOR (base64)"] = base64.b64encode(x).decode()

    # Vigenère — только для букв
    if text.replace(" ", "").isalpha():
        results["Vigenère"] = vigenere_encrypt(text, key)
    else:
        results["Vigenère"] = "только буквы"

    # Caesar — сдвиг из ключа (сумма символов mod 26)
    shift = sum(ord(c) for c in key) % 26
    results["Caesar (shift=" + str(shift) + ")"] = caesar_encrypt(text, shift)

    # AES (Fernet)
    if HAS_AES:
        aes = aes_encrypt(text, key)
        if aes:
            results["AES (Fernet)"] = aes
    else:
        results["AES (Fernet)"] = "pip install cryptography"

    print_block("ENCODE (с ключом)", results)


def decode_with_key(text):
    print("\n[*] Автоопределение метода...")
    candidates = []

    # Проверяем, что похоже на hex
    try:
        binascii.unhexlify(text.replace(" ", ""))
        candidates.append("XOR (hex)")
    except Exception:
        pass

    # Проверяем на base64
    try:
        base64.b64decode(text + "=" * (-len(text) % 4))
        candidates.append("XOR (base64)")
    except Exception:
        pass

    # AES Fernet всегда начинается с gAAAAA
    if text.startswith("gAAAAA"):
        candidates.append("AES (Fernet)")

    # Vigenère — только буквы
    if text.replace(" ", "").isalpha():
        candidates.append("Vigenère")

    # Caesar — тоже только буквы
    if text.replace(" ", "").isalpha():
        candidates.append("Caesar")

    if not candidates:
        print("[-] Метод с ключом не определён.")
        return

    print(f"[*] Возможные методы: {', '.join(candidates)}")
    print("(Попробуй все из списка)")
    print("Выбери метод:")
    for i, c in enumerate(candidates, 1):
        print(f"  {i}. {c}")
    choice = input("Номер: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(candidates)):
        print("[-] Неверный выбор.")
        return

    method = candidates[int(choice) - 1]
    key = input("Введи ключ/пароль: ").strip()
    if not key:
        print("[-] Ключ пустой.")
        return

    result = None

    if method == "XOR (hex)":
        try:
            data = bytes.fromhex(text.replace(" ", ""))
            result = xor_crypt(data, key).decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[-] Ошибка: {e}")
            return
    elif method == "XOR (base64)":
        try:
            data = base64.b64decode(text + "=" * (-len(text) % 4))
            result = xor_crypt(data, key).decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[-] Ошибка: {e}")
            return
    elif method == "AES (Fernet)":
        result = aes_decrypt(text, key)
        if result is None:
            print("[-] Не удалось расшифровать. Неверный ключ или повреждённые данные.")
            return
    elif method == "Vigenère":
        result = vigenere_decrypt(text, key)
    elif method == "Caesar":
        shift = sum(ord(c) for c in key) % 26
        result = caesar_decrypt(text, shift)

    if result is not None:
        print(f"\n[+] Результат ({method}):")
        if Fore:
            print(Fore.GREEN + result)
        else:
            print(result)


# ------------------ ОБЩЕЕ ------------------

def print_block(title, items):
    print(f"\n=== {title} ===")
    for k, v in items.items():
        line = f"  {k:<20} {v}"
        if Fore:
            print(Fore.GREEN + line)
        else:
            print(line)


def main():
    print("=== ENCODER / DECODER v2 ===")
    print("  1. Закодировать")
    print("  2. Расшифровать (автоопределение)")
    print("  3. Оба сразу")
    choice = input("Выбор (1/2/3): ").strip()

    if choice == "1":
        text = input("Введи строку: ").strip()
        if not text:
            print("[-] Пусто.")
            return
        print_block("ENCODE (без ключа)", encode_no_key(text))
        print()
        print("[*] Теперь шифры с ключом.")
        encode_with_key(text)

    elif choice == "2":
        text = input("Введи закодированный текст: ").strip()
        if not text:
            print("[-] Пусто.")
            return
        # Сначала пробуем без ключа
        no_key = decode_no_key(text)
        if no_key:
            print_block("DECODE (без ключа)", no_key)
        # Потом с ключом
        print()
        print("[*] Проверка методов с ключом.")
        decode_with_key(text)

    elif choice == "3":
        text = input("Введи строку: ").strip()
        if not text:
            print("[-] Пусто.")
            return
        print_block("ENCODE (без ключа)", encode_no_key(text))
        print()
        encode_with_key(text)
        print()
        no_key = decode_no_key(text)
        if no_key:
            print_block("DECODE (без ключа)", no_key)
        decode_with_key(text)

    else:
        print("[-] Неверный выбор.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Прервано.")