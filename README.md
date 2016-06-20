# wiktionary-translations-parser

For some editions of Wiktionary, extract translation pairs on each page.

## Input

Eventually the input would a `.zim` file that contains all pages of an edition.

- Wiktionary dumps in `.zim` format can be obtained from [kiwix](https://download.kiwix.org/zim/wiktionary/).

For now, we are dealing with individual `.html` pages from the editions we're working on. For example [gène in French edition](https://fr.wiktionary.org/wiki/g%C3%A8ne).

## Output

Each translation tuple consists of these fields:

- `edition`: the edition of Wiktionary the translation pair is from. It is a 2-3 letter code used in the Wiktionary url.
- `headword`: the word that is being translated.
- `head_lang`: the language of the `headword`. It might be different from the language of the edition.
- `translation`: the translation of the `headword`.
- `trans_lang`: the language the `headword` is translated into.
- `trans_lang_code`: the language code of `tranlation_lang`. This is the edition code used by Wiktionary, and it is [not from a single ISO standard](https://en.wiktionary.org/wiki/Wiktionary:Languages#Language_codes).
- `pos`: the part of speech of the `headword` in `head_lang`.
- `pronunciation`: the IPA representation of the `headword`; reflects how the word would be spoken in the `head_lang` 

The output is a `.csv` with these seven columns.

## Dependencies

- `beautifulsoup4`: used for parsing html.
- `requests`: used to make http calls and fetch `.html` from the Intenet. Will eventually be removed as we will be dealing with locally stored files.
- `pycountry` and `iso-639`: used for conversion between language codes.

Install in a `virtualenv` as appropriate.
To install all dependencies:

    $ pip install -r requirements.txt

To install one by one, use `pip install [PACKAGE NAME]`. 

## Usage
 
To run with a `.zim` file:

    $ python parser.py -z [zimfile]

- Support for using `.zim` file has only been tested for `Python 3.5`. It is probably not working for `Python 2` at this moment.

Detailed usage:

    usage: parser.py [-h] [--zim ZIM] [--edition EDITION]
    optional arguments:
      -h, --help            show this help message and exit
      --zim ZIM, -z ZIM     use zim file instead of html
      --edition EDITION, -e EDITION
                            explicitly specify the language edition



## Common

The list of common things in different editions are listed in [common.md](common.md).

## Todo

- Write parsers for two or three editions.
	- Run parsers on zim files (entire foreign editions of Wiktionary)
- Generalize them and create a skeleton for writing other parsers.
  - make it so that we need minimal changes in order to parse another edition
- Generate parsers for editions of interest.
- Modify current scripts to include pronunciation extraction from foreign editions of Wiktionary.
- Use translation scripts as base for derivation-table-parsing scripts.
