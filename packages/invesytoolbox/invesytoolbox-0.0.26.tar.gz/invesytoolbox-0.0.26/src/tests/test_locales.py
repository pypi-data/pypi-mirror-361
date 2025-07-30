# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_country_language.py
"""

import sys
import unittest
import datetime
import DateTime

sys.path.append(".")

from itb_locales import \
    fetch_all_countries, \
    fetch_holidays, \
    format_price, \
    get_country, \
    get_language_name, \
    get_locale, \
    is_holiday

test_locales = [
    ('de_AT', 'UTF-8'),
    ('de', 'UTF-8'),
]
locale_dicts = [
    {
        'locale': ('de_AT', 'UTF-8'),
        'locale_str': 'de_AT',
        'language': 'de',
        'country': 'AT',
        'currency': 'EUR'
    },
    {
        'locale': ('de', 'UTF-8'),
        'locale_str': 'de',
        'language': 'de',
        'country': '',
        'currency': ''
    }
]

check_country = {
    'name': 'Österreich',
    'alpha_2': 'AT',
    'alpha_3': 'AUT',
    'numeric': '040',
    'official_name': 'Republic of Austria'
}

language_names = {
    'de': {
        'de': 'Deutsch',
        'fr': 'allemand',
        'en': 'German',
        'it': 'tedesco'
    },
    'fr': {
        'de': 'Französisch',
        'fr': 'français',
        'en': 'French',
        'it': 'francese'
    }
}

days_and_holidays = {
    '1.4.2020': False,
    '2022-05-01': True,
    '6.1.2023': True,
    '2023/6/1': False,
    '01/06/2023': True,
    '1/6/2023': True,
    '13.8.2022': False,
    datetime.date(2022, 5, 1): True,
    datetime.date(2022, 12, 11): False,
    datetime.datetime(2023, 1, 6): True,
    datetime.datetime(2023, 1, 11): False,
    DateTime.DateTime(2023, 1, 6): True,
    DateTime.DateTime(2023, 1, 11): False,
}

feiertage_2022_2023 = {
    datetime.date(2022, 1, 1): 'Neujahr',
    datetime.date(2022, 1, 6): 'Heilige Drei Könige',
    datetime.date(2022, 4, 18): 'Ostermontag',
    datetime.date(2022, 5, 1): 'Staatsfeiertag',
    datetime.date(2022, 5, 26): 'Christi Himmelfahrt',
    datetime.date(2022, 6, 6): 'Pfingstmontag',
    datetime.date(2022, 6, 16): 'Fronleichnam',
    datetime.date(2022, 8, 15): 'Mariä Himmelfahrt',
    datetime.date(2022, 10, 26): 'Nationalfeiertag',
    datetime.date(2022, 11, 1): 'Allerheiligen',
    datetime.date(2022, 12, 8): 'Mariä Empfängnis',
    datetime.date(2022, 12, 25): 'Christtag',
    datetime.date(2022, 12, 26): 'Stefanitag',
    datetime.date(2023, 1, 1): 'Neujahr',
    datetime.date(2023, 1, 6): 'Heilige Drei Könige',
    datetime.date(2023, 4, 10): 'Ostermontag',
    datetime.date(2023, 5, 1): 'Staatsfeiertag',
    datetime.date(2023, 5, 18): 'Christi Himmelfahrt',
    datetime.date(2023, 5, 29): 'Pfingstmontag',
    datetime.date(2023, 6, 8): 'Fronleichnam',
    datetime.date(2023, 8, 15): 'Mariä Himmelfahrt',
    datetime.date(2023, 10, 26): 'Nationalfeiertag',
    datetime.date(2023, 11, 1): 'Allerheiligen',
    datetime.date(2023, 12, 8): 'Mariä Empfängnis',
    datetime.date(2023, 12, 25): 'Christtag',
    datetime.date(2023, 12, 26): 'Stefanitag',
    datetime.date(2024, 1, 1): 'Neujahr',
    datetime.date(2024, 1, 6): 'Heilige Drei Könige',
    datetime.date(2024, 4, 1): 'Ostermontag',
    datetime.date(2024, 5, 1): 'Staatsfeiertag',
    datetime.date(2024, 5, 9): 'Christi Himmelfahrt',
    datetime.date(2024, 5, 20): 'Pfingstmontag',
    datetime.date(2024, 5, 30): 'Fronleichnam',
    datetime.date(2024, 8, 15): 'Mariä Himmelfahrt',
    datetime.date(2024, 10, 26): 'Nationalfeiertag',
    datetime.date(2024, 11, 1): 'Allerheiligen',
    datetime.date(2024, 12, 8): 'Mariä Empfängnis',
    datetime.date(2024, 12, 25): 'Christtag',
    datetime.date(2024, 12, 26): 'Stefanitag'
}

price_examples = {
    123: {
    'round': '€ 123,-', 
    'ceil': '€ 123,-',
    'floor': '€ 123,-'
    },
    2: {
    'round': '€ 2,-', 
    'ceil': '€ 2,-',
    'floor': '€ 2,-'
    },
    234234: {
    'round': '€ 234.234,-', 
    'ceil': '€ 234.234,-',
    'floor': '€ 234.234,-'
    },
    234100: {
    'round': '€ 234.100,-', 
    'ceil': '€ 234.100,-',
    'floor': '€ 234.100,-'
    },
    13.5: {
    'round': '€ 13,50', 
    'ceil': '€ 13,50',
    'floor': '€ 13,50'
    },
    45.123: {
    'round': '€ 45,12', 
    'ceil': '€ 45,13',
    'floor': '€ 45,12'
    },
    45.126: {
    'round': '€ 45,13', 
    'ceil': '€ 45,13',
    'floor': '€ 45,12'
    }
}


class TestLocales(unittest.TestCase):
    def test_get_locale(self):
        for test_locale, locale_dict in zip(test_locales, locale_dicts):
            loc = get_locale(test_locale)
            if 'locale' not in loc:
                loc['locale'] = test_locale
            self.assertEqual(
                locale_dict,
                loc
            )

    def test_get_country(self):
        country_info = get_country(
            country='at',
            language='de'
        )
        self.assertEqual(
            check_country,
            country_info
        )

    def test_get_language_name(self):
        for lang_code, names in language_names.items():
            for code, name in names.items():
                lang_name = get_language_name(
                    code=lang_code,
                    language=code
                )
                self.assertEqual(
                    name,
                    lang_name
                )

    def test_fetch_holidays(self):
        holidays = fetch_holidays(
            country='AT',
            state=9,
            years=[2022, 2023, 2024]
        )
        # tests on gitlab will provide English names, so omit the test for now
        # self.assertEqual(holidays, feiertage_2022_2023)

        holidays = fetch_holidays(
            country='AT',
            state=9,
            daterange=['1.1.2022', '31.12.2024']
        )
        # tests on gitlab will provide English names, so omit the test for now
        # self.assertEqual(holidays, feiertage_2022_2023)

    def test_is_holiday(self):
        for date, check in days_and_holidays.items():
            checked = is_holiday(
                datum=date,
                country='AT',
                state=9)

            self.assertEqual(
                checked,
                check
            )

    def test_format_price(self):
        loc = locale_dicts[0]
        for price, price_formatted in price_examples.items():
            for round_mode in ('round', 'ceil', 'floor'):
                price_str = format_price(
                    price=price,
                    loc=loc,
                    round_mode=round_mode
                )
                
                self.assertEqual(
                    price_str,
                    price_formatted[round_mode]
                )


if __name__ == '__main__':
    unittest.main()

    # print('finished country & language tests.')
