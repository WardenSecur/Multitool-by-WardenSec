import re
import sys
import readline
try:
    from colorama import init, Fore
    init(autoreset=True)
except ImportError:
    Fore = None


HASH_PATTERNS = [
    ("MD5",           r"^[a-f0-9]{32}$"),
    ("MD4",           r"^[a-f0-9]{32}$"),
    ("NTLM",          r"^[a-f0-9]{32}$"),
    ("LM",            r"^[a-f0-9]{32}$"),
    ("SHA1",          r"^[a-f0-9]{40}$"),
    ("MySQL 4.1+",    r"^\*[A-F0-9]{40}$"),
    ("SHA224",        r"^[a-f0-9]{56}$"),
    ("SHA256",        r"^[a-f0-9]{64}$"),
    ("SHA384",        r"^[a-f0-9]{96}$"),
    ("SHA512",        r"^[a-f0-9]{128}$"),
    ("SHA3-224",      r"^[a-f0-9]{56}$"),
    ("SHA3-256",      r"^[a-f0-9]{64}$"),
    ("SHA3-512",      r"^[a-f0-9]{128}$"),
    ("RIPEMD-160",    r"^[a-f0-9]{40}$"),
    ("Whirlpool",     r"^[a-f0-9]{128}$"),
    ("bcrypt",        r"^\$2[aby]?\$\d{2}\$[./A-Za-z0-9]{53}$"),
    ("bcrypt (sha256)", r"^\$5\$.{0,16}\$[./A-Za-z0-9]{43}$"),
    ("bcrypt (sha512)", r"^\$6\$.{0,16}\$[./A-Za-z0-9]{86}$"),
    ("MD5 crypt",     r"^\$1\$[./A-Za-z0-9]{0,8}\$[./A-Za-z0-9]{22}$"),
    ("SHA256 crypt",  r"^\$5\$[./A-Za-z0-9]{0,16}\$[./A-Za-z0-9]{43}$"),
    ("SHA512 crypt",  r"^\$6\$[./A-Za-z0-9]{0,16}\$[./A-Za-z0-9]{86}$"),
    ("Argon2",        r"^\$argon2(id|i|d)\$v=\d+\$m=\d+,t=\d+,p=\d+\$[A-Za-z0-9+/]+\$[A-Za-z0-9+/]+$"),
    ("scrypt",        r"^\$scrypt\$"),
    ("PBKDF2",        r"^\$pbkdf2-sha(1|256|512)\$"),
    ("Cisco Type 7",  r"^[0-9]{4,}$"),
    ("JWT",           r"^eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$"),
    ("Base64",        r"^[A-Za-z0-9+/]{16,}={0,2}$"),
    ("Hex",           r"^[a-f0-9]+$"),
    ("MySQL old",     r"^[a-f0-9]{16}$"),
    ("DES crypt",     r"^[./A-Za-z0-9]{13}$"),
    ("Oracle 10g",    r"^[A-F0-9]{16}$"),
    ("MSSQL 2000",    r"^0x[0-9A-F]{80,}$"),
    ("MSSQL 2005",    r"^0x0100[0-9A-F]{84,}$"),
    ("MD5 (MySQL)",   r"^[a-f0-9]{32}$"),
    ("NTLM (base64)", r"^[A-Za-z0-9+/]{32,}={0,2}$"),
    ("Snefru-128",    r"^[a-f0-9]{32}$"),
    ("Snefru-256",    r"^[a-f0-9]{64}$"),
    ("GOST",          r"^[a-f0-9]{64}$"),
    ("Haval-128",     r"^[a-f0-9]{32}$"),
    ("Haval-256",     r"^[a-f0-9]{64}$"),
    ("Tiger-128",     r"^[a-f0-9]{32}$"),
    ("Tiger-192",     r"^[a-f0-9]{48}$"),
]


def detect(hash_str):
    matches = []
    h = hash_str.strip()
    for name, pattern in HASH_PATTERNS:
        if re.match(pattern, h):
            matches.append(name)
    return matches


def entropy(h):
    # грубая оценка: уникальные символы / длина
    if not h:
        return 0
    return len(set(h)) / len(h)


def main():
    print("=== HASH ID ===")
    print("Определение типа хеша")
    h = input("Введи хеш: ").strip()
    if not h:
        print("[-] Пусто.")
        return

    matches = detect(h)
    if not matches:
        print("[-] Тип не определён.")
    else:
        print(f"\n[+] Длина: {len(h)}")
        print(f"[+] Уникальных символов: {len(set(h))}")
        print(f"[+] Возможные типы:")
        for m in matches:
            line = f"   - {m}"
            if Fore:
                print(Fore.GREEN + line)
            else:
                print(line)

    print(f"\n[*] Энтропия (грубо): {entropy(h):.2f}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Прервано.")