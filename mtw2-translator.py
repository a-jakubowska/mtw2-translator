import translate as t
import reference_translation as rt
from pathlib import Path
import traceback


def translate_file(filename, newfilename, source_lang, target_lang, ref_translator):
    import re
    file = open(filename, encoding='utf-16')
    new = open(newfilename, 'w', encoding='utf-16')
    keys_translated = 0
    keys_referenced = 0
    keys_intact = 0
    for line in file:
        match = re.fullmatch(r"({.*})(.*)", line.rstrip())
        if match and len(match.groups()) == 2:
            key = match.group(1)
            value = match.group(2)
            try:
                # Translate string
                text = ref_translator.get_ref(value)
                if text is None:
                    text = t.translate(value, source_lang, target_lang)
                    if text is None:
                        text = value
                        keys_intact = keys_intact + 1
                    else:
                        keys_translated = keys_translated + 1
                else:
                    keys_referenced = keys_referenced + 1
                # Write to file
                new.write(key + text + '\n')
            except Exception as e:
                raise RuntimeError(f"Cannot translate {key}{value} to {text}") from e
        else:
            new.write(line)

    return keys_referenced, keys_translated, keys_intact


def translate_dir(dirname: str, source_lang: str, target_lang: str, ref_translator: rt.RefTranslator) -> None:
    # Create Path object from string
    dirpath = Path(dirname)

    # Create directory to store translations
    translated_dir = dirpath.parent / (dirpath.name + "-" + target_lang)
    if not translated_dir.exists():
        translated_dir.mkdir()

    # Translate file-by-file
    keys_referenced = 0
    keys_translated = 0
    keys_intact = 0
    for orig_file in dirpath.glob('*.txt'):
        translated_file = translated_dir / orig_file.name
        print(
            f"Translating {orig_file} to {translated_file} ({target_lang}). Please be patient, it can take few minutes.")
        ref, trans, intact = translate_file(orig_file, translated_file, source_lang, target_lang, ref_translator)
        print(f"{orig_file} translated ({ref} from reference translations, {trans} translated, {intact} left intact)")
        keys_referenced = keys_referenced + ref
        keys_translated = keys_translated + trans
        keys_intact = keys_intact + intact

    # Summary
    print(f"Directory {dirpath} translated with:")
    keys_total = keys_referenced + keys_translated + keys_intact
    print("\t*", f"{keys_total} strings translated")
    ref_percent = (keys_referenced / keys_total) * 100
    print("\t*", f"{keys_referenced} strings taken from reference translations ({ref_percent:.0f}%)")
    trans_percent = (keys_translated / keys_total) * 100
    print("\t*", f"{keys_translated} strings machine translated ({trans_percent:.0f}%)")
    intact_percent = (keys_intact / keys_total) * 100
    print("\t*", f"{keys_intact} strings left intact ({intact_percent:.0f}%)")

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
    print("Downloading available languages...")
    langdict = t.get_available_languages()
    print("Avaliable languages:")
    for full_lang_name, abbr in langdict.items():
        print(f"{full_lang_name} ({abbr})")

    def input_lang_raw(prompt, default=None):
        if default is not None:
            prompt = prompt[:-1] + f" (default: {default})" + prompt[-1]
        while True:
            lang = input(prompt)
            if len(lang) == 0 and default is not None:
                return default
            if lang not in langdict.keys() and lang not in langdict.values():
                print("Wrong language. Try again.")
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
            ref_translator.add_ref(reference, translation)
        if ref_translation_needed == 'n':
            break
        first_question = False

    return ref_translator


if __name__ == "__main__":
    try:
        source_lang, target_lang = input_lang()
        moddir = input_dir('Enter a mod directory:')
        ref_translator = input_reference_translations()

        # translation
        translate_dir(moddir, source_lang, target_lang, ref_translator)

        print(f"Files in {moddir} replaced with {target_lang} translation!")
    except Exception:
        print("Something went wrong, details:")
        traceback.print_exc()

    print()
    input("Press any key to proceed...")
