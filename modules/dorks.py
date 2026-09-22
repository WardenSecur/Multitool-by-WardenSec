import sys
import readline

def q(base, keywords=None):
    if keywords:
        return f"{base} {keywords}".strip()
    return base


def dorks_by_nickname(nick, kw=None):
    return [
        q(f'"{nick}"', kw),
        q(f'"{nick}" site:vk.com', kw),
        q(f'"{nick}" site:ok.ru', kw),
        q(f'"{nick}" site:t.me', kw),
        q(f'"{nick}" site:github.com', kw),
        q(f'"{nick}" site:instagram.com', kw),
        q(f'"{nick}" site:twitter.com', kw),
        q(f'"{nick}" site:reddit.com', kw),
        q(f'"{nick}" site:youtube.com', kw),
        q(f'"{nick}" site:tiktok.com', kw),
        q(f'"{nick}" site:twitch.tv', kw),
        q(f'"{nick}" site:telegram.me', kw),
        q(f'"{nick}" site:discord.com', kw),
        q(f'"{nick}" site:steamcommunity.com', kw),
        q(f'"{nick}" site:last.fm', kw),
        q(f'"{nick}" site:spotify.com', kw),
        q(f'"{nick}" site:soundcloud.com', kw),
        q(f'"{nick}" site:freelancer.com', kw),
        q(f'"{nick}" site:upwork.com', kw),
        q(f'"{nick}" site:habr.com', kw),
        q(f'"{nick}" site:medium.com', kw),
        q(f'"{nick}" site:patreon.com', kw),
        q(f'"{nick}" site:onlyfans.com', kw),
        q(f'"{nick}" inurl:profile', kw),
        q(f'"{nick}" inurl:user', kw),
        q(f'"{nick}" inurl:id', kw),
        q(f'"{nick}" filetype:pdf', kw),
        q(f'"{nick}" filetype:doc', kw),
        q(f'"{nick}" filetype:xls', kw),
        q(f'"{nick}" email', kw),
        q(f'"{nick}" "@gmail.com"', kw),
        q(f'"{nick}" "@yandex.ru"', kw),
        q(f'"{nick}" "@mail.ru"', kw),
        q(f'"{nick}" phone', kw),
        q(f'"{nick}" telegram', kw),
    ]


def dorks_by_fio(fio, kw=None):
    parts = fio.split()
    first = parts[0] if parts else fio
    last = parts[-1] if len(parts) > 1 else ""
    middle = parts[1] if len(parts) > 2 else ""
    return [
        q(f'"{fio}"', kw),
        q(f'"{fio}" site:vk.com', kw),
        q(f'"{fio}" site:ok.ru', kw),
        q(f'"{fio}" site:facebook.com', kw),
        q(f'"{fio}" site:instagram.com', kw),
        q(f'"{fio}" site:t.me', kw),
        q(f'"{fio}" site:linkedin.com', kw),
        q(f'"{fio}" site:twitter.com', kw),
        q(f'"{fio}" site:youtube.com', kw),
        q(f'"{fio}" site:avito.ru', kw),
        q(f'"{fio}" site:youla.ru', kw),
        q(f'"{fio}" site:hh.ru', kw),
        q(f'"{fio}" site:superjob.ru', kw),
        q(f'"{fio}" site:rabota.ru', kw),
        q(f'"{fio}" site:gosuslugi.ru', kw),
        q(f'"{fio}" site:sudrf.ru', kw),
        q(f'"{fio}" site:fssp.gov.ru', kw),
        q(f'"{fio}" site:nalog.ru', kw),
        q(f'"{fio}" site:rusprofile.ru', kw),
        q(f'"{fio}" site:zachestnyibiznes.ru', kw),
        q(f'"{fio}" filetype:pdf', kw),
        q(f'"{fio}" filetype:doc', kw),
        q(f'"{fio}" filetype:xls', kw),
        q(f'"{fio}" резюме', kw),
        q(f'"{fio}" работа', kw),
        q(f'"{fio}" паспорт', kw),
        q(f'"{fio}" прописка', kw),
        q(f'"{fio}" телефон', kw),
        q(f'"{fio}" email', kw),
        q(f'"{fio}" суд', kw),
        q(f'"{fio}" пристав', kw),
        q(f'"{fio}" налог', kw),
        q(f'"{fio}" instagram', kw),
        q(f'"{fio}" telegram', kw),
        q(f'"{first} {last}"', kw),
        q(f'"{last} {first}"', kw),
        q(f'"{last} {first} {middle}"', kw),
    ]


