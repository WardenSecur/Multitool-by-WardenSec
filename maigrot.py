import requests
import sys
import re
import readline

# Структура: (Название, Шаблон URL, Список фраз-признаков "не найден", Список фраз-признаков "найден")
SITES = [
    (
        "GitHub",
        "https://github.com/{username}",
        ["Not Found", "Page not found"],
        [],
    ),
    (
        "Twitter/X",
        "https://x.com/{username}",
        ["This account doesn’t exist", "Hmm...this page doesn’t exist", "User not found"],
        [],
    ),
    (
        "Instagram",
        "https://www.instagram.com/{username}/",
        ["Sorry, this page isn't available", "Page Not Found"],
        ["og:title"],
    ),
    (
        "Reddit",
        "https://www.reddit.com/user/{username}",
        ["page not found", "Sorry, nobody on Reddit goes by that name"],
        [],
    ),
    (
        "Telegram",
        "https://t.me/{username}",
        ["tgme_page_icon", "If you have Telegram, you can contact"],
        ["tgme_page_title"],
    ),
    (
        "TikTok",
        "https://www.tiktok.com/@{username}",
        ["Couldn't find this account", "Page not available"],
        [],
    ),
    (
        "YouTube",
        "https://www.youtube.com/@{username}",
        ["This page isn't available", "404 Not Found", "This channel does not exist"],
        [],
    ),
    (
        "Pinterest",
        "https://www.pinterest.com/{username}/",
        ["User not found", "Page not found"],
        [],
    ),
    (
        "Twitch",
        "https://www.twitch.tv/{username}",
        ["Sorry. Unless you've got a time machine, that content is unavailable"],
        [],
    ),
    (
        "Steam",
        "https://steamcommunity.com/id/{username}",
        ["The specified profile could not be found"],
        ["actual_persona_name"],
    ),
    (
        "VK",
        "https://vk.com/{username}",
        ["Page not found", "Страница не найдена"],
        [],
    ),
    (
        "Facebook",
        "https://www.facebook.com/{username}",
        ["content isn't available", "This content isn't available right now"],
        [],
    ),
    (
        "Medium",
        "https://medium.com/@{username}",
        ["Out of nothing, something", "404"],
        [],
    ),
    (
        "GitLab",
        "https://gitlab.com/{username}",
        ["Page Not Found", "404"],
        [],
    ),
    (
        "SoundCloud",
        "https://soundcloud.com/{username}",
        ["We can't find that user", "404 - Not Found"],
        [],
    ),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
}


def fetch_page(url):
    """Скачивает страницу и возвращает (html, status_code) или (None, None) при ошибке."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return response.text, response.status_code
    except requests.exceptions.RequestException:
        return None, None


def check_username(username):
    print(f"\n[+] Поиск профиля для: {username}\n")
    print("-" * 50)

    results = {"found": [], "not_found": [], "error": []}

    for name, url_template, not_found_markers, found_markers in SITES:
        url = url_template.format(username=username)
        html, status = fetch_page(url)

        if html is None:
            print(f"[!] {name}: ошибка подключения")
            results["error"].append(name)
            continue

        # Если 404 — точно нет профиля
        if status == 404:
            print(f"[-] {name}: не найден (HTTP 404)")
            results["not_found"].append(name)
            continue

        html_lower = html.lower()

        # Проверяем маркеры "не найден" (ищем без учета регистра)
        is_not_found = any(marker.lower() in html_lower for marker in not_found_markers)

        # Проверяем положительные маркеры
        is_found = any(marker.lower() in html_lower for marker in found_markers)

        if is_not_found and not is_found:
            print(f"[-] {name}: не найден (по содержимому)")
            results["not_found"].append(name)
        elif status == 200:
            print(f"[+] {name}: НАЙДЕН -> {url}")
            results["found"].append((name, url))
        else:
            print(f"[?] {name}: неопределенно (HTTP {status})")
            results["error"].append(name)

    # Итоговая сводка
    print("\n" + "=" * 50)
    print("ИТОГИ:")
    print(f"  Найдено:       {len(results['found'])}")
    print(f"  Не найдено:    {len(results['not_found'])}")
    print(f"  Не определено: {len(results['error'])}")

    if results["found"]:
        print("\nНайденные профили:")
        for name, url in results["found"]:
            print(f"  • {name}: {url}")


if __name__ == "__main__":
    try:
        print("== NickLock ==")
        print("Поиск профилей с никнеймом в популярных сервисах")
        user_input = input("Введите никнейм для поиска: ").strip()
        if user_input:
            check_username(user_input)
        else:
            print("Никнейм не может быть пустым.")
    except KeyboardInterrupt:
        print("\n\nВыход.")
        sys.exit(0)