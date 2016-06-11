# wiktionary-translations-parser

For some editions of Wiktionary, extract translation pairs on each page.

## Input

Eventually the input would a `.zim` file that contains all pages of an edition.

- Wiktionary dumps in `.zim` format can be obtained from [kiwix](https://download.kiwix.org/zim/wiktionary/).

For now, we are dealing with individual `.html` pages from the editions we're working on. For example [gène in French edition](https://fr.wiktionary.org/wiki/g%C3%A8ne).

## Output

Each translation tuple consists of these fields:

- `headword` the word that is being translated.
- `headword_lang` the language of the headword. It might be different from the language of the edition.
- `translation` the translation of the headword.
- `translation_lang` the language the headword is translated into.
- `part_of_speech` the part of speech of the headword in its language.

The output is a `.csv` with these five columns.

## Common

The list of common things in different editions are listed in [common.md](common.md).

## Todo

- Write parsers for two or three editions.
- Generalize them and create a skeleton for writing other parsers.

  - make it so that we need minimal changes in order to parse another edition

- Generate parsers for editions of interest.
