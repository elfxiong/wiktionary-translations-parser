# -*- coding: utf-8 -*-

from bs4 import Tag
from parser.general import GeneralParser
from .helper import get_html_tree_from_url


class ViParser(GeneralParser):
    def __init__(self):
        super(ViParser, self).__init__()
        self.edition = 'vi'
        self.tested_url = [
            "https://vi.wiktionary.org/wiki/kh%C3%B4ng#Ti.E1.BA.BFng_Vi.E1.BB.87t",
            "https://vi.wiktionary.org/wiki/c%C3%A1m_%C6%A1n#Ti.E1.BA.BFng_Vi.E1.BB.87t"
        ]

    def generate_translation_tuples(self, soup):
        # START non-edition-specific
        # this is the table of content which is present in each edition
        toc = soup.find('div', id='mw-content-text')
        # print(toc.get_text())
        page_state = {'headword': None,
                      'headword_lang': None,
                      'part_of_speech': None,
                      'translation_region': False}
        for element in toc.children:
            if isinstance(element, Tag):  # it could be a Tag or a NavigableString
                level = self.get_heading_level(element.name)
                # END non-edition-specific
                if level == 2:  # it is a header tag
                    page_state['headword_lang'] = self.get_heading_text(element)
                    page_state['translation_region'] = False
                elif level == 3:
                    page_state['part_of_speech'] = self.get_heading_text(element)
                    page_state['translation_region'] = False
                elif element.name == "p":  # is a paragraph tag
                    bold_word = element.b
                    if bold_word:
                        page_state['headword'] = bold_word.get_text()
                        # print("headword: ", bold_word.get_text().strip())
                    page_state['translation_region'] = False
                elif element.name == "h4":
                    first_headline = element.find(class_="mw-headline")
                    if first_headline.text.strip() == u"Dịch":  # this translation header
                        # this is an translation table
                        page_state['translation_region'] = True
                    else:
                        page_state['translation_region'] = False
                elif page_state['translation_region']:
                    # table = element.find_next_sibling(class_="columns")
                    for translation, lang, lang_code in self.parse_translation_table(element):
                        yield (
                            self.edition, page_state['headword'], page_state['headword_lang'], translation, lang,
                            lang_code,
                            page_state['part_of_speech'])
                else:
                    page_state['translation_region'] = False


def main():
    parser = ViParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
