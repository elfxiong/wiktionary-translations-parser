"""Dump the html pages out of .zim; OR print all urls.
"""
import argparse

import os
from zim.zimpy_p3 import ZimFile


def yield_url(file):
    namespace = b'A'
    for article in file.articles():
        if article['namespace'] != namespace:
            continue
        body = file.get_article_by_index(
            article['index'], follow_redirect=False)[0]
        if not body:
            continue
        else:
            yield article['url']


def print_url(filename, full=False, edition=None):
    file = ZimFile(filename=filename)

    if not full:
        for url in yield_url(file):
            print(url)
        return

    if not edition:
        import parser.lang_code_conversion as languages
        edition_lang_code = file.metadata()['language'].decode('utf-8')
        # print(edition_lang_code)
        edition = languages.get_wikt_code_from_iso639_3(edition_lang_code)

    for url in yield_url(file):
        print("https://{}.wiktionary.org/wiki/{}".format(edition, url[:-5]))


def print_html(filename, path):
    file = ZimFile(filename=filename)
    namespace = b'A'
    for article in file.articles():
        if article['namespace'] != namespace:
            continue
        body = file.get_article_by_index(
            article['index'], follow_redirect=False)[0]
        if not body:
            continue
        else:
            url = article['url']
            with open(os.path.join(path, url), 'w+') as output_file:
                print(body, file=output_file)


def main():
    parser = argparse.ArgumentParser(description="Print all urls in a ZIM file as a list")
    parser.add_argument('--input', '-i', help="The input zim file", required=True)
    subparsers = parser.add_subparsers(help='commands', dest='command')
    subparsers.required = True

    parser_a = subparsers.add_parser('url', help='Extract all urls from ZIM')
    parser_a.add_argument('--full', '-f', action='store_true', help='Print the full url')
    parser_a.add_argument('--edition', '-e', help='Explicitly specify the edition for forming the url')

    parser_b = subparsers.add_parser('html', help='Extract all html from ZIM')
    parser_b.add_argument('--output', '-o', help='The output directory of the html file', required=True)

    args = parser.parse_args()

    if args.command == 'html':
        print_html(filename=args.input, path=args.output)
    elif args.command == 'url':
        print_url(filename=args.input, full=args.full, edition=args.edition)
    else:
        print("Please specify a command.")


if __name__ == '__main__':
    main()
