import re

from bs4 import BeautifulSoup, Tag
import requests

tested_url = ["https://ja.wiktionary.org/wiki/%E3%81%AA%E3%81%84",
              "https://ja.wiktionary.org/wiki/%E9%81%BA%E4%BC%9D%E5%AD%90"
              ]

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


# def get_translation_table(soup):
#     # spans = soup.find_all('span', string="翻訳", class_="mw-headline")
#     # for span in spans:
#     #     table = span.find_next('table')
#     #     print(table)
#     tables = soup.find_all('table', class_='translations')
#     for table in tables:
#         for li in table.find_all('li'):
#             translation = li.find('a').get_text()
#             translation_lang = li.get_text().split(':')[0]
#             print(translation, translation_lang, sep=',')


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


def generate_translation_tuples(soup):
    """
    A generator of translation tuples
    :param soup: BeautifulSoup object
    :return: tuple of the form (headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
    """

    # START non-edition-specific
    # this is the table of content which is present in each edition
    toc = soup.find('div', id='toc')
    # print(toc.get_text())
    page_state = {'headword': None,
                  'headword_lang': None,
                  'part_of_speech': None}
    for element in toc.next_siblings:
        if isinstance(element, Tag):  # it could be a Tag or a NavigableString
            level = get_heading_level(element.name)
            # END non-edition-specific
            if level == 2:  # it is a header tag
                page_state['headword_lang'] = get_heading_text(element)
            elif level == 3:
                page_state['part_of_speech'] = get_heading_text(element)
            elif element.name == "p":  # is a paragraph tag
                bold_word = element.b
                if bold_word:
                    page_state['headword'] = bold_word.get_text()
                    print(bold_word.get_text().strip())
            elif element.name == "table":
                if "translations" in element['class']:
                    # this is an translation table
                    for translation, lang, lang_code in parse_translation_table(element):
                        yield (page_state['headword'], page_state['headword_lang'], translation, lang, lang_code,
                               page_state['part_of_speech'])


def main():
    for url in tested_url:
        soup = get_html_tree(url)
        for tup in generate_translation_tuples(soup):
            print(",".join(tup))


if __name__ == '__main__':
    main()
