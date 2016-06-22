# -*- coding: utf-8 -*-
import re

from bs4 import Tag
from parser.general import GeneralParser
from parser.helper import get_html_tree_from_url


class DeParser(GeneralParser):
    tested_url = [
        "https://de.wiktionary.org/wiki/gene",
        "https://de.wiktionary.org/wiki/play",
        "https://de.wiktionary.org/wiki/nicht",
        "https://de.wiktionary.org/wiki/flamboyant",
    ]

    def __init__(self):
        super(DeParser, self).__init__()
        self.edition = 'de'

    def generate_translation_tuples(self, soup):
        # format the data to lists and yield
        for word_data in self.parse_page(soup):
            if word_data is None:
                continue
            for translation_tup in word_data['translations']:
                yield (
                    self.edition, word_data['headword'], word_data['headword_lang'], translation_tup[0],
                    translation_tup[1], translation_tup[2], word_data['part_of_speech'], word_data['pronunciation'])
            else:  # when the translation list is empty
                yield (self.edition, word_data['headword'], word_data['headword_lang'], '',
                       '', '', word_data['part_of_speech'], word_data['pronunciation'])

    def parse_page(self, soup):

        page_content = soup.find('div', id='mw-content-text')
        page_heading = None
        element = soup.find('div', class_='mw-body-content') or page_content
        while not page_heading:
            if element is None:
                return None
            element = element.previous_sibling
            if isinstance(element, Tag):
                page_heading = element.text

        page_state = {'headword': None,
                      'headword_lang': "",
                      'part_of_speech': "",
                      'pronunciation': "",
                      'translations': []}
        for element in page_content.children:
            if isinstance(element, Tag):
                level = self.get_heading_level(element.name)

                if level == 2:
                    if page_state['headword']:
                        yield page_state
                    s = self.get_heading_text(element)
                    # format: "headword (language)"
                    page_state['headword'] = s.split('(')[0].strip() or page_heading
                    page_state['headword_lang'] = s[s.find("(") + 1:s.find(")")]
                    page_state['translation_region'] = False
                    page_state['part_of_speech'] = ""
                    page_state['translations'] = []
                    page_state['pronunciation'] = ""
                elif level == 3:
                    page_state['part_of_speech'] = self.get_heading_text(element).split(',')[0].strip()
                    page_state['translation_region'] = False
                elif element.name == "h4":
                    first_headline = element.find(class_="mw-headline")
                    if first_headline is None:
                        continue
                    if first_headline.text.strip() == u"Übersetzungen":  # this translation header
                        # this is an translation table
                        page_state['translation_region'] = True
                    else:
                        page_state['translation_region'] = False
                elif 'class' not in element.attrs:
                    page_state['translation_region'] = False
                elif page_state['translation_region']:
                    page_state['translations'] += self.parse_translation_table(element)

                pronunciation = element.find(class_="ipa")
                if pronunciation:
                    page_state['pronunciation'] = pronunciation.text

        if page_state['headword']:
            yield page_state

    def parse_translation_table(self, table):
        lst = list(super(DeParser, self).parse_translation_table(table))
        # remove ` n`, ` m` or ` f` at the end of the word
        return [(re.sub(r'( n)|( m)|( f)$', '', tup[0]), tup[1], tup[2]) for tup in lst]


def main():
    parser = DeParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
