# -*- coding: utf-8 -*-
"""
data_tools
==========
"""

from typing import Union, List, Dict, Any, Optional
import DateTime
import datetime
import vobject
import pendulum
from dateutil.parser import parse
from itb_date_time import convert_datetime, str_to_date, str_to_DT, get_dateformat
from itb_email_phone import process_phonenumber

comma_float_chars = set(',1234567890')
datetime_chars = set('1234567890.-:/+ ')
time_chars = set('1234567890:')


def any_2boolean(
    value: Any
) -> bool:
    """ return a boolean for any value

    This function recognizes strings and bytes that signifie False, such as "False" or "0"
    """
    if not value:
        return False
    elif isinstance(value, (str, bytes)):
        if value.lower() in ('0', 'false', b'0', b'false'):
            return False
    return True


def dict_from_dict_list(
    dict_list: List[dict],
    key: str,
    single_value: Optional[str] = None,
    include_key: Optional[bool] = False
) -> dict:
    """ Create a dictionary from a list of dictionaries

    :param dictList: the list of dictionaries to be converted
    :param key: the key of the dictionaries to use as key for the new dictionary.
                This must be a unique key, otherwise the new dictionary will
                only contain the first result
    :param singleValue: only a single value for each key is provided (you have to provide the key)
    :param include_key: the value used as key is also included in values dictionary
    """

    dl = [dict(d) for d in dict_list]  # we copy the list because we will change the dictionaries (except for single_value)

    new_dict = {}

    for dictionary in dl:
        if single_value:
            new_dict[dictionary.pop(key)] = dictionary.get(single_value)
        elif include_key:
            new_dict[dictionary[key]] = dictionary
        else:
            # slick: pop the id and use it as key for newDict in one line
            new_dict[dictionary.pop(key)] = dictionary

    return new_dict


def create_vcard(
    data: Dict[str, str],
    returning: str = 'vcard'
) -> str:
    """ create a vCard from a dictionary

    .. note:: The serialized vcard has Windows line-breaks, which is fine, I guess
    .. note:: colons in notes are escaped in vobject

    :param data: keys:

        - prename
        - surname
        - email
        - phone
        - street
        - city
        - region (eg. federal state)
        - zipcode
        - country
    """

    prename = data.get('prename', '')
    surname = data.get('surname', '')
    if not prename and not surname:
        return None

    vcard = vobject.vCard()
    vcard.add('n')
    vcard.n.value = vobject.vcard.Name(
        family=surname,
        given=prename
    )
    vcard.add('fn')
    vcard.fn.value = f'{prename} {surname}'
    vcard.add('email')
    vcard.email.value = data.get('email', '')
    vcard.email.type_param = 'INTERNET'
    vcard.add('tel')
    phone = process_phonenumber(
        data.get('phone', ''),
        empty_if_invalid=True
    )
    if phone:
        vcard.tel.value = phone
        vcard.tel.type_param = ['CELL', 'VOICE']
    vcard.add('adr')
    vcard.adr.type_param = ['HOME', 'pref']
    vcard.adr.value = vobject.vcard.Address(
        street=data.get('street', ''),
        city=data.get('city', ''),
        region=data.get('region', ''),
        code=data.get('zipcode', ''),
        country=data.get('country', '')
    )
    vcard.add('note')
    vcard.note.value = data.get('note', '')

    if returning == 'pretty':
        return vcard.prettyPrint()
    else:
        return vcard.serialize()


def dict_2unicode(
    d: Dict[Union[str, bytes], Any],
    encoding: str = 'utf-8'
) -> dict:
    """ Convert all keys and values in a dictionary from bytes to unicode

    All keys and values are changed from bytes to unicode, if applicable.
    Other data types are left unchaged, including other compound data types.

    :param d: dictionary
    :param encoding: default is utf-8
    """

    return {
        k.decode(encoding) if isinstance(k, bytes) else k:
            (v.decode(encoding) if isinstance(v, bytes) else v)
            for k, v in d.items()
    }


