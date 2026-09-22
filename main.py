import subprocess
from asyncio import sleep
from colorama import init, Fore, Back, Style
init(autoreset=True)
import random
import time
import sys
import readline



def hacker_print(text, scramble_duration=0.1, tick=0.005):
    chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`0123456789abcdefghijklmnopqrstuvwxyz"

    for i, char in enumerate(text):
        end_time = time.time() + scramble_duration

        # 1 секунда "шума" на текущей позиции
        while time.time() < end_time:
            noise = random.choice(chars)
            sys.stdout.write("\r" + text[:i] + noise)
            sys.stdout.flush()
            time.sleep(tick)

        # Фиксируем настоящий символ
        sys.stdout.write("\r" + text[:i+1])
        sys.stdout.flush()

    print()


while True:
    hacker_print("MultiTool by WardenSec")
    time.sleep(0.7)
    print(Fore.MAGENTA + "Выбери функцию:")
    time.sleep(0.7)
    print(Fore.GREEN + "1. Поиск по нику                    2. Security Check")
    print(Fore.GREEN + "3. Dork Gen                         4. Проверка номера | Phone Lookup")
    print(Fore.GREEN + "5. People Search (пока не работает) 6. Port Scan")
    print(Fore.GREEN + "7. ARP Scanner                      8. Hash Id")
    print(Fore.GREEN + "9. Encoder/Decoder")
    print(Fore.RED + "Выйти: /exit")
    chose = input()
    if chose == "1":
        subprocess.run(["python", "maigrot.py"])
    if chose == "2":
        subprocess.run(["python", "basesec.py"])
    if chose == "3":
        subprocess.run(["python", "dorks.py"])
    if chose == "4":
        subprocess.run(["python", "phonelookup.py"])
    if chose == "5":
        print("Ну сказано же что не работает.")
    if chose == "6":
        subprocess.run(["python", "portscan.py"])
    if chose == "7":
        subprocess.run(["python", "arpscan.py"])
    if chose == "8":
        subprocess.run(["python", "hashid.py"])
    if chose == "9":
        subprocess.run(["python", "endecoder.py"])
    if chose == "/exit":
        break


sys.exit()