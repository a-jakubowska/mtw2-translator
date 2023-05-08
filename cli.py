import translate as t
import reference_translation as rt

import logging
from pathlib import Path


def input_dir(prompt):
    while True:
        path = Path(input(prompt))
        if path.exists():
            if path.is_dir():
                return path
            else:
                logging.info("Path is not a directory! Try again.")
        else:
            logging.info("Path does not exists! Try again.")


def input_lang():
    logging.info("Downloading available languages...")
    langdict = t.get_available_languages()
    logging.info("Avaliable languages:")
    logging.info("\n".join([f"{full_lang_name} ({abbr})" for full_lang_name, abbr in langdict.items()]))

    def input_lang_raw(prompt, default=None):
        if default is not None:
            prompt = prompt[:-1] + f" (default: {default})" + prompt[-1]
        while True:
            lang = input(prompt)
            if len(lang) == 0 and default is not None:
                return default
            if lang not in langdict.keys() and lang not in langdict.values():
                logging.info("Wrong language. Try again.")
            else:
                return lang

    source = input_lang_raw("Enter source languague:", default="en")
    target = input_lang_raw("Enter target languague:")
    return source, target


def input_reference_translations():
    ref_translator = rt.RefTranslator()

    first_question = True
    another = ""
    while True:
        if not first_question:
            another = "another "
        ref_translation_needed = input(f'Do you want to add {another}reference translation? (y/n):')
        if ref_translation_needed == 'y':
            reference = input_dir('Enter reference mod text directory:')
            translation = input_dir('Enter reference translation directory:')
            logging.info(f"Adding {reference} -> {translation} reference translation")
            ref_translator.add_ref(reference, translation)
        if ref_translation_needed == 'n':
            break
        first_question = False

    return ref_translator