def dorks_admin_panels(domain=None, kw=None):
    base = [
        'inurl:admin',
        'inurl:admin/login',
        'inurl:administrator',
        'inurl:wp-admin',
        'inurl:wp-login.php',
        'inurl:phpmyadmin',
        'inurl:pma',
        'inurl:cpanel',
        'inurl:webmail',
        'inurl:dashboard',
        'inurl:panel',
        'inurl:manager',
        'inurl:console',
        'inurl:adminpanel',
        'intitle:"admin panel"',
        'intitle:"login" inurl:admin',
        'inurl:admin.php',
        'inurl:admin/index.php',
        'inurl:admin/login.php',
        'inurl:/admin/account',
        'inurl:adminarea',
        'inurl:admin_area',
        'inurl:admincp',
        'inurl:moderator',
        'inurl:modcp',
        'inurl:staff',
        'inurl:controlpanel',
        'inurl:manage',
        'inurl:backend',
        'inurl:secure',
    ]
    out = []
    for d in base:
        s = d
        if domain:
            s = f'site:{domain} {s}'
        out.append(q(s, kw))
    return out


def dorks_storage(domain=None, kw=None):
    base = [
        'intitle:"index of"',
        'intitle:"index of /"',
        'intitle:"index of" "parent directory"',
        'intitle:"index of" "backup"',
        'intitle:"index of" "db"',
        'intitle:"index of" "sql"',
        'intitle:"index of" "config"',
        'intitle:"index of" "passwd"',
        'intitle:"index of" "etc"',
        'intitle:"index of" ".git"',
        'intitle:"index of" ".env"',
        'intitle:"index of" "uploads"',
        'intitle:"index of" "files"',
        'intitle:"index of" "private"',
        'intitle:"index of" "secret"',
        'filetype:sql',
        'filetype:sql "insert into"',
        'filetype:env',
        'filetype:log',
        'filetype:bak',
        'filetype:old',
        'filetype:zip "backup"',
        'filetype:tar.gz "backup"',
        'filetype:rar "backup"',
        'filetype:7z "backup"',
        'inurl:.git/config',
        'inurl:.env',
        'inurl:web.config',
        'inurl:phpinfo.php',
        'inurl:info.php',
        'inurl:test.php',
        'inurl:backup.sql',
        'inurl:db.sql',
        'inurl:dump.sql',
    ]
    out = []
    for d in base:
        s = d
        if domain:
            s = f'site:{domain} {s}'
        out.append(q(s, kw))
    return out


def dorks_cameras(domain=None, kw=None):
    base = [
        'inurl:view/view.shtml',
        'inurl:axis-cgi/mjpg',
        'inurl:/cgi-bin/mjpg/video.cgi',
        'intitle:"Live View / - AXIS"',
        'intitle:"Network Camera"',
        'intitle:"Webcam"',
        'intitle:"Live NetSnap Cam"',
        'intitle:"i-Catcher Console"',
        'inurl:8443 admin',
        'inurl:8080 login',
        'inurl:554',
    ]
    out = []
    for d in base:
        s = d
        if domain:
            s = f'site:{domain} {s}'
        out.append(q(s, kw))
    return out


