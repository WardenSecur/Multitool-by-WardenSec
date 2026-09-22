import requests
import sys
import re
import json
import time
import socket
import ssl
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import urllib3
import readline

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIMEOUT = 6
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) SecurityScanner/2.0"}
MAX_WORKERS = 25

ADMIN_PATHS = [
    "/admin", "/admin/", "/admin/login", "/wp-admin", "/wp-login.php",
    "/phpmyadmin", "/pma", "/administrator", "/cpanel", "/login",
    "/dashboard", "/adminpanel", "/manager", "/console", "/webadmin",
    "/admin.php", "/admin.html", "/admin_area", "/moderator"
]

SENSITIVE_PATHS = [
    "/.git/config", "/.git/HEAD", "/.env", "/.env.bak", "/.htaccess",
    "/.htpasswd", "/backup.zip", "/backup.tar.gz", "/backup.sql",
    "/db.sql", "/dump.sql", "/database.sql", "/config.php.bak",
    "/web.config", "/.svn/entries", "/.DS_Store", "/composer.json",
    "/package.json", "/.aws/credentials", "/id_rsa", "/server-status",
    "/phpinfo.php", "/info.php", "/test.php", "/debug.log", "/error.log"
]

FUZZ_WORDS = [
    "admin", "login", "test", "backup", "old", "dev", "api", "v1", "v2",
    "uploads", "files", "private", "secret", "config", "db", "sql", "tmp",
    "backup", "bak", "data", "logs", "internal", "staging", "prod", "beta",
    "user", "users", "account", "accounts", "panel", "portal", "secure"
]

SQL_PAYLOADS = [
    "'", "\"", "1' OR '1'='1", "1' AND SLEEP(0)--", "' OR 1=1--",
    "1' UNION SELECT NULL--", "admin'--", "' OR 'x'='x"
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><img src=x onerror=alert(1)>",
    "'><svg onload=alert(1)>",
    "javascript:alert(1)"
]

LFI_PAYLOADS = [
    "../../../../etc/passwd",
    "../../../../etc/hosts",
    "....//....//....//etc/passwd",
    "/etc/passwd",
    "..\\..\\..\\windows\\win.ini",
    "php://filter/convert.base64-encode/resource=index.php"
]

REDIRECT_PAYLOADS = [
    "http://evil.com",
    "//evil.com",
    "https://evil.com"
]

SSRF_PAYLOADS = [
    "http://127.0.0.1:80",
    "http://localhost:22",
    "http://169.254.169.254/latest/meta-data/",
    "file:///etc/passwd"
]

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]

SQL_ERRORS = [
    "sql syntax", "mysql_fetch", "mysql_num_rows", "you have an error in your sql",
    "warning: mysql", "unclosed quotation mark", "quoted string not properly terminated",
    "postgresql", "pg_query", "sqlite", "ora-", "microsoft ole db", "odbc sql"
]

LFI_INDICATORS = ["root:x:0:0", "[extensions]", "[fonts]", "daemon:x:", "bin/bash"]

found_vulns = []


def log(msg, tag="INFO"):
    colors = {"INFO": "\033[94m", "OK": "\033[92m", "WARN": "\033[93m", "VULN": "\033[91m", "END": "\033[0m"}
    print(f"{colors.get(tag, '')}[{tag}]{colors['END']} {msg}")


def record(vuln_type, url, detail=""):
    found_vulns.append({"type": vuln_type, "url": url, "detail": detail})
    log(f"{vuln_type} -> {url} {detail}", "VULN")


def normalize(url):
    if not url.startswith("http"):
        url = "http://" + url
    return url.rstrip("/")


def safe_get(url, allow_redirects=False, params=None):
    try:
        return requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                            allow_redirects=allow_redirects, verify=False, params=params)
    except Exception:
        return None


def safe_post(url, data=None, allow_redirects=False):
    try:
        return requests.post(url, headers=HEADERS, timeout=TIMEOUT,
                             allow_redirects=allow_redirects, verify=False, data=data)
    except Exception:
        return None


