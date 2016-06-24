import argparse
import sys
import logging

import os
from parser.helper import infer_edition_from_url, get_html_tree_from_string, get_html_tree_from_url
import importlib

if sys.version_info[0:3] >= (3, 0, 0):  # python 3 (tested)
    from zim.zimpy_p3 import ZimFile
else:  # python 2 (not tested)
    from zim.zimpy_p2 import ZimFile


def setup_logger():
    if not os.path.exists('log/'):
        os.mkdir('log/')
    LOG_FILENAME = "log/parser.log"
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


# key: Wiktionary edition code
# value: parser class (not parser instance)
parsers = {}

headers = ['edition', 'headword', 'head_lang', 'translation', 'trans_lang', 'trans_lang_code', 'pos', 'pronunciation']


# dynamically loading all modules
def import_all_parsers():
    parser_list = ['ja', 'vi', 'tr', 'fr', 'ru', 'uz', 'de', 'az']
    for parser_name in parser_list:
        module_to_import = '.parse_' + parser_name
        module = importlib.import_module(module_to_import, package='parser')
        parsers[parser_name] = getattr(module, parser_name.capitalize() + "Parser")
        # tested_url.extend(module.tested_url)


def get_parser(edition):
    if edition not in parsers:
        module_to_import = '.parse_' + edition
        try:
            module = importlib.import_module(module_to_import, package='parser')
            parsers[edition] = getattr(module, edition.capitalize() + "Parser")
        except Exception as e:
            print(e)
            return None
    # instantiate the class
    return parsers[edition]()


def read_zim_file(file):
    # print(file.metadata())
    # we only need main articles. They are in namespace 'A'.
    namespace = b'A'
    for article in file.articles():
        if article['namespace'] != namespace:
            continue
        body = file.get_article_by_index(
            article['index'], follow_redirect=False)[0]
        if not body:
            continue
        else:
            yield (body.decode('utf-8'))


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

    print(','.join(headers))
    # get the parser class
    parser = get_parser(edition_wikt_code)
    if parser is None:
        print("We don't have a parser for {}/{} language yet.".format(edition_lang_code, edition_wikt_code))
        return

    # instantiate the parser
    page_generator = read_zim_file(file)
    for page in page_generator:
        soup = get_html_tree_from_string(page)
        for tup in parser.generate_translation_tuples(soup):
            try:
                print(','.join(tup))
            except TypeError as e:
                logging.debug(e)
                logging.debug(tup)
                logging.debug(soup)
                continue


def test_html(filename, edition=None):
    with open(filename) as file:
        url_list = file.readlines()

    if edition is None:
        edition = infer_edition_from_url(url_list[0])
    parser = get_parser(edition)

    print(','.join(headers))
    for url in url_list:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


def use_url_zim(filename, edition=None):
    file = ZimFile(filename=filename)
    if not edition:
        print("Edition not provided. Trying to figure out the edition...")
        import parser.lang_code_conversion as languages
        edition_lang_code = file.metadata()['language'].decode('utf-8')
        edition = languages.get_wikt_code_from_iso639_3(edition_lang_code)

    print("Edition: {}".format(edition))
    parser = get_parser(edition)

    print("Start to uncompress zim file to get the url list...")
    from zim.extract import yield_url
    url_list = ["https://{}.wiktionary.org/wiki/{}".format(edition, url[:-5]) for url in yield_url(file=file)]
    print("Got {} urls from the zim file".format(len(url_list)))

    print(','.join(headers))
    for url in url_list:
        soup = get_html_tree_from_url(url)
        for tup in parser.generate_translation_tuples(soup):
            print(','.join(tup))


def main():
    setup_logger()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url_zim', '-uz', help='use a zim file as the source of urls and get html from the Internet')
    group.add_argument('--url_list', '-ul', help='use a file containing a list of urls and get html from the Internet')
    group.add_argument('--zim', '-z', help='use the zim file as input instead of html')
    parser.add_argument('--edition', '-e', help='explicitly specify the language edition, for either html or zim')

    args = parser.parse_args()
    if args.zim:
        test_zim(args.zim, args.edition)
    elif args.url_list:
        test_html(args.url_list, args.edition)
    elif args.url_zim:
        use_url_zim(args.url_zim, args.edition)


if __name__ == '__main__':
    main()
