import argparse
import sys

from parser.helper import infer_edition_from_url, get_html_tree_from_string, get_html_tree_from_url
import importlib

if sys.version_info[0:3] >= (3, 0, 0):  # python 3 (tested)
    from zim.zimpy_p3 import ZimFile
else:  # python 2 (not tested)
    from zim.zimpy_p2 import ZimFile

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
            print(",".join(tup))


def test_html(edition=None):
    if edition is None:
        import_all_parsers()
        print(','.join(headers))
        urls_lists = [parser.tested_url for parser in parsers.values()]
        test_urls = [url for sub_list in urls_lists for url in sub_list]
        for url in test_urls:
            edition = infer_edition_from_url(url)
            soup = get_html_tree_from_url(url)
            parser = get_parser(edition)
            for tup in parser.generate_translation_tuples(soup):
                print(",".join(tup))
    else:
        parser = get_parser(edition)
        print(','.join(headers))
        for url in parser.tested_url:
            soup = get_html_tree_from_url(url)
            for tup in parser.generate_translation_tuples(soup):
                print(','.join(tup))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zim', '-z', help='use zim file instead of html')
    parser.add_argument('--edition', '-e', help='explicitly specify the language edition, for either html or zim')

    args = parser.parse_args()
    if args.zim:
        test_zim(args.zim, args.edition)
    else:
        test_html(args.edition)


if __name__ == '__main__':
    main()
