"""Dump the html pages out of .zim; print all html pages.
"""
import argparse

import os
from zim.zimpy_p3 import ZimFile


def yield_url(filename):
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
            yield article['url']


def print_url(filename):
    for url in yield_url(filename):
        print(url)


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
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', '-m', help="'f' for printing .html files; 'u' for printing urls as a list",
                        required=True)
    parser.add_argument('--input', '-i', help="The input zim file", required=True)
    parser.add_argument('--output', '-o', help="The directory of the output html", required=False)
    args = parser.parse_args()

    if args.mode == 'f':
        if not args.output:
            print("Please specify the output directory with -'o' flag.")
        else:
            print_html(filename=args.input, path=args.output)
    elif args.mode == 'u':
        print_url(filename=args.input)
    else:
        print("Please specify a mode.")


if __name__ == '__main__':
    main()
