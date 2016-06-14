# -*- coding: utf-8 -*-

from bs4 import Tag
from helper import get_heading_level, get_heading_text, get_html_tree_from_url, parse_translation_table_subscript, remove_parenthesis


tested_url = [
    "https://ru.wiktionary.org/wiki/house",
    "https://ru.wiktionary.org/wiki/speak",
    "https://ru.wiktionary.org/wiki/%D0%B4%D0%BE%D0%BC"]
edition = "ru"


def generate_translation_tuples(soup):
    """
    A generator of translation tuples
    :param soup: BeautifulSoup object
    :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
    """

    # START non-edition-specific
    # this is the table of content which is present in most editions
    toc = soup.find('div', id='mw-content-text')
    #print(toc.get_text())
    page_state = {'headword': None,
                  'headword_lang': None,
                  'part_of_speech': None,
                  'pos_region': False, # pos_region is specific to Russian
                  'translation_region': False}
    for element in toc.children:
        if isinstance(element, Tag):  # it could be a Tag or a NavigableString
            level = get_heading_level(element.name)
            # END non-edition-specific
            if level == 1:  # in the Russian edition this always contains the language
                page_state['headword_lang'] = get_heading_text(element)
                print(page_state['headword_lang'])
                page_state['translation_region'] = False
            elif level == 2: # if this exists, it contains the headword + other junk
                first_headline = element.find(class_='mw-headline')
                first_word = first_headline.text.split(' ')[0] # grabs the headword
                page_state['headword'] = first_word
                #print(page_state['headword'])
                page_state['translation_region'] = False
            elif level == 3: # headword + part of speech, or just part of speech follow later
                first_headline = element.find(class_='mw-headline')
                if first_headline.text == u'Морфологические и синтаксические свойства':
                    if not page_state['headword_lang'] == u'Русский':
                        page_state['pos_region'] = True
            elif level == 4: # might be a translation list (or synonyms / antonymes list)
                if get_heading_text(element) == u'Значение':
                    page_state['translation_region'] = True
                elif get_heading_text(element) == u'Перевод':
                    page_state['translation_region'] = True
            elif element.name == 'p' and page_state['pos_region']:
                bold_word = element.b
                if bold_word: # this is a headword
                    page_state['headword'] = bold_word.get_text()
                    #print(page_state['headword'])
                else: # this is a part of speech tag
                    page_state['part_of_speech'] = element.get_text()
                    print(page_state['part_of_speech'])
                    page_state['pos_region'] = False
            elif element.name == 'ol' and page_state['translation_region']:
                for li in element.find_all('li'):
                    text = li.get_text().split(u'◆')[0]
                    text = remove_parenthesis(text).split(',')
                    for translations in text:
                        yield (edition, page_state['headword'], page_state['headword_lang'], translations, 'Русский', 'ru',
                               page_state['part_of_speech'])
            elif element.name == 'table' and page_state['translation_region']:
                for translation, lang, lang_code in parse_translation_table_subscript(element):
                    yield (edition, page_state['headword'], page_state['headword_lang'], translations, lang, lang_code,
                           page_state['part_of_speech'])
            else:
                page_state['translation_region'] = False

def main():
    for url in tested_url:
        soup = get_html_tree_from_url(url)
        for tup in generate_translation_tuples(soup):
            continue
            print(",".join(tup))


if __name__ == '__main__':
    main()
