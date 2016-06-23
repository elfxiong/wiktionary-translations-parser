# TODO: make compatible w/ .zim files, find POS for translated words(?)

# -*- coding: utf-8 -*-
import re

from bs4 import Tag
from parser.general import GeneralParser
from parser.helper import get_html_tree_from_url, remove_parenthesis, COMMA_OR_SEMICOLON


class FrParser(GeneralParser):
    tested_url = [
        "https://fr.wiktionary.org/wiki/ouvrir",
        "https://fr.wiktionary.org/wiki/amour",
    ]

    def __init__(self):
        super(FrParser, self).__init__()
        self.edition = 'fr'

    def generate_translation_tuples(self, soup):
        """ A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
        """

        # this is the table of content which is present in each edition
        toc = soup.find('div', id='mw-content-text')
        page_state = {'headword': '',
                      'headword_lang': '',
                      'part_of_speech': '',
                      'pronunciation': ''}
        edition = "fr"
        if not toc:
            return
        for element in toc.children:
            if isinstance(element, Tag):  # it could be a Tag or a NavigableString
                level = self.get_heading_level(element.name)

                if level == 2:  # it is a header tag
                    page_state['headword_lang'] = self.get_heading_text(element)
                elif level == 3:
                    page_state['part_of_speech'] = self.get_heading_text(element)
                elif element.name == "p":  # is a paragraph tag
                    bold_word = element.b
                    if bold_word:
                        page_state['headword'] = bold_word.get_text()
                        # print("headword: ", bold_word.get_text().strip())
                        link = element.a
                        if link:
                            for child in link.findChildren():
                                if child.has_attr('class') and "API" in child.get("class"):
                                    page_state['pronunciation'] = child.get_text()
                elif element.name == "h4":
                    first_headline = element.find(class_="mw-headline")
                    if first_headline and first_headline.text.strip() == "Traductions":  # this translation header
                        # this is a translation table
                        while True:
                            table = element.find_next_sibling()
                            if table.has_attr("class") and "boite" in table.get("class"):
                                for translation, lang, lang_code in self.parse_translation_table(table):
                                    yield (
                                        edition, page_state['headword'], page_state['headword_lang'], translation, lang,
                                        lang_code, page_state['part_of_speech'], page_state['pronunciation'])
                                element = table
                            else:
                                break

    def parse_translation_table(self, table):
        """ Overrides GeneralParser's method.
        :param table: a Tag object. Not necessary a table; can be a div.
        :return: (translation, language_name, language_code)
        """
        for li in table.find_all('li'):
            if not isinstance(li, Tag):
                continue
            text = li.get_text().split(':')
            if len(text) < 2:
                continue

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


def main():
    parser = FrParser()
    text_file = open("data/html_fr.txt", "r")
    url_list = text_file.read().split('\n')
    for url in url_list:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
