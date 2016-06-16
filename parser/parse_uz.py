# -*- coding: utf-8 -*-

from bs4 import Tag
from parser.general import GeneralParser
from parser.helper import get_html_tree_from_url

class TrParser(GeneralParser):
    def __init__(self):
        super(TrParser, self).__init__()
        self.edition = 'uz'
        self.tested_url = [
            "https://uz.wiktionary.org/wiki/uy",
            "https://uz.wiktionary.org/wiki/yugurmoq",
            "https://uz.wiktionary.org/wiki/avtomobil",
        ]

    def generate_translation_tuples(soup):
        """
        A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
        """

        # START non-edition-specific
        # this is the table of content which is present in each edition
        toc = soup.find('div', id='mw-content-text')
        # print(toc.get_text())
        translation_table = False
        page_state = {'headword': None,
                  'headword_lang': None,
                  'part_of_speech': None}

        page_state['headword'] = soup.find('h1', id='firstHeading', class='firstHeading')
        
        for element in toc.children:
            if isinstance(element, Tag):  # it could be a Tag or a NavigableString
                level = get_heading_level(element.name)
                # END non-edition-specific
                # Find the headword language
                if element['id'] == 'toc':
                    page_state['headword_lang'] = element.b.strip()
                # Find Part of Speech: Not sure if this works. The only way i've been able to see a correlation between
                # All pages for part of speech is by it being a h2 and the POS in a font tag. Since my sample test is so small
                # I don't know if it's working properly

                if level == 2:
                    if element.font != None:
                        page_state['part_of_speech'] = element.font.text
                        
                
                # Find the translation table
                elif element.contents.text == 'Tillarda' or element.contents.text == 'Tillar':
                    translation_table = True
                
                elif translation_table == True:

                    for translation, lang, lang_code in self.parse_translation_table(element):
                        
                        yield (
                            self.edition, page_state['headword'], page_state['headword_lang'], translation, lang,
                            lang_code, page_state['part_of_speech'])
                translation_table = False


def main():
    parser = TrParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
