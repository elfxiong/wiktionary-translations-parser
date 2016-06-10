# wiktionary-translations-parser

For some editions of Wiktionary, extract translation pairs on each page.

## Output

Each translation tuple consists of these fields:

- `headword` the word that is being translated
- `headword_lang` the language of the headword
- `translation` the translation of the headword
- `translation_lang` the language the headword is translated into
- `part_of_speech` the part of speech of the headword in its language

## Todo

- Write parsers for two or three editions
- Generalize them and create a skeleton for writing other parsers

  - make it so that we need minimal changes in order to parse another edition

- Generate parsers for editions of interest
