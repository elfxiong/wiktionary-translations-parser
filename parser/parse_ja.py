from bs4 import Tag
from helper import get_heading_level, get_heading_text, get_html_tree, parse_translation_table

tested_url = [
    "https://ja.wiktionary.org/wiki/%E3%81%AA%E3%81%84",
    "https://ja.wiktionary.org/wiki/%E9%81%BA%E4%BC%9D%E5%AD%90"
]


def generate_translation_tuples(soup):
    """
    A generator of translation tuples
    :param soup: BeautifulSoup object
    :return: tuple of the form (headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
    """

    # START non-edition-specific
    # this is the table of content which is present in each edition
    toc = soup.find('div', id='toc')
    # print(toc.get_text())
    page_state = {'headword': None,
                  'headword_lang': None,
                  'part_of_speech': None}
    for element in toc.next_siblings:
        if isinstance(element, Tag):  # it could be a Tag or a NavigableString
            level = get_heading_level(element.name)
            # END non-edition-specific
            if level == 2:  # it is a header tag
                page_state['headword_lang'] = get_heading_text(element)
            elif level == 3:
                page_state['part_of_speech'] = get_heading_text(element)
            elif element.name == "p":  # is a paragraph tag
                bold_word = element.b
                if bold_word:
                    page_state['headword'] = bold_word.get_text()
                    # print("headword: ", bold_word.get_text().strip())
            elif element.name == "table":
                if "translations" in element['class']:
                    # this is an translation table
                    for translation, lang, lang_code in parse_translation_table(element):
                        yield (page_state['headword'], page_state['headword_lang'], translation, lang, lang_code,
                               page_state['part_of_speech'])


def main():
    for url in tested_url:
        soup = get_html_tree(url)
        for tup in generate_translation_tuples(soup):
            print(",".join(tup))


if __name__ == '__main__':
    main()
