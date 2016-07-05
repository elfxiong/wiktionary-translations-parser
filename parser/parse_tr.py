# -*- coding: utf-8 -*-

from bs4 import Tag
from parser.general import GeneralParser
from parser.helper import get_html_tree_from_url


class TrParser(GeneralParser):
    tested_url = [
        "https://tr.wiktionary.org/wiki/ev",
        "https://tr.wiktionary.org/wiki/abartmak",
        "https://tr.wiktionary.org/wiki/fobi",
        "https://tr.wiktionary.org/wiki/arap",
    ]

    def __init__(self):
        super(TrParser, self).__init__()
        self.edition = 'tr'

    def generate_translation_tuples(self, soup):
        """
        A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
        """

        # START non-edition-specific
        # this is the table of content which is present in each edition
        toc = soup.find('div', id='mw-content-text')
        # Needed to check if we found headword already
        head = False
        translation_table = False
        # print(toc.get_text())
        page_state = {'headword': None,
                      'headword_lang': None,
                      'part_of_speech': None}
        
        pronounce = ''
        head_word = soup.find('h1', id='titleHeading')
        if head_word is not None:
            page_state['headword'] = head_word.text
            head = True

        for element in toc.children:
            if isinstance(element, Tag):  # it could be a Tag or a NavigableString
                level = self.get_heading_level(element.name)
                # END non-edition-specific
                if level == 2:  # it is a header tag
                    # print (self.get_heading_text(element))
                    page_state['headword_lang'] = self.get_heading_text(element)
                    page_state['headword_lang'] = page_state['headword_lang'].lstrip('\n')
                    pronounce = ''
                elif level == 3:
                    page_state['part_of_speech'] = self.get_heading_text(element)
                elif element.name == "p":  # is a paragraph tag
                    bold_word = element.b
                    if not bold_word:
                        continue
                        # print("headword: ", bold_word.get_text().strip())
                    # Then we found translations
                    if bold_word.text == u"Çeviriler" and head == True:
                        translation_table = True

                    if bold_word.text == u"Türk Dilleri" and head == True:
                        translation_table = True
                #elif element.b is not None and 'Söyleniş' in element.b.text:

                #   temp = element.find_next_sibling

                #        pronounce = temp.text

                elif translation_table:
                    
                    for translation, lang, lang_code in self.parse_translation_table(element):
                        if len(translation.split()) >= 2:
                            translation = translation.split()[1]
                        # NOTE: The translations that start with [1] [#Language] are just being put as the language
                        # even though no translation is actually available. So right now i throw those tuples out completely
                        # If we don't want that, just take out the if statement.

                        translation = translation.strip('[#|]')
                        if page_state['part_of_speech'] is not None:
                            page_state['part_of_speech'] = page_state['part_of_speech'].strip()

                        if page_state['headword_lang'] is not None:
                            page_state['headword_lang'] = page_state['headword_lang'].strip()

                        # Uncomment next lines to skip tuples with blank translation field
                        #if translation is '':
                        #    continue
                        yield (
                            self.edition, page_state['headword'], page_state['headword_lang'], translation, lang,
                            lang_code, page_state['part_of_speech'], pronounce)
                        
                    translation_table = False



def main():
    parser = TrParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))

if __name__ == '__main__':
    main()
