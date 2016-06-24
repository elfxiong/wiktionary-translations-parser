# wiktionary-translations-parser

For some editions of Wiktionary, extract translation pairs on each page.

## Input

[ZIM](https://en.wikipedia.org/wiki/ZIM_%28file_format%29) is a file format that stores wiki content for offline usage.

- Wiktionary dumps in `.zim` format can be obtained from [kiwix](https://download.kiwix.org/zim/wiktionary/).

The input to this program can be either a `.zim` containing all pages of a Wiktionary edition, or a list of urls. See [usage](#usage) for more detail.

## Output

Each line consists of these fields:

- `edition`: the edition of Wiktionary the translation pair is from. It is a 2-3 letter code used in the Wiktionary url.
- `headword`: the word that is being translated.
- `head_lang`: the language of the `headword`. It might be different from the language of the edition.
- `translation`: the translation of the `headword`.
- `trans_lang`: the language the `headword` is translated into.
- `trans_lang_code`: the language code of `trans_lang`. This is the edition code used by Wiktionary, and it is [not from a single ISO standard](https://en.wiktionary.org/wiki/Wiktionary:Languages#Language_codes).
- `pos`: the part of speech of the `headword` in `head_lang`.
- `pronunciation`: the IPA representation of the `headword`; reflects how the word would be spoken in the `head_lang`

The output is in CSV format with these eight columns.

## Dependencies

- `beautifulsoup4`: used for parsing html.
- `requests`: used to make http calls and fetch `.html` from the Internet. Required if using Internet as data source.
- `pycountry` and `iso-639`: used for conversion between language codes. Required if you do not specify an Wiktionary edition code.
- `repoze.lru`: LRU cache which significantly improve performance for `.zim`. Recommended if using `.zim` as data source.

Install in a `virtualenv` as appropriate.
To install all dependencies (you don't have to):
```
$ pip install -r requirements.txt
```

To install one by one, use `pip install [PACKAGE NAME]`.

## Usage

```
usage: parser.py [-h] (--url_zim URL_ZIM | --url_list URL_LIST | --zim ZIM)
                 [--edition EDITION]

optional arguments:
  -h, --help            show this help message and exit
  --url_zim URL_ZIM, -uz URL_ZIM
                        use a zim file as the source of urls and get html from
                        the Internet
  --url_list URL_LIST, -ul URL_LIST
                        use a file containing a list of urls and get html from
                        the Internet
  --zim ZIM, -z ZIM     use the zim file as input instead of html
  --edition EDITION, -e EDITION
                        explicitly specify the language edition, for either
                        html or zim
```

- Support for using `.zim` file has only been tested for `Python 3.5`. It is probably not working for `Python 2` at this moment.
- `parser.py` should be able to automatically figure out the Wiktionary edition and choose the correct parser based on the url or the metadata in `.zim`. If it doens't use the parser you expect, please use `-e` to explicitly specify the edition.

### Use ZIM file as data source

A '.zim` file contains all pages in a Wiktionary edition.

To run `parser.py` with `.zim` as input:
```
$ python parser.py -z [ZIM FILE]
```

### Use Internet as data source

Instead of using a `.zim` file, you can also provide a list of urls to specify the pages to extract. The parser will fetch html from the urls to use as data source.

If you already have a file with a list of urls:
```
$ python parser.py -ul [FILE]
```
- The file should contain one url on each line.
- All urls should come from the same Wiktionary edition.

If you want to use the urls from a `.zim` file, which contains all the urls from a Wiktionary edition:
```
$ python parser.py -uz [ZIM FILE]
```

### To run the `main()` of a particular parser or `extract.py`

```
$ python -m parser.parse_[EDITION]
```
or
```
$ python -m zim.extract
```
This is telling python to run the `main()` in a file in the module.

- Notice there is no `.py` extension.

## Progress

- Tested with `.zim` file: `ja`, `de`
- Tested with some representative `.html` pages: `az` `fr` `ru` `tr` `uz` `vi`
- Started: `pl`

## Todo

- Write parsers for two or three editions.
	- Run parsers on zim files (entire foreign editions of Wiktionary)
- Generalize them and create a skeleton for writing other parsers.
  - make it so that we need minimal changes in order to parse another edition
- Generate parsers for editions of interest.
- Modify current scripts to include pronunciation extraction from foreign editions of Wiktionary.
- Use translation scripts as base for derivation-table-parsing scripts.
