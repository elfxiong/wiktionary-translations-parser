# -*- coding: utf-8 -*-

from bs4 import Tag, BeautifulSoup
from parser.general import GeneralParser
from parser.helper import get_html_tree_from_url, remove_parenthesis
class AzParser(GeneralParser):
    
    tested_url = [

        "https://az.wiktionary.org/wiki/yem%C9%99k",
        "https://az.wiktionary.org/wiki/ev",
        "https://az.wiktionary.org/wiki/qa%C3%A7%C4%B1%C5%9F",
        "https://az.wiktionary.org/wiki/avtomobil",

    ]

    def __init__(self):
        super(AzParser, self).__init__()
        self.edition = 'az'
        

    def generate_translation_tuples(self, soup):
        """
        A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
        """

        # START non-edition-specific
        # this is the table of content which is present in each edition
        toc = soup.find('div', id='mw-content-text')
        
        page_state = {'headword': None,
                  'headword_lang': None,
                  'part_of_speech': ''}


        pronounce = ''

        headword_element = soup.find('h1', id='titleHeading')
        
        if headword_element is not None:

            page_state['headword'] = headword_element.text

        for element in toc.children:
            if isinstance(element, Tag):  # it could be a Tag or a NavigableString
                level = self.get_heading_level(element.name)
                # END non-edition-specific
                # Find the headword language

                if level == 2 and 'id' in element.attrs and element['id'] == 'mwAQ':

                    page_state['headword_lang'] = element.text.replace('dili','').strip()
                    pronounce = ''

                elif level == 3 and 'id' in element.attrs and element['id'] == 'mwAw':
                    
                    page_state['part_of_speech'] = element.text
                
                elif element.name == 'ul':

                    for li in element.find_all('li'):
                        if not isinstance(li, Tag):
                            continue
                        if li.get_text().split(':')[0] == 'Tələffüz':
                            pronounce = li.get_text().split(':')[1].strip()

                elif element.name == 'p':
                    
                    if  '<div class="NavHead" #FFFFE0">' in element.text:

                        for translation, lang, lang_code in self.parse_translation_table(\
                            element.find_next_sibling('div', class_='NavFrame')):

                            if translation == '':
                                continue
                            translation = translation.strip()
                            lang = lang.strip()
                            yield (
                                self.edition, page_state['headword'], page_state['headword_lang'], translation, lang,
                                lang_code, page_state['part_of_speech'], pronounce)
                        

def main():
    parser = AzParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
