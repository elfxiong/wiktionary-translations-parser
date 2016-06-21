# -*- coding: utf-8 -*-

import re

from bs4 import Tag
from parser.general import GeneralParser
from .helper import get_heading_level, get_heading_text, get_html_tree_from_url, remove_parenthesis

COMMA_OR_SEMICOLON = re.compile('[,;]')

class PlParser(GeneralParser):
    def __init__(self):
        super(PlParser, self).__init__()
        self.edition = 'pl'

    tested_url = [
        "https://pl.wiktionary.org/wiki/red",
        "https://pl.wiktionary.org/wiki/house",
        "https://pl.wiktionary.org/wiki/дом",
        "https://pl.wiktionary.org/wiki/mleko",
        "https://pl.wiktionary.org/wiki/czerwony"]

    # parse through an unordered list for translations in Polish edition
    def parse_unordered_list_polish(self, ulist):
    
        for li in ulist.find_all('li'):
            if not isinstance(li, Tag):
                continue
            if not li.get_text() == '':
                text = li.get_text().split(':')
                lang_name = text[0]
                lang_code = ''
                trans_list = re.split(COMMA_OR_SEMICOLON, text[1])
                for trans in trans_list:
                    translation = remove_parenthesis(trans).strip()
                    yield (translation, lang_name, lang_code)
    
    def generate_translation_tuples(self, soup):
        """
        A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (edition, headword, head_lang, translation, 
        trans_lang, trans_lang_code, part_of_speech)
        """
    
        # Find the headword of the page
        title = soup.find('h1', id='firstHeading')
        title = title.text

        # Find the table of contents
        toc = soup.find('div', id='mw-content-text')
    
        # Variable to keep track of important information
        page_state = {'headword': title,
                      'headword_lang': None,
                      'part_of_speech': None,
                      'translation_region': False}

        # iterate through table of contents to find translations              
        for element in toc.children:
            if isinstance(element, Tag):
                level = get_heading_level(element.name)
            
                # Grab the language of the headword
                if level == 2:
                    text = get_heading_text(element)
                    text = text[text.find("(")+1:text.find(")")] # find language within heading
                    if text[:5] == u'język': # remove extra word (most of the time)
                        text = text[6:]
                    page_state['headword_lang'] = text
                    page_state['translation_region'] = False
                
                # check to see if we are about to enter a translations region   
                elif element.name == 'dl' and not page_state['translation_region']:
                    text = element.get_text().strip()
                    if (text == u'znaczenia:' and not page_state['headword_lang'] == u'polski') or text == u'tłumaczenia:':
                        page_state['translation_region'] = True
            
                # we are probably in a translations region, grab translations
                elif element.name == 'dl' and page_state['translation_region']:
                    text = element.get_text().strip()
                    if text[0] == '(': # only consistent thing I found across the edition for encountering translations
                        trans_list = text.split('\n')
                        for trans in trans_list:
                            yield (self.edition, page_state['headword'], page_state['headword_lang'], 
                                   remove_parenthesis(trans).strip(), u'polski', 'pl',
                                   page_state['part_of_speech'])
                    else:
                        page_state['translation_region'] = False
                
                # grab the part of speech, conveniently always in a paragraph tag
                elif element.name == 'p':
                    page_state['part_of_speech'] = element.get_text()
        
                # parse through a list to grab translations
                elif element.name == 'ul':
                    for translation, lang, lang_code in self.parse_unordered_list_polish(element):
                        yield (self.edition, page_state['headword'], page_state['headword_lang'], 
                               translation.strip(), lang, lang_code, page_state['part_of_speech'])
            
                else:
                    page_state['translation_region'] = False

                    
def main():
    parser = PlParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
