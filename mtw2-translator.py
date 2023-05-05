import translate as t
import reference_translation as rt
from pathlib import Path


def translate_file(filename, newfilename, lang, ref_translator):
    import re
    file = open(filename, encoding='utf-16')
    new = open(newfilename, 'w', encoding='utf-16')
    for line in file:
        match = re.fullmatch(r"({.*})(.*)", line.rstrip())
        if match and len(match.groups()) == 2:
            key = match.group(1)
            value = match.group(2)
            # Translate string
            text = ref_translator.get_ref(value)
            if text is None:
                text = t.translate(value, lang)
            # Write to file
            new.write(key + text + '\n')
        else:
            new.write(line)


def translate_dir(dirname: str, lang: str, ref_translator: rt.RefTranslator) -> None:
    # Create Path object from string
    dirpath = Path(dirname)

    # Create directory to store translations
    translated_dir = dirpath.parent / (dirpath.name + "-" + lang)
    if not translated_dir.exists():
        translated_dir.mkdir()

    # Translate file-by-file
    for orig_file in dirpath.glob('*.txt'):
        translated_file = translated_dir / orig_file.name
        print(f"Translating {orig_file} to {translated_file} ({lang}). Please be patient, it can take few minutes.")
        translate_file(orig_file, translated_file, lang, ref_translator)

    # Set desired paths
    orig_path = dirpath
    backup_path = Path(str(dirpath) + "-backup")

    # rename paths
    print(f"Moving {dirpath.name} to {backup_path.name}")
    dirpath.rename(backup_path)
    print(f"Moving {translated_dir.name} to {orig_path.name}")
    translated_dir.rename(orig_path)


def input_dir(prompt):
    while True:
        path = Path(input(prompt))
        if path.exists():
            if path.is_dir():
                return path
            else:
                print("Path is not a directory! Try again.")
        else:
            print("Path does not exists! Try again.")

def input_lang():
    langdict = t.get_available_languages()
    print("Avaliable languages:")
    for full_lang_name, abbr in langdict.items():
        print(f"{full_lang_name} ({abbr})")

    while True:
        lang = input("Enter target languague:")
        if lang not in langdict.keys() and lang not in langdict.values():
            print("Wrong language. Try again.")
        else:
            return lang

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
            ref_translator.add_ref(reference, translation)
        if ref_translation_needed == 'n':
            break
        first_question = False

    return ref_translator

if __name__ == "__main__":
    lang = input_lang()
    moddir = input_dir('Enter a mod directory:')
    ref_translator = input_reference_translations()

    # translation
    translate_dir(moddir, lang, ref_translator)
