"""
The common methods in different editions
"""
import re
import requests
from bs4 import BeautifulSoup, Tag

HEADING_TAG = re.compile(r'^h(?P<level>[1-6])$', re.I)
COMMA_OR_SEMICOLON = re.compile('[,;]')
PARENTHESIS_WITH_TEXT = re.compile(r'\([^()]*\)')  # no nesting


def get_edition_from_url(url):
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


def get_html_tree_from_url(url):
    html = requests.get(url)
    # print(html.content)
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup


def get_html_tree_from_string(html):
    return BeautifulSoup(html, 'html.parser')


def parse_translation_table(table):
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
            
def parse_translation_table_subscript(table):
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

        # language name is before ":"
        lang_name = text[0]

        # language code is in super script
        lang_code = li.find("sub")
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
    


def parse_french_table(table):
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

        # language name is before ":"
        lang_name = text[0]

        # language code is in super script
        lang_code = li.find(class_="trad-existe")
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
            yield (translation, lang_name.strip(), lang_code)


def remove_parenthesis(string):
    """Remove parentheses and text within them.
    For nested parentheses, only the innermost one is removed.
    """
    return re.sub(PARENTHESIS_WITH_TEXT, '', string=string)


def remove_parenthesis2(string):
    """Remove parentheses and text within them.
    For nested parentheses, removes the whole thing.
    """
    ret = ''
    skip_c = 0
    for c in string:
        if c == '(':
            skip_c += 1
        elif c == ')' and skip_c > 0:
            skip_c -= 1
        elif skip_c == 0:
            ret += c
    return ret
