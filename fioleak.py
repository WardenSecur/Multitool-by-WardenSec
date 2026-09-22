import sys
import time
import random
import urllib.parse
import readline

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[-] Установи: pip install requests beautifulsoup4 googlesearch-python")
    sys.exit(1)

try:
    from googlesearch import search as gsearch
except ImportError:
    gsearch = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"
}

DORKS = {
    "fio": [
        '"{q}"',
        '"{q}" site:vk.com',
        '"{q}" site:ok.ru',
        '"{q}" site:facebook.com',
        '"{q}" site:instagram.com',
        '"{q}" site:t.me',
        '"{q}" filetype:pdf',
        '"{q}" filetype:doc',
        '"{q}" filetype:xls',
        '"{q}" резюме',
        '"{q}" работа',
        '"{q}" суд',
        '"{q}" пристав',
        '"{q}" телефон',
        '"{q}" email',
        '"{q}" "@gmail.com"',
        '"{q}" "@yandex.ru"',
        '"{q}" "@mail.ru"',
    ],
    "nick": [
        '"{q}"',
        '"{q}" site:vk.com',
        '"{q}" site:t.me',
        '"{q}" site:github.com',
        '"{q}" site:reddit.com',
        '"{q}" site:youtube.com',
        '"{q}" inurl:profile',
        '"{q}" inurl:user',
        '"{q}" inurl:id',
        '"{q}" telegram',
    ],
    "email": [
        '"{q}"',
        '"{q}" filetype:pdf',
        '"{q}" filetype:doc',
        '"{q}" filetype:xls',
        '"{q}" site:pastebin.com',
        '"{q}" site:github.com',
        '"{q}" password',
        '"{q}" leak',
    ],
    "phone": [
        '"{q}"',
        '"{q}" site:vk.com',
        '"{q}" site:ok.ru',
        '"{q}" site:avito.ru',
        '"{q}" site:youla.ru',
        '"{q}" объявление',
        '"{q}" продам',
    ]
}


def detect_type(query):
    q = query.strip()
    if "@" in q:
        return "email"
    if q.startswith("+") or (q.replace(" ", "").replace("-", "").isdigit() and len(q) >= 10):
        return "phone"
    parts = q.split()
    if len(parts) >= 2 and all(p[0].isupper() for p in parts if p):
        return "fio"
    return "nick"


def search_google(query, max_results=15):
    if not gsearch:
        return []
    try:
        results = []
        for url in gsearch(query, num_results=max_results, lang="ru", sleep_interval=2):
            results.append((url, url))
        return results
    except Exception as e:
        print(f"   [!] Google ошибка: {e}")
        return []


def search_ddg_lite(query, max_results=15):
    url = "https://lite.duckduckgo.com/lite/"
    try:
        r = requests.post(url, data={"q": query}, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
    except Exception:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") and "duckduckgo" not in href:
            title = a.get_text(strip=True) or href
            results.append((title, href))
        if len(results) >= max_results:
            break
    return results


def search_yandex_html(query, max_results=15):
    url = "https://yandex.ru/search/"
    params = {"text": query}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
    except Exception:
        return []
    if "captcha" in r.text.lower() or r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.select("a.organic__url, a.Link_theme_normal"):
        href = a.get("href", "")
        if href.startswith("http"):
            results.append((a.get_text(strip=True) or href, href))
        if len(results) >= max_results:
            break
    return results


def multi_search(query):
    engines = [
        ("Google", search_google),
        ("DDG Lite", search_ddg_lite),
        ("Yandex", search_yandex_html),
    ]
    for name, fn in engines:
        print(f"   [*] Пробую {name}...")
        res = fn(query)
        if res:
            print(f"   [+] {name} дал {len(res)} результатов")
            return res
        else:
            print(f"   [-] {name} пусто")
    return []


def run_dorks(query, category):
    dorks = DORKS.get(category, DORKS["nick"])
    all_results = {}
    for i, d in enumerate(dorks, 1):
        q = d.format(q=query)
        print(f"\n[{i}/{len(dorks)}] Дорк: {q}")
        results = multi_search(q)
        if results:
            for title, link in results:
                if link not in all_results:
                    all_results[link] = title
                    print(f"   -> {title[:70]}")
                    print(f"      {link}")
        else:
            print("   нет результатов")
        time.sleep(random.uniform(2.0, 4.0))
    print(f"\n[+] Уникальных ссылок: {len(all_results)}")


def main():
    print("=== PEOPLE SEARCH ===")
    query = input("Введите ФИО / ник / email / телефон: ").strip()
    if not query:
        print("[-] Пусто.")
        return
    category = detect_type(query)
    print(f"[*] Определён тип: {category}")
    confirm = input("Верно? (y/n, Enter = y): ").strip().lower()
    if confirm == "n":
        category = input("Укажи тип вручную (fio/nick/email/phone): ").strip().lower()
        if category not in DORKS:
            print("[-] Неверный тип.")
            return
    run_dorks(query, category)


if __name__ == "__main__":
    main()