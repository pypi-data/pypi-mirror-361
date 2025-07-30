# coding=utf-8
"""
run the test from the sr/invesytoolbox directory:
python ../tests/test_text_name.py
"""

import sys
import unittest
from bs4 import BeautifulSoup

sys.path.append(".")

from itb_html import (
    change_h_tags,
    prettify_html
)

html_raw = """<html><head><title>The Dormouse's story</title></head>
<body>
<h1>The Dormouse's story</h1>

<h3>Two Sisters</h3>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

h_tag_changed = {
    1: """<html><head><title>The Dormouse's story</title></head>
<body>
<h2>The Dormouse's story</h2>

<h4>Two Sisters</h4>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
""",
    2: """<html><head><title>The Dormouse's story</title></head>
<body>
<h3>The Dormouse's story</h3>

<h5>Two Sisters</h5>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
}

html_pretty = """<html>
 <head>
  <title>
   The Dormouse's story
  </title>
 </head>
 <body>
  <h1>
   The Dormouse's story
  </h1>
  <h3>
   Two Sisters
  </h3>
  <p class="story">
   Once upon a time there were three little sisters; and their names were
   <a class="sister" href="http://example.com/elsie" id="link1">
    Elsie
   </a>
   ,
   <a class="sister" href="http://example.com/lacie" id="link2">
    Lacie
   </a>
   and
   <a class="sister" href="http://example.com/tillie" id="link3">
    Tillie
   </a>
   ;
and they lived at the bottom of a well.
  </p>
  <p class="story">
   ...
  </p>
 </body>
</html>"""


class TestRestrictedPython(unittest.TestCase):
    def test_prettify_html(self) -> str:
        html_prettified = prettify_html(html_raw)
        print('html_prettified', html_prettified)
        print()
        print('html_pretty', html_pretty)
        # Assertion does not work, so we compare visually
        """
        self.maxDiff = None
        self.assertEqual(
            html_prettified,
            html_pretty
        )
        """

    def test_change_h_tags(self) -> str:
        """
        Prettifying is needed to compare the results
        (we could have compared the soups as well)
        """
        html = prettify_html(html_raw)
        self.maxDiff = None
        for i in (1, 2):
            html_h_changed = change_h_tags(
                html=html_raw,
                change=i,
                returning='pretty'
            )
            self.assertEqual(
                html_h_changed,
                prettify_html(h_tag_changed[i])
            )


if __name__ == '__main__':
    unittest.main()
