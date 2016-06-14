from pycountry import languages
from iso639 import languages as iso
import logging


def get_language_from_wiktionary_code(code):
    lang = None
    try:
        lang = languages.get(iso639_1_code=code)
    except KeyError:
        pass
    if not lang:
        try:
            lang = languages.get(iso639_3_code=code)
        except KeyError:
            pass
    if not lang:
        try:
            lang = languages.get(iso639_2T_code=code)
        except KeyError:
            pass
    if not lang:
        code = code.split('-')[0]
        try:
            lang = iso.get(part5=code)
            setattr(lang, 'iso639_3_code', lang.part3)
        except KeyError:
            # print("no lang for: ", code)
            pass
    return lang


def get_iso639_3_from_wikt(code):
    lang = get_language_from_wiktionary_code(code)
    if lang:
        return lang.iso639_3_code
    else:
        return "UNKNOWN(" + code + ")"


def get_wikt_code_from_iso639_3(code):
    lang = languages.get(iso639_3_code=code)
    if lang.iso639_1_code:
        return lang.iso639_1_code
    if lang.iso639_3_code:
        return lang.iso639_3_code
    logging.debug('Do not know the Wikt code for {}'.format(code))
