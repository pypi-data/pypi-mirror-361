# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_text_name.py
"""

import sys
import unittest
import random

sys.path.append(".")

from itb_text_name import (
    adjust_spaces_on_punctuation,
    and_list,
    capitalize_name,
    get_gender,
    leet,
    map_special_chars,
    normalize_name,
    sort_names,
    could_be_a_name
)

reference_names = {
    'Georg Pfolz': {
        'prename': False,
        'lastname': False,
        'lowercase': 'georg pfolz',
        'capitalized': 'Georg Pfolz',
        'ascii': 'Georg Pfolz',
        'sort': 'Georg Pfolz',
        'gender': 'male',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Georg',
            'middle': '',
            'last': 'Pfolz',
            'suffix': '',
            'nickname': ''
        }
    },
    'Patrizia Höfstädter': {
        'prename': False,
        'lastname': False,
        'lowercase': 'patrizia höfstädter',
        'capitalized': 'Patrizia Höfstädter',
        'ascii': 'Patrizia Hoefstaedter',
        'sort': 'Patrizia Hofstadter',
        'gender': 'female',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Patrizia',
            'middle': '',
            'last': 'Höfstädter',
            'suffix': '',
            'nickname': ''
        }
    },
    'Eugénie Caraçon': {
        'prename': False,
        'lastname': False,
        'lowercase': 'eugénie caraçon',
        'capitalized': 'Eugénie Caraçon',
        'ascii': 'Eugenie Caracon',
        'sort': 'Eugenie Caracon',
        'gender': 'female',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Eugénie',
            'middle': '',
            'last': 'Caraçon',
            'suffix': '',
            'nickname': ''
        }
    },
    'Joanna MacArthur': {
        'prename': False,
        'lastname': False,
        'lowercase': 'joanna macarthur',
        'capitalized': 'Joanna MacArthur',
        'ascii': 'Joanna MacArthur',
        'sort': 'Joanna MacArthur',
        'gender': 'female',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Joanna',
            'middle': '',
            'last': 'MacArthur',
            'suffix': '',
            'nickname': ''
        }
    },
    'Sandra de Vitt': {
        'prename': False,
        'lastname': False,
        'lowercase': 'sandra de vitt',
        'capitalized': 'Sandra de Vitt',
        'ascii': 'Sandra de Vitt',
        'sort': 'Sandra de Vitt',
        'gender': 'female',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Sandra',
            'middle': '',
            'last': 'de Vitt',
            'suffix': '',
            'nickname': ''
        }
    },
    'Bea-Regina Obersteigen': {
        'prename': False,
        'lastname': False,
        'lowercase': 'bea-regina obersteigen',
        'capitalized': 'Bea-Regina Obersteigen',
        'ascii': 'Bea-Regina Obersteigen',
        'sort': 'Bea-Regina Obersteigen',
        'gender': 'female',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Bea-Regina',
            'middle': '',
            'last': 'Obersteigen',
            'suffix': '',
            'nickname': ''
        }
    },
    'Antun Meier-Lansky': {
        'prename': False,
        'lastname': False,
        'lowercase': 'antun meier-lansky',
        'capitalized': 'Antun Meier-Lansky',
        'ascii': 'Antun Meier-Lansky',
        'sort': 'Antun Meier-Lansky',
        'gender': 'male',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Antun',
            'middle': '',
            'last': 'Meier-Lansky',
            'suffix': '',
            'nickname': ''
        }
    },
    'Bogumila Österreicher': {
        'prename': False,
        'lastname': False,
        'lowercase': 'bogumila österreicher',
        'capitalized': 'Bogumila Österreicher',
        'ascii': 'Bogumila Oesterreicher',
        'sort': 'Bogumila Osterreicher',
        'gender': 'unknown',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Bogumila',
            'middle': '',
            'last': 'Österreicher',
            'suffix': '',
            'nickname': ''
        }
    },
    'Rafael': {
        'prename': True,
        'lastname': False,
        'lowercase': 'rafael',
        'capitalized': 'Rafael',
        'ascii': 'Rafael',
        'sort': 'Rafael',
        'gender': 'male',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Rafael',
            'middle': '',
            'last': '',
            'suffix': '',
            'nickname': ''
        }
    },
    'Maria Helena Blawatsky': {
        'prename': False,
        'lastname': False,
        'lowercase': 'maria helena blawatsky',
        'capitalized': 'Maria Helena Blawatsky',
        'ascii': 'Maria Helena Blawatsky',
        'sort': 'Maria Helena Blawatsky',
        'gender': 'female',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Maria',
            'middle': 'Helena',
            'last': 'Blawatsky',
            'suffix': '',
            'nickname': ''
        }
    },
    'DsZHkfNijWFPrET JGLAjuaqZ': {
        'prename': False,
        'lastname': False,
        'lowercase': 'dszhkfnijwfpret jglajuaqz',
        'capitalized': 'Dszhkfnijwfpret Jglajuaqz',
        'ascii': 'DsZHkfNijWFPrET JGLAjuaqZ',
        'sort': 'DsZHkfNijWFPrET JGLAjuaqZ',
        'gender': 'unknown',
        'is_a_name': False,
        'human_name': {
            'title': '',
            'first': 'DsZHkfNijWFPrET',
            'middle': '',
            'last': 'JGLAjuaqZ',
            'suffix': '',
            'nickname': ''
        }
    },
    'Bethy De La Cruz': {
        'prename': False,
        'lastname': False,
        'lowercase': 'bethy de la cruz',
        'capitalized': 'Bethy de la Cruz',
        'ascii': 'Bethy De La Cruz',
        'sort': 'Bethy De La Cruz',
        'gender': 'unknown',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Bethy',
            'middle': '',
            'last': 'De La Cruz',
            'suffix': '',
            'nickname': ''
        }
    },
    'Robert Štetić': {
        'prename': False,
        'lastname': False,
        'lowercase': 'robert štetić',
        'capitalized': 'Robert Štetić',
        'ascii': 'Robert Stetic',
        'sort': 'Robert Stetic',
        'gender': 'male',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': 'Robert',
            'middle': '',
            'last': 'Štetić',
            'suffix': '',
            'nickname': ''
        }
    },
    'Štetić': {
        'prename': False,
        'lastname': True,
        'lowercase': 'štetić',
        'capitalized': 'Štetić',
        'ascii': 'Stetic',
        'sort': 'Stetic',
        'gender': 'unknown',
        'is_a_name': True,
        'human_name': {
            'title': '',
            'first': '',
            'middle': '',
            'last': 'Štetić',
            'suffix': '',
            'nickname': ''
        }
    }
}

reference_names_sorted = [
    'Maria Helena Blawatsky',
    'Eugénie Caraçon',
    'Bethy De La Cruz',
    'Patrizia Höfstädter',
    'DsZHkfNijWFPrET JGLAjuaqZ',
    'Joanna MacArthur',
    'Antun Meier-Lansky',
    'Bea-Regina Obersteigen',
    'Bogumila Österreicher',
    'Georg Pfolz',
    'Rafael',
    'Štetić',
    'Robert Štetić',
    'Sandra de Vitt'
]

lower_text = 'das ist ein Beispiel-Text, der kapitalisiert werden kann.'

# Language Texts (for adjusting spaces on the indentation)
punct_texts = {
    'de': "Hallo Welt ! Wie geht es Ihnen ? Ich hoffe, Sie haben einen schönen Tag : Das Wetter ist herrlich . Wussten Sie, dass 75 % aller Statistiken erfunden sind?",
    'en': "Hello world ! How are you today ? I hope you're having a great day : The weather is lovely . Did you know that 80 % of all statistics are made up?",
    'fr': "Bonjour le monde! Comment allez-vous aujourd'hui? J'espère que vous passez une bonne journée: Le temps est magnifique . Saviez-vous que 85% des statistiques sont inventées?",
    'es': "¡Hola mundo! ¿Cómo estás hoy ? Espero que tengas un buen día : El clima es hermoso. ¿Sabías que el 90 % de las estadísticas son inventadas ?",
    'ro': "Salut lume! Cum ești azi? Sper că ai o zi bună: Vremea este minunată.Știai că 95 % din statistici sunt inventate?"
}

punct_texts_corrected = {
    'de': "Hallo Welt! Wie geht es Ihnen? Ich hoffe, Sie haben einen schönen Tag: Das Wetter ist herrlich. Wussten Sie, dass 75% aller Statistiken erfunden sind?",
    'en': "Hello world! How are you today? I hope you're having a great day: The weather is lovely. Did you know that 80% of all statistics are made up?",
    'fr': "Bonjour le monde\u202f! Comment allez-vous aujourd'hui\u202f? J'espère que vous passez une bonne journée\u202f: Le temps est magnifique. Saviez-vous que 85\u202f% des statistiques sont inventées\u202f?",
    'es': "¡\u202fHola mundo! ¿\u202fCómo estás hoy? Espero que tengas un buen día: El clima es hermoso. ¿\u202fSabías que el 90% de las estadísticas son inventadas?",
    'ro': "Salut lume\u202f! Cum ești azi\u202f? Sper că ai o zi bună\u202f: Vremea este minunată.Știai că 95% din statistici sunt inventate\u202f?"
}

class TestTextName(unittest.TestCase):
    def test_adjust_spaces_on_punctuation(self):
        for lang, text in punct_texts.items():
            print(f'Language: {lang}')
            try:
                corrected_text = adjust_spaces_on_punctuation(
                    text = text,
                    language = lang
                )
            except Exception as e:
                print(f'Error: {e}')
                raise AssertionError(f'Error: {e}')
            self.assertEqual(
                corrected_text,
                punct_texts_corrected[lang]
            )
    
    def test_and_list(self):
        a_list = [1, 'Georg', 'Haus', True]
        correct_str = '1, Georg, Haus and True'

        and_str = and_list(a_list)

        self.assertEqual(
            and_str,
            correct_str
        )

    # Deactivated for automatic tests because of errors in gitlab CI/CD
    # can be activated by changing the name of the function
    def do_not_test_leet(self):
        for _ in range(3):
            string_to_leet = random.choice(list(reference_names))
            max_length = random.randint(6, 12)
            start_at_begin = random.randint(0, 1)

            print(f'{string_to_leet} --> {leet(string_to_leet)}')
            leeted_text = leet(
                text=string_to_leet,
                max_length=max_length,
                start_at_begin=start_at_begin
            )
            print(
                f'{string_to_leet}, {max_length = }  {start_at_begin = } --> {leeted_text}'
            )

        # because of the use of random, using Asserts does not make any sense here

    def test_capitalize_name(self):
        for name_dict in reference_names.values():
            capitalized_name = capitalize_name(
                text=name_dict.get('lowercase')
            )
            self.assertEqual(
                name_dict.get('capitalized'),
                capitalized_name
            )

    def test_get_gender(self):
        for name, name_dict in reference_names.items():
            correct_gender = name_dict.get('gender')
            gender = get_gender(name.split()[0])  # prename

            try:
                self.assertEqual(
                    gender,
                    correct_gender
                )
            except AssertionError:
                msg = f'{gender} != {correct_gender} for {name}'
                raise AssertionError(msg)

    def test_map_special_chars(self):
        for name, name_dict in reference_names.items():
            correct_ascii = name_dict.get('ascii')
            ascii_str = map_special_chars(text=name)

            try:
                self.assertEqual(
                    ascii_str,
                    correct_ascii
                )
            except AssertionError:
                msg = f'ASCII: {ascii_str} != {correct_ascii} for {name}'
                raise AssertionError(msg)

    def test_map_special_chars_sort(self):
        for name, name_dict in reference_names.items():
            correct_sort = name_dict.get('sort')
            sort_str = map_special_chars(text=name, sort=True)

            try:
                self.assertEqual(
                    sort_str,
                    correct_sort
                )
            except AssertionError:
                msg = f'SORT: {sort_str} != {correct_sort} for {name}'
                raise AssertionError(msg)

    def test_normalize_name(self):
        for name, name_dict in reference_names.items():
            normalized_name = normalize_name(
                name=name,
                lastname=name_dict['lastname']
            )
            self.assertEqual(
                name,
                normalized_name
            )

            name_data = normalize_name(
                name=name,
                lastname=name_dict['lastname'],
                returning='dict'
            )
            self.assertEqual(
                name_dict.get('human_name'),
                name_data
            )

    def test_sort_names(self):
        names_list = list(reference_names)
        sorted_names = sort_names(names=names_list)

        self.assertEqual(
            sorted_names,
            reference_names_sorted
        )

    def test_could_be_a_name(self):
        for name, vals in reference_names.items():
            kwargs = {'name': name}

            if ' ' not in name:
                kwargs['prename'] = True

            self.assertEqual(
                could_be_a_name(**kwargs),
                vals.get('is_a_name'),
                f'could_be_a_name failed on {name}'
            )


if __name__ == '__main__':
    unittest.main()
