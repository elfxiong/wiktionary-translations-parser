from parser.parse_ja import generate_translation_tuples as ja_parser
from parser.parse_vi import generate_translation_tuples as vi_parser
from parser.helper import get_edition_from_url, get_html_tree


tested_url = [
    "https://vi.wiktionary.org/wiki/kh%C3%B4ng#Ti.E1.BA.BFng_Vi.E1.BB.87t",
    "https://vi.wiktionary.org/wiki/c%C3%A1m_%C6%A1n#Ti.E1.BA.BFng_Vi.E1.BB.87t",
    "https://ja.wiktionary.org/wiki/%E3%81%AA%E3%81%84",
    "https://ja.wiktionary.org/wiki/%E9%81%BA%E4%BC%9D%E5%AD%90",
]

parsers = {'ja': ja_parser, 'vi': vi_parser}


def main():
    for url in tested_url:
        edition = get_edition_from_url(url)
        # print(edition)
        soup = get_html_tree(url)
        print(edition)
        for tup in parsers[edition](soup):
            print(",".join(tup))


if __name__ == '__main__':
    main()