def check_path(base, path, label):
    url = base + path
    r = safe_get(url)
    if r and r.status_code in (200, 301, 302, 401, 403):
        size = len(r.content)
        if r.status_code == 200 and size > 0:
            record(label, url, f"[{r.status_code}] {size}b")
        elif r.status_code in (301, 302):
            record(f"{label} (redirect)", url, f"[{r.status_code}] -> {r.headers.get('Location', '?')}")
        elif r.status_code in (401, 403):
            log(f"[{r.status_code}] {url} (защищено, но существует)", "WARN")


def scan_paths(base, paths, label):
    log(f"Проверка: {label}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        list(ex.map(lambda p: check_path(base, p, label), paths))


def fuzz_dirs(base):
    log("Фаззинг директорий и файлов")
    words = []
    for w in FUZZ_WORDS:
        words.extend([f"/{w}/", f"/{w}.php", f"/{w}.html", f"/{w}.bak", f"/{w}.zip", f"/{w}.txt"])
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        list(ex.map(lambda p: check_path(base, p, "Фаззинг"), words))


def test_sql_get(base):
    log("SQL-инъекции в GET-параметрах")
    parsed = urlparse(base)
    if not parsed.query:
        log("Параметров нет, пропуск", "WARN")
        return
    params = parse_qs(parsed.query)
    for param in params:
        for payload in SQL_PAYLOADS:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urlencode(new_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            r = safe_get(test_url)
            if r:
                body = r.text.lower()
                if any(e in body for e in SQL_ERRORS):
                    record("SQLi (GET)", test_url, f"param={param}")
                    break


def test_sql_post(base):
    log("SQL-инъекции в POST-формах")
    r = safe_get(base)
    if not r:
        return
    soup = BeautifulSoup(r.text, "html.parser")
    forms = soup.find_all("form")
    for form in forms:
        action = form.get("action") or ""
        method = (form.get("method") or "get").lower()
        if method != "post":
            continue
        form_url = urljoin(base, action)
        inputs = form.find_all("input")
        data = {}
        for inp in inputs:
            name = inp.get("name")
            if not name:
                continue
            data[name] = "test"
        for payload in SQL_PAYLOADS:
            test_data = {k: payload for k in data}
            resp = safe_post(form_url, data=test_data)
            if resp and any(e in resp.text.lower() for e in SQL_ERRORS):
                record("SQLi (POST)", form_url, f"fields={list(data.keys())}")
                break


def test_xss_get(base):
    log("XSS (отражение) в GET-параметрах")
    parsed = urlparse(base)
    if not parsed.query:
        log("Параметров нет, пропуск", "WARN")
        return
    params = parse_qs(parsed.query)
    for param in params:
        for payload in XSS_PAYLOADS:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urlencode(new_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            r = safe_get(test_url)
            if r and payload in r.text:
                record("XSS (GET)", test_url, f"param={param}")


def test_xss_forms(base):
    log("XSS в формах (POST)")
    r = safe_get(base)
    if not r:
        return
    soup = BeautifulSoup(r.text, "html.parser")
    for form in soup.find_all("form"):
        action = form.get("action") or ""
        method = (form.get("method") or "get").lower()
        if method != "post":
            continue
        form_url = urljoin(base, action)
        inputs = form.find_all("input")
        data = {}
        for inp in inputs:
            name = inp.get("name")
            if not name:
                continue
            data[name] = "test"
        for payload in XSS_PAYLOADS:
            test_data = {k: payload for k in data}
            resp = safe_post(form_url, data=test_data)
            if resp and payload in resp.text:
                record("XSS (POST)", form_url, f"fields={list(data.keys())}")
                break


def test_lfi(base):
    log("LFI (Local File Inclusion)")
    parsed = urlparse(base)
    if not parsed.query:
        log("Параметров нет, пропуск", "WARN")
        return
    params = parse_qs(parsed.query)
    for param in params:
        for payload in LFI_PAYLOADS:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urlencode(new_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            r = safe_get(test_url)
            if r and any(i in r.text for i in LFI_INDICATORS):
                record("LFI", test_url, f"param={param}")


def test_open_redirect(base):
    log("Open Redirect")
    parsed = urlparse(base)
    if not parsed.query:
        log("Параметров нет, пропуск", "WARN")
        return
    params = parse_qs(parsed.query)
    for param in params:
        for payload in REDIRECT_PAYLOADS:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urlencode(new_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            r = safe_get(test_url, allow_redirects=False)
            if r and r.status_code in (301, 302) and "evil.com" in (r.headers.get("Location") or ""):
                record("Open Redirect", test_url, f"param={param}")


def test_ssrf(base):
    log("SSRF (базовая)")
    parsed = urlparse(base)
    if not parsed.query:
        log("Параметров нет, пропуск", "WARN")
        return
    params = parse_qs(parsed.query)
    for param in params:
        for payload in SSRF_PAYLOADS:
            new_params = params.copy()
            new_params[param] = [payload]
            new_query = urlencode(new_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            r = safe_get(test_url)
            if r and any(i in r.text for i in LFI_INDICATORS):
                record("SSRF (возможно)", test_url, f"param={param}")


def check_http_methods(base):
    log("Проверка HTTP-методов")
    for method in ["PUT", "DELETE", "TRACE", "OPTIONS", "PATCH"]:
        try:
            r = requests.request(method, base, headers=HEADERS, timeout=TIMEOUT, verify=False)
            if r.status_code in (200, 201, 204):
                record(f"HTTP метод {method}", base, f"[{r.status_code}]")
            if method == "OPTIONS" and "allow" in r.headers:
                log(f"Разрешённые методы: {r.headers['Allow']}")
        except Exception:
            pass


def check_headers(base):
    log("Заголовки безопасности")
    r = safe_get(base)
    if not r:
        return
    for h in SECURITY_HEADERS:
        if h not in r.headers:
            record("Отсутствует заголовок", base, h)
    if "Server" in r.headers:
        log(f"Server: {r.headers['Server']}", "WARN")
    if "X-Powered-By" in r.headers:
        log(f"X-Powered-By: {r.headers['X-Powered-By']}", "WARN")


def check_cookies(base):
    log("Флаги cookie")
    r = safe_get(base)
    if not r:
        return
    for cookie in r.cookies:
        issues = []
        if not cookie.secure:
            issues.append("нет Secure")
        if "httponly" not in [k.lower() for k in cookie._rest.keys()]:
            issues.append("нет HttpOnly")
        if issues:
            record("Cookie без флагов", base, f"{cookie.name}: {', '.join(issues)}")


def check_ssl(host):
    log("SSL/TLS")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                log(f"SSL OK, выдан: {cert.get('issuer')}", "OK")
    except Exception as e:
        log(f"SSL ошибка: {e}", "WARN")


def check_robots(base):
    log("robots.txt / sitemap.xml")
    for p in ["/robots.txt", "/sitemap.xml"]:
        r = safe_get(base + p)
        if r and r.status_code == 200:
            log(f"Найден {p}", "OK")
            if p == "/robots.txt":
                for line in r.text.splitlines():
                    if "disallow" in line.lower():
                        log(f"  {line.strip()}", "INFO")


def main():
    print("=" * 60)
    print("=== Security Checks ===")
    print("Анализ сайта на уязвимости")
    print("=" * 60)
    target = input("Введите URL сайта: ").strip()
    if not target:
        print("URL не введён.")
        sys.exit(1)
    base = normalize(target)
    host = urlparse(base).hostname
    log(f"Цель: {base}", "OK")

    start = time.time()

    check_headers(base)
    check_cookies(base)
    check_http_methods(base)
    check_robots(base)
    scan_paths(base, ADMIN_PATHS, "Админ-панели")
    scan_paths(base, SENSITIVE_PATHS, "Открытые конфиги/хранилища")
    fuzz_dirs(base)
    test_sql_get(base + "?id=1")
    test_sql_post(base)
    test_xss_get(base + "?q=test")
    test_xss_forms(base)
    test_lfi(base + "?file=test")
    test_open_redirect(base + "?url=test")
    test_ssrf(base + "?url=test")
    if host:
        check_ssl(host)

    elapsed = round(time.time() - start, 2)

    print("\n" + "=" * 60)
    print(f"  ИТОГИ: найдено {len(found_vulns)} потенциальных проблем за {elapsed}с")
    print("=" * 60)
    for v in found_vulns:
        print(f"[{v['type']}] {v['url']} {v['detail']}")



if __name__ == "__main__":
    main()