# -*- coding: utf-8 -*-
import re

from bs4 import Tag
from parser.general import GeneralParser
from .helper import get_heading_level, get_heading_text, get_html_tree_from_url, remove_parenthesis, remove_comma_period

COMMA_SEMI_PERIOD = re.compile('[,;.]')
COMMA_OR_SEMICOLON = re.compile('[,;]')

class RuParser(GeneralParser):
    def __init__(self):
        super(RuParser, self).__init__()
        self.edition = 'ru'
    
    tested_url = [
        "https://ru.wiktionary.org/wiki/-ациj"#,
       # "https://ru.wiktionary.org/wiki/blood",
        #"https://ru.wiktionary.org/wiki/flower",
        #"https://ru.wiktionary.org/wiki/house",
        #"https://ru.wiktionary.org/wiki/speak",
        #"https://ru.wiktionary.org/wiki/%D0%B4%D0%BE%D0%BC",
        #"https://ru.wiktionary.org/wiki/говорить"
    ]
        
    # parse through a translation table in the Russian edition of Wiktionary
    def parse_translation_table_russian(self, table):
    
        for li in table.find_all('li'):
            if not isinstance(li, Tag):
                continue
            text = li.get_text().split(':')

            # language name is before ":"
            lang_name = text[0]

            lang_code = ''
            if li.find("sub"):
                lang_code = li.find("sub").get_text()
                
            # remove the lang code from the lang name
            lang_name = lang_name[:-len(lang_code)]

            if len(text) > 1:
                t = remove_parenthesis(text[1])
            else:
                t = remove_parenthesis(text[0])
            
            trans_list = re.split(COMMA_OR_SEMICOLON, t)

            for trans in trans_list:
                translation = trans.split('(')[0].strip()
                if not translation == '':
                    yield (translation, lang_name, lang_code)

    # parse through an ordered list in the Russian edition of wiktionary
    def parse_ordered_list_russian2(self, olist):
        for li in olist.find_all('li'):
            for href in li.find_all('a'):
                if href.has_attr('href') and href.has_attr('title'):
                    if not href['title'] == 'Викисловарь:Условные сокращения' and not href['title'] == 'ВС:ЦИТ':
                        translation = href['title']
                        yield translation
                    

    # parse through an ordered list in the Russian edition of wiktionary                
    def parse_ordered_list_russian(self, olist):
        for li in olist.find_all('li'):
            if not li.get_text() == '':
                # format the text (specific to RU)
                text = li.get_text().split(u'◆')[0]
                text = remove_parenthesis(text)
                text = re.split(COMMA_SEMI_PERIOD, text)
                for translations in text:
                    yield translations

    # grab and format the part of speech
    def get_pos_russian(self, target):
        text = target.get_text().split(',')[0]
        text = text.split(u'—')
        if len(text) > 1:
            text = text[1].strip()
        else:
            text = text[0].strip()
        return remove_comma_period(text)

    # parse through an unordered list in the Russian edition of wiktionary for part of speech
    def parse_unordered_list_russian(self, ulist):
        for li in ulist.find_all('li'):
            if not li.get_text() == '':
                # format the text (specific to RU)
                text = li.get_text().split(u'—')
                if len(text) > 1:
                    text = text[1].strip()
                else:
                    text = text[0].strip()
                return remove_comma_period(text)

    def generate_translation_tuples(self, soup):
        """
        A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
        """

        
        # Find the headword of the page
        title = soup.find('title')
        if title:
            title = title.text
        else:
            title = ''
        
        # Find the table of contents
        toc = soup.find('div', id='mw-content-text')
        
        # Variable to keep track of important information
        page_state = {'headword': title,
                      'headword_lang': '',
                      'part_of_speech': '',
                      'pronunciation': '',
                      'pos_region': False, # pos_region is specific to Russian
                      'translation_region': False,
                      'pro_region': False}
        
        # iterate through the childen of the table of contents to find translations              
        for element in toc.children:
            if isinstance(element, Tag):
                level = get_heading_level(element.name)
                
                # in the Russian edition, h1s always contain the language
                if level == 1:
                    page_state['headword_lang'] = get_heading_text(element).strip()
                    page_state['translation_region'] = False
                    page_state['pos_region'] = True 

                # Grab the part of speech, always contained in a level 3
                # sometimes the part of speech is preceded by headword
                elif level == 3 or level == 4:
                    text = element.get_text()
                    text = remove_parenthesis(text).strip()
                    
                    if text == u'Морфологические и синтаксические свойства':
                        page_state['pos_region'] = True
                    elif text == u'Перевод':
                        page_state['translation_region'] = True
                        page_state['pos_region'] = False
                    elif text == u'Произношение':
                        page_state['translation_region'] = False
                        page_state['pro_region'] = True
                        page_state['pos_region'] = False
                    elif text == u'Значение':
                        if not page_state['headword_lang'] == u'Русский':
                            page_state['translation_region'] = True
                            page_state['pos_region'] = False
                        else:
                            page_state['translation_region'] = False
                            page_state['pos_region'] = False
                    else:
                        page_state['translation_region'] = False
                        page_state['pos_region'] = False
                        
                # grab the part of speech
                elif element.name == 'p' and page_state['pos_region']:
                    bold_word = element.b
                    if not bold_word: # if the word is not bold, it's the pos
                        page_state['part_of_speech'] = self.get_pos_russian(element)
                        page_state['pos_region'] = False

                # parse through an unordered list to grab part of speech
                elif element.name == 'ul' and page_state['pos_region']:
                    page_state['part_of_speech'] = self.parse_unordered_list_russian(element)
                    page_state['pos_region'] = False
                        
                # parse through a paragraph to grab translations
                elif element.name == 'p' and page_state['translation_region']:
                    translation = element.get_text()
                    yield (self.edition, page_state['headword'], page_state['headword_lang'], translation.strip(),
                           u'Русский', 'ru', page_state['part_of_speech'])
                           
                # parse through an ordered list to grab translations
                elif element.name == 'ol' and page_state['translation_region']:
                    for translation in self.parse_ordered_list_russian(element):
                        yield (self.edition, page_state['headword'], page_state['headword_lang'], translation.strip(),
                               u'Русский', 'ru', page_state['part_of_speech'])
                                       
                # parse through a table to grab translations
                elif element.name == 'table' and page_state['translation_region']:
                    for translation, lang, lang_code in self.parse_translation_table_russian(element):
                        yield (self.edition, page_state['headword'], page_state['headword_lang'], 
                               translation.strip(), lang, lang_code, page_state['part_of_speech'])
                else:
                    page_state['translation_region'] = False

        #yield('', '', '', '', '','', '')

        
def main():
    
    parser = RuParser()
    text_file = open("data/html_ru.txt", "r")
    url_list = text_file.read().split('\n')
    for url in url_list:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            if not ''.join(str(el) for el in tup) == '':
               print(','.join(str(el) for el in tup))
'''
def main():
    parser = RuParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))

'''
if __name__ == '__main__':
    main()
