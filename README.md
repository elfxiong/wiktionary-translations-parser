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

The output is a `.csv` with these seven columns.

## Dependencies

Use `pip install` to install. Install in a `virtualenv` as appropriate.

- `beautifulsoup4`: used for parsing html.
- `requests`: used to make http calls and fetch `.html` from the Intenet. Will eventually be removed as we will be dealing with locally stored files.

## Common

The list of common things in different editions are listed in [common.md](common.md).

## Todo

- Write parsers for two or three editions.
- Generalize them and create a skeleton for writing other parsers.

  - make it so that we need minimal changes in order to parse another edition

- Generate parsers for editions of interest.
