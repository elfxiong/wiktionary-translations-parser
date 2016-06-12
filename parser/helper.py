"""
The common methods in different editions
"""
import re
import requests
from bs4 import BeautifulSoup, Tag

HEADING_TAG = re.compile(r'^h(?P<level>[1-6])$', re.I)
COMMA_OR_SEMICOLON = re.compile('[,;]')


def get_heading_level(tag):
    """If the tag is a heading tag, return its level (1 through 6).
    Otherwise, return `None`."""
    heading_match = HEADING_TAG.match(tag)
    if heading_match:
        return int(heading_match.group('level'))
    return None


def get_heading_text(tag):
    """
    Extract the text of the heading, discarding "[edit]".
    May need to be modified to work for more complex headings.
    :param tag: a Tag object. It should be one of the <h?> tags.
    :return: the actual/clean text in the tag
    """
    text = tag.get_text()
    text = text.split('[')[0]
    return text


def get_html_tree(url):
    html = requests.get(url)
    # print(html.content)
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup


def parse_translation_table(table):
    """
    Parse the table to get translations and the languages.
    Hopefully this function will work for all editions.
    :param table: a Tag object of <table>.
    :return: (translation, language_name, language_code)
    """
    for li in table.find_all('li'):
        if not isinstance(li, Tag):
            continue
        text = li.get_text().split(':')

        # language name is before ":"
        lang_name = text[0]

        # language code is in super script
        lang_code = li.find("sup")
        if lang_code:
            lang_code = lang_code.text.strip()[1:-1]
        else:
            lang_code = ""

        # each "trans" is: translation <sup>(lang_code)</sup> (transliteration)
        # lang_code and transliteration may not exist
        trans_list = re.split(COMMA_OR_SEMICOLON, text[1])
        for trans in trans_list:
            translation = trans.split('(')[0].strip()
            yield (translation, lang_name, lang_code)
