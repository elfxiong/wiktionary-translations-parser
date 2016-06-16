# -*- coding: utf-8 -*-

import re
from bs4 import Tag
from helper import get_heading_level, get_heading_text, get_html_tree_from_url, remove_parenthesis


tested_url = [
    "https://ru.wiktionary.org/wiki/blood",
    "https://ru.wiktionary.org/wiki/flower",
    "https://ru.wiktionary.org/wiki/house",
    "https://ru.wiktionary.org/wiki/speak",
    "https://ru.wiktionary.org/wiki/%D0%B4%D0%BE%D0%BC",
    "https://ru.wiktionary.org/wiki/говорить"]
    
edition = "ru"

COMMA_SEMI_PERIOD = re.compile('[,;.]')
COMMA_OR_SEMICOLON = re.compile('[,;]')

# parse through a translation table in the Russian edition of Wiktionary
def parse_translation_table_russian(table):
    
    for li in table.find_all('li'):
        if not isinstance(li, Tag):
            continue
        text = li.get_text().split(':')

        # language name is before ":"
        lang_name = text[0]
    
        if li.find("sub"):
            lang_code = li.find("sub").get_text()
        else:
            lang_code = ''
            
        lang_name = lang_name[:-len(lang_code)]

        t = remove_parenthesis(text[1])
        trans_list = re.split(COMMA_OR_SEMICOLON, t)
        # each "trans" is: translation <sup>(lang_code)</sup> (transliteration)
        # lang_code and transliteration may not exist
        for trans in trans_list:
            translation = trans.split('(')[0].strip()
            if not translation == '':
                yield (translation, lang_name, lang_code)

# parse through an ordered list in the Russian edition of wiktionary                
def parse_ordered_list_russian(olist):
    
    for li in olist.find_all('li'):
        if not li.get_text() == '':
            # format the text (specific to RU)
            text = li.get_text().split(u'◆')[0]
            text = remove_parenthesis(text)
            text = re.split(COMMA_SEMI_PERIOD, text)
            for translations in text:
                yield translations

def generate_translation_tuples(soup):
    """
    A generator of translation tuples
    :param soup: BeautifulSoup object
    :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
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
                  'pos_region': False, # pos_region is specific to Russian
                  'translation_region': False}
    
    # iterate through the childen of the table of contents to find translations              
    for element in toc.children:
        if isinstance(element, Tag):
            level = get_heading_level(element.name)
            
            # in the Russian edition, h1s always contain the language
            if level == 1: 
                page_state['headword_lang'] = get_heading_text(element)
                page_state['translation_region'] = False

            # Grab the part of speech, always contained in a level 3
            # sometimes the part of speech is preceded by headword
            elif level == 3:
                first_headline = element.find(class_='mw-headline')
                if first_headline.text == u'Морфологические и синтаксические свойства':
                    page_state['pos_region'] = True
                elif first_headline.text == u'Перевод':
                    page_state['translation_region'] = True
                else:
                    page_state['translation_region'] = False
                    
            # A level 4 might contain a translation list / paragraph
            elif level == 4:
                if get_heading_text(element) == u'Значение':
                    if not page_state['headword_lang'] == u'Русский':
                        page_state['translation_region'] = True
                else:
                    page_state['translation_region'] = False
                    
            # grab the part of speech
            elif element.name == 'p' and page_state['pos_region']:
                bold_word = element.b
                if not bold_word: # if the word is not bold, it's the pos
                    page_state['part_of_speech'] = element.get_text().split(',')[0]
                    page_state['pos_region'] = False
                    
            # parse through a paragraph to grab translations
            elif element.name == 'p' and page_state['translation_region']:
                translation = element.get_text()
                yield (edition, page_state['headword'], page_state['headword_lang'], translation.strip(),
                       u'Русский', 'ru', page_state['part_of_speech'])
                       
            # parse through an ordered list to grab translations
            elif element.name == 'ol' and page_state['translation_region']:
                for translation in parse_ordered_list_russian(element):
                    yield (edition, page_state['headword'], page_state['headword_lang'], translation.strip(),
                           u'Русский', 'ru', page_state['part_of_speech'])
                                   
            # parse through a table to grab translations
            elif element.name == 'table' and page_state['translation_region']:
                for translation, lang, lang_code in parse_translation_table_russian(element):
                    yield (edition, page_state['headword'], page_state['headword_lang'], 
                           translation.strip(), lang, lang_code, page_state['part_of_speech'])
            else:
                page_state['translation_region'] = False

def main():
    for url in tested_url:
        soup = get_html_tree_from_url(url)
        for tup in generate_translation_tuples(soup):
            print(','.join(tup))


if __name__ == '__main__':
    main()
