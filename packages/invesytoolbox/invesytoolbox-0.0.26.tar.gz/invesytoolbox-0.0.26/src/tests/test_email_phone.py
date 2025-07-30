# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_data.py
"""

import sys
import unittest

from itb_email_phone import (
    compare_phonenumbers,
    create_email_message,
    process_phonenumber
)
import email
from itertools import combinations

sys.path.append(".")

phonenumbers = {
    '(699) 123 456 789': {
        'international': '+43 699 123456789',
        'national': '0699 123456789',
        'E164': '+43699123456789'
    },
    '01 456 789': {
        'international': '+43 1 456789',
        'national': '01 456789',
        'E164': '+431456789'
    },
    '+12124567890': {
        'international': '+1 212-456-7890',
        'national': '(212) 456-7890',
        'E164': '+12124567890'
    },
    '+32 460224965': {
        'international': '+32 460 22 49 65',
        'national': '0460 22 49 65',
        'E164': '+32460224965'
    }
}

email_data = {
    'mail_from': 'test@invesy.work',
    'subject': 'Testing email message',
    'text': 'Ein Text mit Umlauten öäüß',
    'mail_to': 'georg.tester@test.at',
    'html': '<html><body><p>Ein Text mit Umlauten öäüß</p></body></html>',
}

email_msg_boundary = '===============0423875057181292250=='
email_msg_str = f'Content-Type: multipart/alternative; boundary="{email_msg_boundary}"\nMIME-Version: 1.0\nSubject: Testing email message\nFrom: test@invesy.work\nTo: georg.tester@test.at\n\n--===============0423875057181292250==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: base64\n\nRWluIFRleHQgbWl0IFVtbGF1dGVuIMO2w6TDvMOf\n\n--===============0423875057181292250==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: base64\n\nPGh0bWw+PGJvZHk+PHA+RWluIFRleHQgbWl0IFVtbGF1dGVuIMO2w6TDvMOfPC9wPjwvYm9keT48\nL2h0bWw+\n\n--===============0423875057181292250==--\n'


class TestEmailPhone(unittest.TestCase):
    def test_create_email_message(self):
        email_msg = create_email_message(**email_data)
        if not isinstance(email_msg, email.mime.multipart.MIMEMultipart):
            raise AssertionError('Email message is not email.mime.multipart.MIMEMultipart')
        email_msg.set_boundary(email_msg_boundary)
        self.assertEqual(
            email_msg_str,
            str(email_msg)
        )

    def test_process_phonenumber(self):
        for pn, data in phonenumbers.items():
            for fmt in (
                'international',
                'national',
                'E164'
            ):
                self.assertEqual(
                    data[fmt],
                    process_phonenumber(
                        pn,
                        numberfmt=fmt,
                        country='AT'
                    )
                )

    # use dedicated data for correct results
    def not_yet_test_compare_phonenumbers(self):
        for pn, data in phonenumbers.items():
            for fmt in (
                'international',
                'national',
                'E164'
            ):
                for ignore_invalid in (True, False):
                    for country in ('at', 'us'):
                        # first we compare the pairs, which should be different
                        for number_pair in list(
                            combinations(phonenumbers, r=2)
                        ):
                            number1, number2 = number_pair

                            message = (
                                f'1 - numbers: {number1}, {number2}, '
                                f'ignore_invalid: {ignore_invalid}, '
                                f'country: {country}, '
                                f'numberfmt: {fmt}'
                            )
                            self.assertEqual(
                                False,
                                compare_phonenumbers(
                                    number1=number1,
                                    number2=number2,
                                    numberfmt=fmt,
                                    country=country,
                                    ignore_invalid=ignore_invalid
                                ),
                                message
                            )

                        # now we compare the different versions of the same number,
                        # which should be identical except if invalid
                        for number1, numbers in phonenumbers.items():
                            number2 = numbers.get(fmt)
                            number1_processed = process_phonenumber(
                                phonenumber=number1,
                                numberfmt=fmt,
                                country=country,
                                omit_error_str=ignore_invalid
                            )
                            number2_processed = process_phonenumber(
                                phonenumber=number2,
                                numberfmt=fmt,
                                country=country,
                                omit_error_str=ignore_invalid
                            )

                            compare_result = True
                            invalid = False

                            for invalid_str in ('invalid', 'impossible'):
                                if (
                                    invalid_str in number1_processed
                                    or invalid_str in number2_processed
                                ):
                                    invalid = True
                                    break

                                if not ignore_invalid and invalid:
                                    compare_result = False

                                message = (
                                    f'2 - numbers: {number1} ({number1_processed}), '
                                    f'{number2} ({number2_processed}), '
                                    f'ignore_invalid: {ignore_invalid}, '
                                    f'country: {country}, '
                                    f'numberfmt: {fmt}'
                                )
                                self.assertEqual(
                                    compare_result,
                                    compare_phonenumbers(
                                        number1=number1,
                                        number2=number2,
                                        numberfmt=fmt,
                                        ignore_invalid=ignore_invalid
                                    ),
                                    message
                                )


if __name__ == '__main__':
    unittest.main()

    # print('finished format tests.')
