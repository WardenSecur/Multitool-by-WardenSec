import sys
import re
import readline

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, number_type, PhoneNumberType
except ImportError:
    print("[-] Установи: pip install phonenumbers")
    sys.exit(1)


# DEF-коды РФ: префикс (после +7) -> регион
DEF_CODES_RU = {
    "900": "Москва и область", "901": "Москва и область", "902": "Москва и область",
    "903": "Москва и область", "904": "Москва и область", "905": "Москва и область",
    "906": "Москва и область", "907": "Москва и область", "908": "Москва и область",
    "909": "Москва и область", "910": "Москва и область", "911": "Северо-Запад",
    "912": "Урал", "913": "Сибирь", "914": "Дальний Восток", "915": "Москва и область",
    "916": "Москва и область", "917": "Москва и область", "918": "Юг",
    "919": "Москва и область", "920": "Москва и область", "921": "Северо-Запад",
    "922": "Урал", "923": "Сибирь", "924": "Дальний Восток", "925": "Москва и область",
    "926": "Москва и область", "927": "Поволжье", "928": "Юг",
    "929": "Москва и область", "930": "Москва и область", "931": "Северо-Запад",
    "932": "Урал", "933": "Сибирь", "934": "Дальний Восток", "936": "Москва и область",
    "937": "Поволжье", "938": "Юг", "939": "Москва и область",
    "950": "Москва и область", "951": "Северо-Запад", "952": "Урал",
    "953": "Сибирь", "954": "Дальний Восток", "955": "Москва и область",
    "956": "Поволжье", "957": "Юг", "958": "Москва и область",
    "960": "Москва и область", "961": "Северо-Запад", "962": "Урал",
    "963": "Сибирь", "964": "Дальний Восток", "965": "Москва и область",
    "966": "Поволжье", "967": "Юг", "968": "Москва и область",
    "969": "Москва и область",
    "977": "Москва и область", "978": "Крым", "980": "Москва и область",
    "981": "Северо-Запад", "982": "Урал", "983": "Сибирь",
    "984": "Дальний Восток", "985": "Москва и область", "986": "Поволжье",
    "987": "Юг", "988": "Юг", "989": "Юг",
    "991": "Москва и область", "992": "Урал", "993": "Сибирь",
    "994": "Дальний Восток", "995": "Юг", "996": "Москва и область",
    "997": "Москва и область", "999": "Москва и область",
}

# Более точные привязки для популярных DEF-кодов
DEF_DETAILED_RU = {
    "903": "Москва", "905": "Москва", "906": "Москва", "909": "Москва",
    "910": "Москва", "915": "Москва", "916": "Москва", "917": "Москва",
    "925": "Москва", "926": "Москва", "929": "Москва", "999": "Москва",
    "911": "Санкт-Петербург", "921": "Санкт-Петербург", "931": "Санкт-Петербург",
    "950": "Санкт-Петербург", "961": "Санкт-Петербург",
    "912": "Екатеринбург", "922": "Екатеринбург", "932": "Екатеринбург",
    "952": "Екатеринбург", "982": "Екатеринбург",
    "913": "Новосибирск", "923": "Новосибирск", "933": "Новосибирск",
    "953": "Новосибирск", "983": "Новосибирск",
    "914": "Владивосток", "924": "Владивосток", "934": "Владивосток",
    "954": "Владивосток", "984": "Владивосток",
    "927": "Казань", "937": "Казань", "956": "Казань", "986": "Казань",
    "918": "Краснодар", "928": "Краснодар", "938": "Краснодар",
    "958": "Краснодар", "988": "Краснодар",
    "978": "Симферополь", "978": "Крым",
}


def get_ru_region(national_number):
    """Определяет регион по DEF-коду для РФ."""
    s = str(national_number)
    if len(s) < 10:
        return None
    # отсекаем 9 в начале (мобильный код РФ начинается с 9)
    prefix = s[:3]
    if prefix in DEF_DETAILED_RU:
        return DEF_DETAILED_RU[prefix]
    if prefix in DEF_CODES_RU:
        return DEF_CODES_RU[prefix]
    return None


def type_name(num_type):
    types = {
        PhoneNumberType.MOBILE: "Мобильный",
        PhoneNumberType.FIXED_LINE: "Стационарный",
        PhoneNumberType.FIXED_LINE_OR_MOBILE: "Стационарный/Мобильный",
        PhoneNumberType.TOLL_FREE: "Бесплатный",
        PhoneNumberType.PREMIUM_RATE: "Премиум",
        PhoneNumberType.SHARED_COST: "Shared cost",
        PhoneNumberType.VOIP: "VoIP",
        PhoneNumberType.PERSONAL_NUMBER: "Личный",
        PhoneNumberType.PAGER: "Пейджер",
        PhoneNumberType.UAN: "UAN",
        PhoneNumberType.VOICEMAIL: "Голосовая почта",
        PhoneNumberType.UNKNOWN: "Неизвестно",
    }
    return types.get(num_type, "Неизвестно")


def lookup(number, region=None):
    try:
        parsed = phonenumbers.parse(number, region)
    except phonenumbers.NumberParseException as e:
        print(f"[-] Ошибка разбора: {e}")
        return

    if not phonenumbers.is_valid_number(parsed):
        print("[-] Номер невалиден.")
        return

    print("\n=== РЕЗУЛЬТАТ ===")
    print(f"Номер:          {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
    print(f"Национальный:   {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)}")
    print(f"E.164:          {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}")
    print(f"Код страны:     +{parsed.country_code}")
    print(f"Регион (phonenumbers): {geocoder.description_for_number(parsed, 'ru') or geocoder.description_for_number(parsed, 'en')}")
    print(f"Оператор:       {carrier.name_for_number(parsed, 'ru') or carrier.name_for_number(parsed, 'en') or 'неизвестно'}")
    print(f"Тип линии:      {type_name(number_type(parsed))}")
    tz = timezone.time_zones_for_number(parsed)
    print(f"Часовой пояс:   {', '.join(tz) if tz else 'неизвестно'}")
    print(f"Возможен:       {'да' if phonenumbers.is_possible_number(parsed) else 'нет'}")

    # Точный регион по DEF-коду для РФ
    if parsed.country_code == 7:
        nat = parsed.national_number
        ru_region = get_ru_region(nat)
        if ru_region:
            print(f"Регион (DEF):   {ru_region}")
        else:
            print("Регион (DEF):   не определён")


def main():
    print("=== PHONE LOOKUP ===")
    number = input("Введите номер (например +79991234567): ").strip()
    if not number:
        print("[-] Пусто.")
        return
    region = input("Код страны по умолчанию (RU, US, KZ... Enter если номер с +): ").strip().upper() or None
    lookup(number, region)


if __name__ == "__main__":
    main()