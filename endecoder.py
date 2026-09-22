import base64
import binascii
import urllib.parse
import html
import sys
import json
import readline

try:
    from colorama import init, Fore
    init(autoreset=True)
except ImportError:
    Fore = None


def try_decode(name, func, data):
    try:
        result = func(data)
        if isinstance(result, bytes):
            result = result.decode("utf-8", errors="replace")
        return (name, str(result))
    except Exception:
        return None


def encode_all(text):
    results = {}
    raw = text.encode("utf-8")

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


def decode_all(text):
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
        r = try_decode(name, func, t)
        if r:
            results[r[0]] = r[1]

    # бинарный ввод
    if all(c in "01 " for c in t):
        try:
            bits = t.replace(" ", "")
            if len(bits) % 8 == 0:
                decoded = "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
                results["Binary"] = decoded
        except Exception:
            pass

    # восьмеричный
    if all(c in "01234567 " for c in t):
        try:
            parts = t.split()
            decoded = "".join(chr(int(p, 8)) for p in parts)
            results["Octal"] = decoded
        except Exception:
            pass

    # десятичный
    if all(c.isdigit() or c == " " for c in t):
        try:
            parts = t.split()
            if all(0 <= int(p) <= 255 for p in parts):
                decoded = "".join(chr(int(p)) for p in parts)
                results["Decimal"] = decoded
        except Exception:
            pass

    # реверс
    results["Reverse"] = t[::-1]
    return results


def print_block(title, items):
    print(f"\n=== {title} ===")
    for k, v in items.items():
        line = f"  {k:<20} {v}"
        if Fore:
            print(Fore.GREEN + line)
        else:
            print(line)


def main():
    print("=== ENCODER / DECODER ===")
    print("Шифрует/дешифрует текст популярными методами")
    print("  1. Закодировать")
    print("  2. Декодировать (автоопределение)")
    print("  3. Оба сразу")
    choice = input("Выбор (1/2/3): ").strip()

    text = input("Введи строку: ").strip()
    if not text:
        print("[-] Пусто.")
        return

    if choice == "1":
        print_block("ENCODE", encode_all(text))
    elif choice == "2":
        print_block("DECODE", decode_all(text))
    elif choice == "3":
        print_block("ENCODE", encode_all(text))
        print_block("DECODE", decode_all(text))
    else:
        print("[-] Неверный выбор.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Прервано.")