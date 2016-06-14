from parser.parse_ja import generate_translation_tuples as ja_parser
from parser.parse_vi import generate_translation_tuples as vi_parser
from parser.parse_tr import generate_translation_tuples as tr_parser
from parser.parse_fr import generate_translation_tuples as fr_parser

import sys
import argparse
import parser.lang_code_conversion as languages
from parser.helper import infer_edition_from_url, get_html_tree_from_string, get_html_tree_from_url

if sys.version_info[0:3] >= (3, 0, 0):  # python 3 (tested)
    from zim.zimpy_p3 import ZimFile
else:  # python 2 (not tested)
    from zim.zimpy_p2 import ZimFile

tested_url = [
    "https://vi.wiktionary.org/wiki/kh%C3%B4ng#Ti.E1.BA.BFng_Vi.E1.BB.87t",
    "https://vi.wiktionary.org/wiki/c%C3%A1m_%C6%A1n#Ti.E1.BA.BFng_Vi.E1.BB.87t",
    "https://ja.wiktionary.org/wiki/%E3%81%AA%E3%81%84",
    "https://ja.wiktionary.org/wiki/%E9%81%BA%E4%BC%9D%E5%AD%90",
    "https://tr.wiktionary.org/wiki/ev",
    "https://tr.wiktionary.org/wiki/abartmak",
    "https://fr.wiktionary.org/wiki/amour",
    "https://fr.wiktionary.org/wiki/ouvrir",
]

parsers = {'ja': ja_parser, 'vi': vi_parser, 'tr': tr_parser, 'fr': fr_parser}


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
    file.list_articles_by_url()
    edition_lang_code = file.metadata()['language'].decode('utf-8')
    edition_wikt_code = edition or languages.get_wikt_code_from_iso639_3(edition_lang_code)
    print(edition_wikt_code)
    if edition_wikt_code not in parsers:
        print("We don't have a parser for {}/{} language yet.".format(edition_lang_code, edition_wikt_code))
        return
    parser = parsers[edition_wikt_code]
    page_generator = read_zim_file(file)

    for page in page_generator:
        soup = get_html_tree_from_string(page)
        for tup in parser(soup):
            print(",".join(tup))


def test_html():
    for url in tested_url:
        edition = infer_edition_from_url(url)
        soup = get_html_tree_from_url(url)
        for tup in parsers[edition](soup):
            print(",".join(tup))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zim', '-z', help='use zim file instead of html')
    parser.add_argument('--edition', '-e', help='explicitly specify the language edition')

    args = parser.parse_args()
    if args.zim:
        test_zim(args.zim, args.edition)
    else:
        test_html()


if __name__ == '__main__':
    main()