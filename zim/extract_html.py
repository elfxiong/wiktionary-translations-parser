"""Dump the html pages out of .zim"""
import os
from zim.zimpy_p3 import ZimFile


def read_zim_file(file):
    # print(file.metadata())
    # we only need main articles. They are in namespace 'A'.
    namespace = b'A'
    for article in file.articles():
        # print(article)
        if article['namespace'] != namespace:
            continue
        body = file.get_article_by_index(
            article['index'], follow_redirect=False)[0]
        if not body:
            continue
        else:
            url = article['url']
            print("https://fr.wiktionary.org/wiki/", url[:-5], sep='')
            yield (body.decode('utf-8'), url)


def test_zim(filename, edition=None):
    file = ZimFile(filename=filename)
    # file.list_articles_by_url()
    edition_lang_code = file.metadata()['language'].decode('utf-8')
    # print(edition_lang_code)

    if edition:
        edition_wikt_code = edition
        # print(edition_wikt_code)
    else:
        import parser.lang_code_conversion as languages
        edition_wikt_code = languages.get_wikt_code_from_iso639_3(edition_lang_code)
        # print(edition_wikt_code)

    # instantiate the parser
    page_generator = read_zim_file(file)
    path = 'data/' + edition_wikt_code
    if not os.path.exists(path):
        os.mkdir(path)
    # for page, url in page_generator:
        # with open(os.path.join(path, url), 'w+') as file:
            # print(page, file=file)


def main():
    filename = "wiktionary_fr_all_nopic_2016-05.zim"
    file = ZimFile(filename=filename)
    for read in read_zim_file(file):
        pass


if __name__ == '__main__':
    main()
