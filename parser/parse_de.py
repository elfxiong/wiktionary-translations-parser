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
    ]

    def __init__(self):
        super(DeParser, self).__init__()
        self.edition = 'de'

    def generate_translation_tuples(self, soup):
        toc = soup.find('div', id='mw-content-text')

        page_state = {'headword': None,
                      'headword_lang': None,
                      'part_of_speech': None,
                      'translation_region': False}
        for element in toc.children:
            if isinstance(element, Tag):
                level = self.get_heading_level(element.name)
                # print(element)
                # print(page_state['translation_region'], element.name)
                if level == 2:
                    s = self.get_heading_text(element)
                    # format: "headword (language)"
                    page_state['headword'] = s.split('(')[0].strip()
                    page_state['headword_lang'] = s[s.find("(") + 1:s.find(")")]
                    page_state['translation_region'] = False
                elif level == 3:
                    page_state['part_of_speech'] = self.get_heading_text(element).split(',')[0].strip()
                    page_state['translation_region'] = False
                elif element.name == "h4":
                    first_headline = element.find(class_="mw-headline")
                    if first_headline.text.strip() == u"Übersetzungen":  # this translation header
                        # this is an translation table
                        page_state['translation_region'] = True
                    else:
                        page_state['translation_region'] = False
                elif 'class' not in element.attrs:
                    page_state['translation_region'] = False
                elif page_state['translation_region']:
                    # print()
                    # print()
                    # print()
                    # print(element)
                    # table = element.find_next_sibling(class_="columns")
                    for translation, lang, lang_code in self.parse_translation_table(element):
                        # remove ` n`, ` m` or ` f` at the end of the word
                        translation = re.sub(r'( n)|( m)|( f)$', '', translation)
                        yield (
                            self.edition, page_state['headword'], page_state['headword_lang'], translation, lang,
                            lang_code, page_state['part_of_speech'])


def main():
    parser = DeParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))
            pass


if __name__ == '__main__':
    main()
