from bs4 import Tag
from parser.general import GeneralParser
from parser.helper import get_html_tree_from_url


class JaParser(GeneralParser):
    tested_url = [
        "https://ja.wiktionary.org/wiki/%E3%81%AA%E3%81%84",
        "https://ja.wiktionary.org/wiki/%E9%81%BA%E4%BC%9D%E5%AD%90",
        "https://ja.wiktionary.org/wiki/speak",
    ]

    def __init__(self):
        super(JaParser, self).__init__()
        self.edition = 'ja'

    # override the parent class method
    def generate_translation_tuples(self, soup):
        """
        A generator of translation tuples
        :param soup: BeautifulSoup object
        :return: tuple of the form (edition, headword, head_lang, translation, trans_lang, trans_lang_code, part_of_speech)
        """

        # format the data to lists and yield
        for word_data in self.parse_page(soup):
            for translation_tup in word_data['translations']:
                yield (
                    self.edition, word_data['headword'], word_data['headword_lang'], translation_tup[0],
                    translation_tup[1], translation_tup[2], word_data['part_of_speech'], word_data['pronunciation'])
            else:  # when the translation list is empty
                yield (self.edition, word_data['headword'], word_data['headword_lang'], '',
                       '', '', word_data['part_of_speech'], word_data['pronunciation'])

    def parse_page(self, soup):
        """ Yield for each language section
        """
        # try:
        #     page_heading = soup.find('div', class_='mw-body-content').previous_sibling.text
        # except AttributeError as e:
        #     print(soup)
        page_content = soup.find('div', id='mw-content-text')
        page_heading = None
        element = soup.find('div', class_='mw-body-content') or page_content
        if element is None:
            return
        while not page_heading:
            element = element.previous_sibling
            if isinstance(element, Tag):
                page_heading = element.text

        page_state = {'headword': page_heading,
                      'headword_lang': "",
                      'part_of_speech': "",
                      'pronunciation': "",
                      'translations': []}
        for element in page_content.children:
            if isinstance(element, Tag):
                level = self.get_heading_level(element.name)

                if level == 2:
                    if page_state['headword']:
                        yield page_state
                    page_state['headword_lang'] = self.get_heading_text(element)
                    page_state['part_of_speech'] = ""
                    # page_state['headword'] = page_heading  # default value
                    page_state['pronunciation'] = ""
                    page_state['translations'] = []
                elif level == 3:
                    page_state['part_of_speech'] = self.get_heading_text(element)
                # elif element.name == "p":
                #     bold_word = element.b
                #     if bold_word:
                #         page_state['headword'] = bold_word.get_text()
                elif element.name == 'table' and 'class' in element.attrs and 'translations' in element['class']:
                    page_state['translations'] += list(self.parse_translation_table(element))
                pronunciation = element.find(class_="IPA")
                if pronunciation:
                    page_state['pronunciation'] = pronunciation.text
        yield page_state


def main():
    parser = JaParser()
    for url in parser.tested_url:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))
            # print(tup)


if __name__ == '__main__':
    main()
