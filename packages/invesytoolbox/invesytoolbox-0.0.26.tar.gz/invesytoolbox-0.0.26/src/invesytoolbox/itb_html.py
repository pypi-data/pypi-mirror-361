# -*- coding: utf-8 -*-
"""
=======================
html_tools
=======================
"""
from bs4 import BeautifulSoup


def prettify_html(
    html: str
) -> str:
    """
    Prettify html (from bs4/BeautifulSoup)

    .. note:: This function is needed for Zope Python Scripts
        because even if bs4 can be imported, prettify throws
        an Unauthorized error in Restricted Python
    """

    return BeautifulSoup(html, "html.parser").prettify()


def change_h_tags(
    html: str,
    change: int,
    returning: str = 'str'
):
    """
    change all the H-tags in a HTML,
    increase or decrease by a certain number
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    h_numbers = {}

    if change > 0:
        for i in range(1, 7):
            h_numbers[i] = min(i + change, 6)
    elif change < 0:
        for i in range(1, 7):
            h_numbers[i] = max(i + change, 1)
    else:  # 0
        for i in range(1, 7):
            h_numbers[i] = i

    tags = {}
    for h_original in h_numbers:  # keys
        tag_name = f'h{h_original}'
        tags[tag_name] = soup.find_all(f'h{h_original}')

    for tag_name, tag_list in tags.items():
        for tag in tag_list:
            tag.name = f'h{h_numbers.get(int(tag_name[-1]))}'

    if returning == 'soup':
        return soup
    elif returning == 'pretty':
        return soup.prettify()
    else:
        return str(soup)
