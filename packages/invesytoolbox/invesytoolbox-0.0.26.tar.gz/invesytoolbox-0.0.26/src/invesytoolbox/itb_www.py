# -*- coding: utf-8 -*-
"""
www_tools
=========
"""
from typing import Union, List, Dict
import urllib.parse

zope_data_types = {
    'boolean',
    'int',
    'long',
    'float',
    'string',
    'text',
    'list',
    'tuple',
    'tokens',
    'lines',
    ':ignore_empty'
}


def change_query_string(
    *,
    params: dict,
    url: str = None,
    query_string: str = None,
    delete_remaining: bool = False,
    returning: str = 'auto'
) -> str:
    """
    Change arguments in a query string

    There are no positional arguments, because it must be clear
    if an url or a query string is provided

    :param returning: values: url, query_string or auto
    :param delete_remaining: only keep arguments specified in params
    """
    if returning == 'auto':
        if url:
            returning = 'url'
        elif query_string:
            returning = 'query_string'

    if url:
        url_parts = urllib.parse.urlparse(url)
        query = dict(urllib.parse.parse_qsl(url_parts.query))
    elif query_string:
        if not url and returning == 'url':
            raise Exception('an url is needed to return an url (only query string provided)')
        query = dict(urllib.parse.parse_qsl(query_string))
    else:
        raise TypeError('change_query_string needs an "url" or "query_string" argument!')

    if delete_remaining:
        query = params
    else:
        query.update(params)

    new_query_string = urllib.parse.urlencode(query)
    if '%3A' in new_query_string:
        for typ in zope_data_types:
            new_query_string = new_query_string.replace(f'%3A{typ}', f':{typ}')

    if returning == 'query_string':
        return new_query_string

    if returning == 'url':
        new_url = url_parts._replace(query=new_query_string).geturl()
        return new_url
