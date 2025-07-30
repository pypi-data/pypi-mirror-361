# -*- coding: utf-8 -*-
"""
=================
email_phone_tools
=================
"""

from typing import Union, List, Dict
import phonenumbers
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase

from itb_locales import get_locale

mycountry = get_locale().get('country')


def check_spam(
    text: str,
    spamwords: str,
    subject: str = '',
    allow_url: bool = False

) -> float:
    """
    Check for spam

    This is intended for checking for spam in web forms,
    usually before the submitted data is sent or stored.

    There are no positional arguments because it must be clear
    if a mail message or a mail body text is provided

    :param spamwords: the list has to be provided!
    :param text: only provide the text of the mail body
    :param allow_url: if False, no URLs are allowed in the message text
    """
    score = 0.0

    def set_score():
        global score
        if not score:
            score = 9.0
        else:
            score += 0.1

    for prot in ['http://', 'https://']:
        if prot in subject:
            set_score()

        if not allow_url:
            spamwords.append(prot)

    for t in (text, subject):
        for spamword in spamwords:
            if spamword in t:
                set_score()

    return score


def create_email_message(
    mail_from: str,
    subject: str,
    text: str,
    mail_to: str = None,
    cc: str = None,
    bcc: str = None,
    html: str = None,
    attachments: List[Dict] = None,
    encoding: str = 'utf-8'
) -> str:
    """ Create a valid email message

    .. note:: it is possible to not have a **mail_to**,
       if there is a **cc** or **bcc**.
    """

    if attachments:
        msg = MIMEMultipart('mixed')
        body = MIMEMultipart('alternative')
    elif text and html:
        msg = MIMEMultipart('alternative')
        body = None
    else:
        msg = MIMEMultipart('alternative')
        body = None

    msg['Subject'] = subject
    msg['From'] = mail_from

    if not (mail_to or cc or bcc):
        raise Exception(
            'mailMessage needs mail_to or cc or bcc!'
        )

    if mail_to:
        msg['To'] = mail_to
    if cc:
        msg['CC'] = cc
    if bcc:
        msg['BCC'] = bcc

    mime_text = MIMEText(text, 'plain', encoding)
    mime_html = None
    
    if html:
        mime_html = MIMEText(html, 'html', encoding)

    if body:
        body.attach(mime_text)
        if html:
            body.attach(mime_html)
        msg.attach(body)
    else:
        msg.attach(mime_text)
        if html:
            msg.attach(mime_html)

    for attachment in attachments or []:
        attPart = MIMEBase(
            'application',
            'octet-stream'
        )
        attPart.set_payload(attachment['data'])
        encoders.encode_base64(attPart)
        attPart.add_header(
            'Content-Disposition',
            f"attachment; filename={attachment['filename']}"
        )
        msg.attach(attPart)

    return msg


def process_phonenumber(
    phonenumber: str,
    numberfmt: str = 'international',
    checkonly: bool = False,
    empty_if_invalid: bool = False,
    omit_error_str: bool = False,
    country=mycountry
) -> Union[str, bool]:
    """ Checks if a phonenumber is valid returns in specified format.

    :param phonenumber: phone number string to be processed
    :param numberfmt: format in which the number is returned

        * international (default)
        * national
        * E164 (international, condensed)

    :param checkonly: only check if the number is valid (returns boolean)
    :param empty_if_invalid: returns an empty string if the number is not valid
        (only if checkonly is False)
    """

    phonenumber = ''.join(c for c in phonenumber if c in '01234567890+')

    try:
        pn = phonenumbers.parse(phonenumber, country)  # country code will be parsed nonetheless
    except phonenumbers.phonenumberutil.NumberParseException:
        error_str = ' (not a phone number)'
        return phonenumber + error_str

    error_str = ''

    if not phonenumbers.is_possible_number(pn):
        if checkonly:
            return False
        else:
            error_str = ' (impossible)'

    elif not phonenumbers.is_valid_number(pn):
        if checkonly:
            return False
        else:
            error_str = ' (invalid)'

    if checkonly:
        return True
    else:
        if empty_if_invalid and error_str:
            return ''

        try:
            phonefmt = getattr(phonenumbers.PhoneNumberFormat, numberfmt.upper())
        except AttributeError:
            raise AttributeError('numberfmt must be "international", "national" or "E164"!')

        return phonenumbers.format_number(
            pn,
            phonefmt
        ) + (error_str if not omit_error_str else '')


def compare_phonenumbers(
    number1: str,
    number2: str,
    numberfmt: str = 'international',
    country=mycountry,
    ignore_invalid: bool = True
) -> bool:
    """ Compares two phone numbers, returns True if they are identical

    :param number1: phone number string to be processed
    :param number2: phone number string to be processed
    :param numberfmt: format in which the numbers are processed

        * international (default)
        * national
        * E164 (international, condensed)
    """
    if not number1 or not number2:
        return False

    number1_processed = process_phonenumber(
        number1,
        numberfmt=numberfmt,
        omit_error_str=ignore_invalid,
        country=country
    )
    number2_processed = process_phonenumber(
        number2,
        numberfmt=numberfmt,
        omit_error_str=ignore_invalid,
        country=country
    )

    if not ignore_invalid:  # only for better perfomance
        for error_str in ('invalid', 'impossible', 'not a phone number'):
            if error_str in number1_processed or error_str in number2_processed:
                return False

    is_equal = False
    if number1_processed and number2_processed:
        is_equal = number1_processed == number2_processed

    if not is_equal:  # try another route
        number1 = ''.join(c for c in number1 if c in '01234567890').lstrip('0')
        number2 = ''.join(c for c in number2 if c in '01234567890').lstrip('0')
        is_equal = number1 == number2

    return is_equal
