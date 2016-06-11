import re

from bs4 import BeautifulSoup, Tag
import requests

HEADING_TAG = re.compile(r'^h(?P<level>[1-6])$', re.I)


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


def get_html_tree():
    html = requests.get("https://ja.wiktionary.org/wiki/%E9%81%BA%E4%BC%9D%E5%AD%90")
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
    for li in table.find_all('li'):
        translation = li.find('a').get_text()
        translation_lang = li.get_text().split(':')[0]
        yield (translation, translation_lang)


def find_languages(soup):
    toc = soup.find('div', id='toc')
    # print(toc.get_text())
    page_state = {'headword': None,
                  'headword_lang': None,
                  'part_of_speech': None}
    for element in toc.next_siblings:
        if isinstance(element, Tag):  # it could be a Tag or a NavigableString
            level = get_heading_level(element.name)
            if level == 2:  # it is a header tag
                page_state['headword_lang'] = element.get_text()
            elif level == 3:
                page_state['part_of_speech'] = element.get_text()
            elif element.name == "p":  # is a paragraph tag
                bold_word = element.b
                if bold_word:
                    page_state['headword'] = bold_word.get_text()
                    print(bold_word.get_text().strip())
            elif element.name == "table":
                if "translations" in element['class']:
                    # this is an translation table
                    for translation, lang in parse_translation_table(element):
                        print(page_state['headword'], page_state['headword_lang'], translation, lang,
                              page_state['part_of_speech'], sep=',')


def main():
    soup = get_html_tree()
    find_languages(soup)
    pass


if __name__ == '__main__':
    main()
