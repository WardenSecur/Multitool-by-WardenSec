import socket
import sys
import concurrent.futures
from datetime import datetime
import readline

try:
    from colorama import init, Fore
    init(autoreset=True)
except ImportError:
    Fore = None


COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 1723: "PPTP", 2049: "NFS",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
    27017: "MongoDB", 5000: "Flask/UPnP", 8000: "HTTP-Alt"
}


def grab_banner(ip, port, timeout=2):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        s.settimeout(timeout)
        try:
            raw = s.recv(1024)
        except Exception:
            raw = b""
        s.close()

        # отрезаем всё после первого переноса строки
        raw = raw.split(b"\n")[0].split(b"\r")[0]

        # выкидываем нечитаемые байты (кроме ASCII 32-126)
        cleaned = bytes(b for b in raw if 32 <= b <= 126)

        return cleaned.decode("ascii", errors="ignore").strip()
    except Exception:
        return ""


def scan_port(ip, port, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        if result == 0:
            banner = grab_banner(ip, port)
            service = COMMON_PORTS.get(port, "unknown")
            return (port, service, banner)
    except Exception:
        pass
    return None


def parse_ports(spec):
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            ports.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            ports.add(int(part))
    return sorted(ports)


def resolve(target):
    try:
        return socket.gethostbyname(target)
    except Exception:
        return None


def main():
    print("=== PORT SCANNER ===")
    print("Скан портов с отображением статуса")
    target = input("Введи IP или домен: ").strip()
    if not target:
        print("[-] Пусто.")
        return
    ip = resolve(target)
    if not ip:
        print("[-] Не удалось resolve.")
        return
    print(f"[*] IP: {ip}")

    port_spec = input("Порты (Enter = топ-25, пример: 1-1000, 80,443,8080): ").strip()
    if not port_spec:
        ports = sorted(COMMON_PORTS.keys())
    else:
        try:
            ports = parse_ports(port_spec)
        except Exception:
            print("[-] Неверный формат.")
            return

    print(f"[*] Сканирую {len(ports)} портов...")
    start = datetime.now()
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as ex:
        futures = {ex.submit(scan_port, ip, p): p for p in ports}
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                port, service, banner = res
                open_ports.append(port)
                line = f"[+] {port:<6} {service:<15}"
                if banner:
                    line += f" | {banner[:60]}"
                if Fore:
                    print(Fore.GREEN + line)
                else:
                    print(line)

    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n[*] Готово за {elapsed:.2f}s. Открыто: {len(open_ports)}")
    if open_ports:
        print(f"[*] Список: {', '.join(map(str, open_ports))}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Прервано.")