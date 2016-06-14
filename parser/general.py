"""
The common methods in different editions
"""
import re
import requests
from bs4 import BeautifulSoup, Tag
from .helper import remove_parenthesis, remove_parenthesis2, infer_edition_from_url

HEADING_TAG = re.compile(r'^h(?P<level>[1-6])$', re.I)
COMMA_OR_SEMICOLON = re.compile('[,;]')
PARENTHESIS_WITH_TEXT = re.compile(r'\([^()]*\)')  # no nesting


class GeneralParser:
    def __init__(self):
        self.edition = None

    def get_heading_level(self, tag):
        """If the tag is a heading tag, return its level (1 through 6).
        Otherwise, return `None`."""
        heading_match = HEADING_TAG.match(tag)
        if heading_match:
            return int(heading_match.group('level'))
        return None

    def get_heading_text(self, tag):
        """
        Extract the text of the heading, discarding "[edit]".
        May need to be modified to work for more complex headings.
        :param tag: a Tag object. It should be one of the <h?> tags.
        :return: the actual/clean text in the tag
        """
        text = tag.get_text()
        text = text.split('[')[0]
        return text

    def parse_translation_table(self, table):
        """
        Parse the table to get translations and the languages.
        Hopefully this function will work for all editions.
        :param table: a Tag object. Not necessary a table; can be a div.
        :return: (translation, language_name, language_code)
        """
        for li in table.find_all('li'):
            if not isinstance(li, Tag):
                continue
            text = li.get_text().split(':')

            # TBD: the table is not a translation table
            #  OR the table is a translation table but there are some <li> without colon
            if len(text) < 2:
                continue

            # language name is before ":"
            lang_name = text[0]

            # language code is in super script
            lang_code = li.find("sup")
            if lang_code:
                lang_code = lang_code.text.strip()[1:-1]
            else:
                lang_code = ""

            # There are two functions that removes parentheses. Not sure which one to use.
            t = remove_parenthesis(text[1])
            trans_list = re.split(COMMA_OR_SEMICOLON, t)
            # each "trans" is: translation <sup>(lang_code)</sup> (transliteration)
            # lang_code and transliteration may not exist
            for trans in trans_list:
                translation = trans.split('(')[0].strip()
                yield (translation, lang_name, lang_code)
