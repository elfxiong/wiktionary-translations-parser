from parser.parse_ja import generate_translation_tuples as ja_parser
from parser.parse_vi import generate_translation_tuples as vi_parser
from parser.parse_tr import generate_translation_tuples as tr_parser

from parser.helper import get_edition_from_url, get_html_tree_from_string, get_html_tree_from_url
import sys
import argparse

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
]

parsers = {'ja': ja_parser, 'vi': vi_parser, 'tr': tr_parser}


def read_zim_file(filename):
    file = ZimFile(filename=filename)
    file.list_articles_by_url()
    print(file.metadata()['description'].decode('utf-8'))
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


def test_zim(filename):
    page_generator = read_zim_file(filename)
    for page in page_generator:
        soup = get_html_tree_from_string(page)
        for tup in ja_parser(soup):
            print(",".join(tup))


def test_html():
    for url in tested_url:
        edition = get_edition_from_url(url)
        soup = get_html_tree_from_url(url)
        for tup in parsers[edition](soup):
            print(",".join(tup))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zim', '-z', help='use zim file instead of html.')

    args = parser.parse_args()
    if args.zim:
        test_zim(args.zim)
    else:
        test_html()


if __name__ == '__main__':
    main()
