# -*- coding: utf-8 -*-

import re
from bs4 import Tag
from helper import get_heading_level, get_heading_text, get_html_tree_from_url, parse_translation_table_russian, remove_parenthesis


tested_url = [
    "https://ru.wiktionary.org/wiki/blood",
    "https://ru.wiktionary.org/wiki/flower",
    "https://ru.wiktionary.org/wiki/house",
    "https://ru.wiktionary.org/wiki/speak",
    "https://ru.wiktionary.org/wiki/%D0%B4%D0%BE%D0%BC",
    "https://ru.wiktionary.org/wiki/говорить"]
    
edition = "ru"

COMMA_SEMI_PERIOD = re.compile('[,;.]')

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
    
    #iterate through the childen of the table of contents to find translations              
    for element in toc.children:
        if isinstance(element, Tag):  # it could be a Tag or a NavigableString
            level = get_heading_level(element.name)
            
            # in the Russian edition, h1s always contain the language
            if level == 1: 
                page_state['headword_lang'] = get_heading_text(element)
                #print(page_state['headword_lang'])
                page_state['translation_region'] = False
            #elif level == 2: # if this exists, it contains the headword + other junk
                #first_headline = element.find(class_='mw-headline')
                #first_word = first_headline.text.split(' ')[0] # grabs the headword
                #page_state['headword'] = first_word
                #print(page_state['headword'])
                #page_state['translation_region'] = False
            elif level == 3: # headword + part of speech, or just part of speech follow later
                first_headline = element.find(class_='mw-headline')
                if first_headline.text == u'Морфологические и синтаксические свойства':
                    #if not page_state['headword_lang'] == u'Русский':
                    page_state['pos_region'] = True
                elif first_headline.text == u'Перевод':
                    page_state['translation_region'] = True
                else:
                    page_state['translation_region'] = False
            elif level == 4: # might be a translation list (or synonyms / antonymes list)
                if get_heading_text(element) == u'Значение':
                    if not page_state['headword_lang'] == u'Русский':
                        page_state['translation_region'] = True
                else:
                    page_state['translation_region'] = False
            elif element.name == 'p' and page_state['pos_region']:
                bold_word = element.b
                if not bold_word: # this is a headword
                    #page_state['headword'] = bold_word.get_text()
                    #print(page_state['headword'])
                    # this is a part of speech tag
                    page_state['part_of_speech'] = element.get_text().split(',')[0]
                    #print(page_state['part_of_speech'])
                    page_state['pos_region'] = False
            elif element.name == 'p' and page_state['translation_region']:
                translation = element.get_text()
                yield (edition, page_state['headword'], page_state['headword_lang'], translation.strip(),
                       u'Русский', 'ru', page_state['part_of_speech'])
            elif element.name == 'ol' and page_state['translation_region']:
                for li in element.find_all('li'):
                    if not li.get_text() == '':
                        text = li.get_text().split(u'◆')[0]
                        text = remove_parenthesis(text)
                        text = re.split(COMMA_SEMI_PERIOD, text)
                        for translations in text:
                            #print(translations)
                            yield (edition, page_state['headword'], page_state['headword_lang'], translations.strip(),
                                   u'Русский', 'ru', page_state['part_of_speech'])
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
