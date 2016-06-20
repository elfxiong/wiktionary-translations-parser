"""Extract translation tuples from Wiktionary pages."""


import json
import logging
import re

from lxml import etree, html

from ..html import classes, textify, heading_level, mw_headline
from ..zim import ZimFile


def parse_translation_table(table):
    """Extract translation tuples from *table*, which is an lxml
    ElementTree object representing an HTML table."""
    gloss = table.get('data-gloss', '')
    logging.debug('Entering translation table with gloss "%s"', gloss)
    translations = []
    table_state = {
        'gloss': gloss,
        'qualifier': None,
        'source': 'translations'
    }
    for list_item in table.iter('li'):
        table_state['qualifier'] = None
        for span in list_item.iter('span'):
            element_classes = classes(span)
            lang = span.get('lang', '')
            if lang:
                translation = {
                    'translation': textify(span),
                    'translation_lang': lang,
                    'gender': None,
                    'transliteration': None
                }
                translation.update(table_state)
                translations.append(translation)
            elif 'qualifier-content' in element_classes:
                qualifier = textify(span)
                logging.debug('Entering qualifier "%s"',
                              qualifier.encode('utf-8'))
                table_state['qualifier'] = qualifier
            elif 'gender' in element_classes:
                # Genders are listed after the translation.
                gender = textify(span)
                if not translations:
                    logging.debug(
                        'Saw stray gender "%s"',
                        gender.encode('utf-8'))
                    continue
                logging.debug(
                    'Adding gender "%s" to translation "%s"',
                    gender.encode('utf-8'),
                    translations[-1]['translation'].encode('utf-8'))
                translations[-1]['gender'] = gender
            elif 'tr' in element_classes:
                # So are transliterations.
                transliteration = textify(span)
                if not translations:
                    logging.debug(
                        'Saw stray transliteration "%s"',
                        transliteration.encode('utf-8'))
                    continue
                logging.debug(
                    'Adding transliteration "%s" to translation "%s"',
                    transliteration.encode('utf-8'),
                    translations[-1]['translation'].encode('utf-8'))
                translations[-1]['transliteration'] = transliteration
    return translations


def parse_definition_list(ol):
    """Extract translation tuples from *ol*, which is an lxml
    ElementTree object representing an ordered list, by looking for
    items containing a single link, excluding parentheticals and example
    sentences, and extracting the text of that link."""
    logging.debug('Entering definition list')
    list_state = {
        'gloss': None,
        'qualifier': None,
        'source': 'definitions'
    }
    for list_item in ol.iterchildren('li'):
        list_state['qualifier'] = None
        links = {}
        link_index = 0
        for element in list_item.iterchildren():
            if 'ib-content' in classes(element):
                list_state['qualifier'] = textify(element)
            elif element.tag == 'a':
                # Only add this as a link if we don't already have one;
                # otherwise, change the existing link to None because
                # it's ambiguous.
                if link_index in links:
                    links[link_index] = None
                else:
                    links[link_index] = element
            # Look through the element's tail for a comma or semicolon,
            # separating different phrasings of the same definition.
            if element.tail and (',' in element.tail or ';' in element.tail):
                link_index += 1
        for link in links.itervalues():
            if link is None:
                continue
            translation = {
                'translation': textify(link),
                'translation_lang': 'en',  # definitions in English
                'gender': None,
                'transliteration': None
            }
            translation.update(list_state)
            yield translation


def parse_document(doc):
    """Extract translation tuples from the Wiktionary page contained in
    the lxml HTML document object *doc*."""
    # We can only find out what headings are active by proceeding
    # linearly through the page, hence the iteration below the root.
    headings = [[]] * 6
    page_state = {'headword': None,
                  'headword_lang': None,
                  'headings': []}
    for element in doc.iter(tag=etree.Element):
        level = heading_level(element)
        element_classes = classes(element)
        if level:
            index = level - 1
            headings[index].append(mw_headline(element))
            for i in xrange(index + 1, 6):
                headings[i] = []
            logging.debug('Entering headings %r', headings)
            # We use "tuple" here to get an immutable copy.
            page_state['headings'] = filter(None, [tuple(h) for h in headings])
            if level <= 3:  # XXX: enwiktionary-specific
                page_state['headword'] = None
                page_state['headword_lang'] = None
        elif 'headword' in element_classes:
            page_state['headword'] = textify(element)
            page_state['headword_lang'] = element.get('lang')
        elif 'translations' in element_classes:
            for translation in parse_translation_table(element):
                translation.update(page_state)
                yield translation
        elif element.tag == 'ol':
            for translation in parse_definition_list(element):
                translation.update(page_state)
                yield translation


def main():
    """Command line entry point."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__)
    parser.add_argument(
        'article_file', metavar='ARTICLE', type=argparse.FileType(),
        help='path to Wiktionary article file')
    parser.add_argument(
        '-z', '--zim-file', action='store_true',
        help='treat the article file as a ZIM archive, instead of HTML '
             'source')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='enable debugging output')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO)

    if args.zim_file:
        article_tuples = ZimFile(args.article_file).article_tuples()
    else:
        article_tuples = [(None, None, args.article_file.read())]

    for article_tuple in article_tuples:
        context = {'edition': article_tuple[0], 'pagename': article_tuple[1]}
        doc = html.fromstring(article_tuple[2])
        for translation in parse_document(doc):
            translation.update(context)
            print json.dumps(translation)


if __name__ == '__main__':
    main()