def dict_2datatypes(
    d: dict,
    metadata: Dict[str, str] = {},
    convert_keys: bool = False,
    convert_to_unicode: bool = False,
    dt: str = 'datetime',
    fmt: str = None,
    timezone: str = 'local'
) -> Dict[Any, Any]:
    """ Convert all data of a dictionary to specific (json metadata) or guessed types

    :param d: dictionary
    :param metadata: dictionary containing types for the keys:
               - boolean
               - int
               - float
               - date
               - datetime: date and time
               - time: conversion or not based on dt
    :param convert_keys: convert keys to unicode
    :param convert_to_unicode: convert all bytes to unicode in the process
    :param dt: - datetime or dt
               - DateTime or DT
               - ignore or string
               - pendulum
               - default: datetime, because it's Python's default
    :param fmt: format for datetime parsing
    :param timezone: default is 'local', other options are 'UTC' or 'Europe/Vienna'
    """

    if convert_keys:
        return {
            value_2datatype(
                value=key,
                convert_to_unicode=convert_to_unicode,
                dt=dt,
                fmt=fmt
            ): value_2datatype(
                value=val,
                typ=metadata.get(key),
                key=key,
                convert_to_unicode=convert_to_unicode,
                dt=dt,
                fmt=fmt,
                timezone=timezone
            )
            for key, val in d.items()
        }  # dict comprehension
    else:
        return {
            key: value_2datatype(
                value=val,
                typ=metadata.get(key),
                key=key,
                convert_to_unicode=convert_to_unicode,
                dt=dt,
                fmt=fmt,
                timezone=timezone
            )
            for key, val in d.items()
        }  # dict comprehension


def dictlist_2datatypes(
    dictlist: List[Dict[Any, Any]],
    metadata: Dict[Any, Any] = {},
    convert_keys: bool = False,
    convert_to_unicode: bool = False,
    dt: str = 'datetime',
    fmt: str = None,
    timezone: str = 'local'
) -> list:
    """ Convert all data of a list of dictionaries to specific (json metadata) or guessed types

    :param dictList: list of dictionaries
    :param metadata: dictionary containing types for the keys:
                - boolean
                - int
                - float
                - date
                - datetime: date and time
                - time: conversion or not based on dt
    :param convert_keys: convert keys to unicode
    :param convert_to_unicode: convert all bytes to unicode in the process
    :param dt: - datetime or dt
               - DateTime or DT
               - ignore or string
               - pendulum
               - default: datetime, because it's Python's default
    :param fmt: format for datetime parsing
    :param timezone: default is 'local', other options are 'UTC' or 'Europe/Vienna'
    """
    return [
        dict_2datatypes(
            d=dic,
            metadata=metadata,
            convert_keys=convert_keys,
            convert_to_unicode=convert_to_unicode,
            dt=dt,
            fmt=fmt,
            timezone=timezone
        )
        for dic
        in dictlist
    ]


def sort_dictlist(
    dictlist: List[dict],
    keys: Union[str, List[str]],
    reverse: bool = False
) -> list:
    """ Sorts a list of dictionaries

    :param dictList: list of dictionaries
    :param keys: sort by these keys
    :param reverse: True reverses the sorting order

    .. deprecated:: 0.0.14
       install package multisort and use it instead
    """

    if isinstance(keys, str):
        if ',' in keys:
            keys = keys.replace(
                ' ', ''
            ).split(',')
        else:
            keys = [keys]

    if len(keys) == 1:
        key = keys[0]
        sorted_dictlist = sorted(
            dictlist,
            key=lambda i: i[key],
            reverse=reverse
        )
    else:
        sorted_dictlist = sorted(
            dictlist,
            key=lambda i: [i[key] for key in keys]
        )

    return sorted_dictlist