def dorks_files(domain=None, kw=None):
    base = [
        'filetype:pdf "confidential"',
        'filetype:pdf "internal"',
        'filetype:xls "password"',
        'filetype:xls "login"',
        'filetype:doc "password"',
        'filetype:txt "password"',
        'filetype:csv "email"',
        'filetype:csv "phone"',
        'filetype:json "api_key"',
        'filetype:json "token"',
        'filetype:yml "password"',
        'filetype:conf "password"',
        'filetype:ini "password"',
        'filetype:xml "password"',
        'inurl:api/v1',
        'inurl:api/v2',
        'inurl:swagger',
        'inurl:swagger-ui.html',
        'inurl:api-docs',
        'inurl:graphql',
    ]
    out = []
    for d in base:
        s = d
        if domain:
            s = f'site:{domain} {s}'
        out.append(q(s, kw))
    return out


def dorks_vuln(domain=None, kw=None):
    base = [
        'inurl:"?id="',
        'inurl:"?page="',
        'inurl:"?file="',
        'inurl:"?url="',
        'inurl:"?redirect="',
        'inurl:"?cmd="',
        'inurl:"?exec="',
        'inurl:"?query="',
        'inurl:"?search="',
        'inurl:"?cat="',
        'inurl:"?product="',
        'inurl:"?item="',
        'inurl:"?view="',
        'inurl:"?lang="',
        'inurl:"?path="',
        'inurl:"?include="',
        'inurl:"?load="',
        'inurl:"?template="',
        'inurl:"?dir="',
        'inurl:"?download="',
    ]
    out = []
    for d in base:
        s = d
        if domain:
            s = f'site:{domain} {s}'
        out.append(q(s, kw))
    return out


def print_block(title, items):
    print(f"\n=== {title} ===")
    for i, d in enumerate(items, 1):
        print(f"  {i:>2}. {d}")


def main():
    print("=== DORK GEN ===")
    print("Генерация дорков под задачу")
    print("Что ищем?")
    print("  1. Ник / псевдоним")
    print("  2. ФИО")
    print("  3. Админ-панели")
    print("  4. Открытые хранилища / бекапы")
    print("  5. Камеры / веб-интерфейсы")
    print("  6. Утечки в файлах / API")
    print("  7. Точки для теста уязвимостей")
    print("  8. Всё сразу")
    choice = input("Выбери функцию: ").strip()

    domain = input("Домен (если есть, иначе Enter): ").strip() or None
    target = input("Цель (ник или ФИО, если нужно): ").strip()
    kw_input = input("Ключевые слова (город, сервис, год; через запятую, Enter если нет): ").strip()
    kw = " ".join(k.strip() for k in kw_input.split(",") if k.strip()) if kw_input else None

    if choice == "1":
        print_block("По нику", dorks_by_nickname(target, kw))
    elif choice == "2":
        print_block("По ФИО", dorks_by_fio(target, kw))
    elif choice == "3":
        print_block("Админ-панели", dorks_admin_panels(domain, kw))
    elif choice == "4":
        print_block("Хранилища", dorks_storage(domain, kw))
    elif choice == "5":
        print_block("Камеры", dorks_cameras(domain, kw))
    elif choice == "6":
        print_block("Файлы/API", dorks_files(domain, kw))
    elif choice == "7":
        print_block("Точки уязвимостей", dorks_vuln(domain, kw))
    elif choice == "8":
        if target:
            print_block("По нику", dorks_by_nickname(target, kw))
            print_block("По ФИО", dorks_by_fio(target, kw))
        print_block("Админ-панели", dorks_admin_panels(domain, kw))
        print_block("Хранилища", dorks_storage(domain, kw))
        print_block("Камеры", dorks_cameras(domain, kw))
        print_block("Файлы/API", dorks_files(domain, kw))
        print_block("Точки уязвимостей", dorks_vuln(domain, kw))
    else:
        print("Неверный выбор.")


if __name__ == "__main__":
    main()