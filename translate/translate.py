"""
This is the translation module.

The translation module supplies one function, translate().  For example,

>>> translate("Hello", "auto", "fr")
'Bonjour'
"""


def translate(text: str, source_lang: str, target_lang: str) -> str | None:
    """Return a machine translation for text.

    >>> translate("¿Cómo estás?", "auto", "en-gb")
    'How are you?'

    :param text: Text to be translated
    :param target_lang: Output language
    :return: Translated text in output language
    """
    import os
    import logging
    deepl_env_name = "DEEPL_API_KEY"

    try:
        if deepl_env_name in os.environ:
            return deepl_translate(text, target_lang, os.environ[deepl_env_name])
    except Exception as e:
        logging.debug("DeepL raised an error: ", e)

    try:
        return webgoogle_translate(text, source_lang=source_lang, target_lang=target_lang)
    except Exception as e:
        logging.debug(f"Google Translator (web) raised an error: ({e})")

    return None


def get_available_languages():
    import deep_translator as d
    return d.GoogleTranslator().get_supported_languages(as_dict=True)


def deepl_translate(text: str, target_lang: str, auth_key: str) -> str:
    """"Return a machine translation from DeepL for text.

    :param text: Text to be translated
    :param target_lang: Output language
    :param auth_key: DeepL API key
    :return: Translated text in output language
    """
    import deepl
    translator = deepl.Translator(auth_key)

    result = translator.translate_text(text, target_lang=target_lang)
    return result.text


def webgoogle_translate(text: str, source_lang: str, target_lang: str) -> str:
    """"Return a machine translation from Google Translator using webpage for text.

    >>> webgoogle_translate("Alice has a cat.", "auto", "pl")
    'Alicja ma kota.'

    :param text: Text to be translated
    :param source_lang: Input language
    :param target_lang: Output language
    :return: Translated text in output language
    """
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import NotValidLength
    import textwrap

    target_lang = target_lang.lower()
    if target_lang == "en-gb" or target_lang == "en-us":
        target_lang = "en"
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    max_text_length = 5000
    texts = []
    if len(text) > max_text_length:
        texts = text.split("\\n")
    else:
        texts.append(text)
    translations = []
    try:
        translations = translator.translate_batch(texts)
    except NotValidLength as e:
        raise ValueError(f"Text too long (max 5000, text {len(t)})")
    return "\\n".join(translations)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
