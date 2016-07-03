"""
The common methods in different editions
"""
import string

import re
import requests
from bs4 import BeautifulSoup, Tag

html_parser = 'html.parser'
try:
    import lxml

    html_parser = 'lxml'
except ImportError:
    pass

HEADING_TAG = re.compile(r'^h(?P<level>[1-6])$', re.I)
COMMA_OR_SEMICOLON = re.compile('[,;]')
PARENTHESIS_WITH_TEXT = re.compile(r'\([^()]*\)')  # no nesting


def infer_edition_from_url(url):
    # print(url)
    result = re.match(r'.*//(?P<edition>\w{2,3})\..+', url)
    return result.group('edition')


def get_heading_level(tag):
    """If the tag is a heading tag, return its level (1 through 6).
    Otherwise, return `None`."""
    heading_match = HEADING_TAG.match(tag)
    if heading_match:
        return int(heading_match.group('level'))
    return None


def get_html_tree_from_url(url):
    html = requests.get(url)
    # print(html.content)
    soup = BeautifulSoup(html.content, html_parser)
    return soup


def get_html_tree_from_string(html):
    return BeautifulSoup(html, html_parser)


def remove_parenthesis2(string):
    """Remove parentheses and text within them.
    For nested parentheses, only the innermost one is removed.
    """
    return re.sub(PARENTHESIS_WITH_TEXT, '', string=string)


def remove_parenthesis(string):
    """Remove parentheses and text within them.
    For nested parentheses, removes the whole thing.
    """
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in string:
        if i == '[':
            skip1c += 1
        elif i == '(':
            skip2c += 1
        elif i == ']' and skip1c > 0:
            skip1c -= 1
        elif i == ')' and skip2c > 0:
            skip2c -= 1
        elif skip1c == 0 and skip2c == 0:
            ret += i
    return ret


def remove_all_punctuation(line):
    punc = str.maketrans('', '', string.punctuation)
    return line.translate(punc).replace('→', '').strip()


def remove_comma_period(line):
    return re.sub('[,.]', '', line)
