import subprocess
import sys
import re
import platform
import concurrent.futures
import ipaddress
import socket
import readline
try:
    from colorama import init, Fore
    init(autoreset=True)
except ImportError:
    Fore = None


SYSTEM = platform.system().lower()
IS_TERMUX = "com.termux" in str(sys.prefix) if hasattr(sys, "prefix") else False


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def get_interface_network():
    ip = get_local_ip()
    if not ip:
        return None
    # предполагаем /24
    net = ipaddress.ip_network(ip + "/24", strict=False)
    return net


def ping_host(ip):
    param = "-n" if SYSTEM == "windows" else "-c"
    timeout = "-w" if SYSTEM == "windows" else "-W"
    try:
        subprocess.run(
            ["ping", param, "1", timeout, "1", str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return str(ip)
    except Exception:
        return None


def ping_sweep(net):
    print(f"[*] Пингую {net.num_addresses - 2} хостов...")
    alive = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        futures = [ex.submit(ping_host, ip) for ip in net.hosts()]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                alive.append(res)
    print(f"[+] Живых хостов: {len(alive)}")
    return alive


def get_arp_table():
    table = {}
    try:
        if SYSTEM == "windows":
            out = subprocess.check_output(["arp", "-a"], encoding="cp866", errors="ignore")
            for line in out.splitlines():
                m = re.match(r"\s*(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})", line)
                if m:
                    table[m.group(1)] = m.group(2).replace("-", ":").lower()
        else:
            # Linux / Termux
            try:
                out = subprocess.check_output(["ip", "neigh"], encoding="utf-8", errors="ignore")
            except Exception:
                out = subprocess.check_output(["arp", "-a"], encoding="utf-8", errors="ignore")
            for line in out.splitlines():
                m = re.search(r"(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F:]{17})", line)
                if m:
                    table[m.group(1)] = m.group(2).lower()
    except Exception as e:
        print(f"[-] Ошибка чтения ARP: {e}")
    return table


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""


def get_mac_vendor(mac):
    # первые 3 байта = OUI
    oui = mac.upper().replace(":", "")[:6]
    known = {
        "000C29": "VMware", "005056": "VMware", "080027": "VirtualBox",
        "00155D": "Microsoft Hyper-V", "525400": "QEMU/KVM",
        "B827EB": "Raspberry Pi", "DCA632": "Raspberry Pi",
        "F4F26D": "TP-Link", "A42BB0": "TP-Link", "C46E1F": "TP-Link",
        "001A2B": "Apple", "001B63": "Apple", "002500": "Apple",
        "3C5A37": "Samsung", "8C7712": "Samsung", "E8508B": "Samsung",
        "001C42": "Parallels", "001C14": "VMware",
        "FCECDA": "Ubiquiti", "0418D6": "Ubiquiti", "788A20": "Ubiquiti",
    }
    return known.get(oui, "unknown")


def main():
    print("=== ARP SCANNER ===")
    print("озволяет просмотреть какие устройства подключены и идентификаторы этих устройств")
    net = get_interface_network()
    if not net:
        print("[-] Не удалось определить сеть.")
        return
    print(f"[*] Локальная сеть: {net}")

    auto = input("Сделать ping-sweep для заполнения ARP? (y/n, Enter=y): ").strip().lower()
    if auto != "n":
        ping_sweep(net)

    print("\n[*] Читаю ARP-таблицу...")
    table = get_arp_table()
    if not table:
        print("[-] ARP пуст. Возможно, нужен ping-sweep или Root.")
        return

    print(f"\n{'IP':<18}{'MAC':<20}{'VENDOR':<20}HOSTNAME")
    print("-" * 80)
    for ip, mac in sorted(table.items(), key=lambda x: ipaddress.ip_address(x[0])):
        vendor = get_mac_vendor(mac)
        host = get_hostname(ip)
        line = f"{ip:<18}{mac:<20}{vendor:<20}{host}"
        if Fore:
            print(Fore.GREEN + line)
        else:
            print(line)

    print(f"\n[+] Всего устройств: {len(table)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Прервано.")