def value_2datatype(
    value,
    typ: str = None,
    key: str = None,
    convert_to_unicode: bool = False,
    encoding: str = 'utf-8',
    dt: str = 'datetime',
    fmt: str = None,
    timezone: str = 'local'
) -> Union[str, int, float]:
    """ Convert a value to a datatype

    this function has two modes:

    1. a type is provided for the conversion
    2. it makes educated guesses in converting a string

    :param value:
    :param typ: type for the conversion
    :param metadata: dictionary containing types for the keys:
               - string
               - boolean
               - int
               - float
               - date
               - datetime: date and time
               - time: conversion or not based on dt
    :param key: key in the metadata (value name)
    :param convert_to_unicode: convert all bytes to unicode in the process
    :param encoding: if bytes are present, use this encoding to convert them to unicode
    :param dt: - datetime or dt
               - DateTime or DT
               - ignore or string
               - pendulum
               - default: datetime, because it's Python's default
    :param timezone: default is 'local', other options are 'UTC' or 'Europe/Vienna'
    """
    if typ:
        if typ == 'ignore':
            return value
        elif typ == 'string':
            return str(value)
        elif typ == 'boolean':
            return any_2boolean(value=value)
        elif typ == 'int':
            try:
                return int(value)
            except ValueError:
                return value
        elif typ == 'float':
            value = value.replace(',', '.')
            try:
                return float(value)
            except ValueError:
                return value
        elif typ == 'date':
            if dt in ('datetime', 'dt'):
                return convert_datetime(
                    value,
                    convert_to='date',
                    fmt=fmt
                )
            elif dt in ('DateTime', 'DT'):
                if ' ' in value:
                    value = value.split()[0]  # get rid of time
                return DateTime.DateTime(
                    value,
                    datefmt='international'
                ) + 0.5  # to avoid day-shifting due to timezones, use 12am
            elif dt == 'pendulum':
                if fmt:
                    p_dt = pendulum.from_format(value, fmt)
                else:
                    p_dt = pendulum.parse(value)

                if p_dt.tzinfo == 'UTC' and timezone == 'local':
                    return p_dt.in_tz(pendulum.local_timezone())
                elif timezone:
                    return p_dt.in_tz(timezone)
                return p_dt.date()
            elif dt in ('ignore', 'string'):
                return value
            else:
                raise Exception(f'invalid value {dt} for argument dt')
        elif typ == 'datetime':
            if dt in ('datetime', 'dt'):
                return datetime.datetime.strptime(value, fmt)
            elif dt in ('DateTime', 'DT'):
                value = value.strip()
                try:
                    return DateTime.DateTime(
                        value,
                        datefmt='international'
                    )
                except DateTime.interfaces.SyntaxError:
                    return value
            elif dt == 'pendulum':
                if fmt:
                    p_dt = pendulum.from_format(value, fmt)
                else:
                    p_dt = pendulum.parse(value)

                if p_dt.tzinfo == 'UTC' and timezone == 'local':
                    return p_dt.in_tz(pendulum.local_timezone())
                elif timezone:
                    return p_dt.in_tz(timezone)
                return p_dt
            elif dt in ('ignore', 'string'):
                return value
            else:
                raise Exception(f'invalid value {dt} for argument dt')
        elif 'time' in typ:
            if 'datetime' in typ or dt in ('datetime', 'dt'):
                dt = parse(value)
                return dt.time()
            else:
                return value  # DT: return the string

    else:
        if isinstance(value, (bool, int, float)):
            return value

        original_value = value
        if isinstance(value, bytes):
            value = value.decode(encoding)

        if isinstance(value, str):
            value = value.strip()

            if value == 'False':
                return False

            if value == 'True':
                return True

            try:
                if (
                    ':' in value
                    and set(value).issubset(time_chars)
                    and (
                        len(value) == 5  # hh:mm
                        or len(value) == 8  # hh:mm:ss
                    )
                ):
                    if dt in ('datetime', 'dt'):
                        return parse(value).time()
                    else:
                        return value
                elif get_dateformat(
                    datestring=value,
                    checkonly=True
                ):
                    if dt in ('datetime', 'dt'):
                        return str_to_date(
                            datestring=value
                        )
                    elif dt in ('DateTime', 'DT'):
                        return str_to_DT(
                            datestring=value
                        )
                    elif dt == 'pendulum':
                        if fmt:
                            p_dt = pendulum.from_format(value, fmt)
                        else:
                            p_dt = pendulum.parse(value)
                
                        if p_dt.tzinfo == 'UTC' and timezone == 'local':
                            return p_dt.in_tz(pendulum.local_timezone())
                        elif timezone:
                            return p_dt.in_tz(timezone)
                        return p_dt
                    else:
                        return convert_datetime(
                            date=value,
                            convert_to=dt
                        )

            except Exception:
                # in case it's a subset of datetime_chars but not a date or datetime or time
                pass

            try:
                return int(value)
            except (ValueError, TypeError):
                pass

            if set(value).issubset(comma_float_chars):
                value = value.replace(',', '.')

            try:
                return float(value)
            except (ValueError, TypeError):
                pass

            if (
                not convert_to_unicode
                and isinstance(value, str)
            ):  # portentionally restore bytes
                value = original_value

        return value
