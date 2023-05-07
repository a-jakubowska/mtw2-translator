import translate as t
import reference_translation as rt
from edit_data import edit_data

import re
import sys
import json
import textwrap
import traceback
from pathlib import Path

from tqdm import tqdm


def translate_file(filename, newfilename, source_lang, target_lang, ref_translator):
    file = open(filename, encoding='utf-16')
    new = open(newfilename, 'w', encoding='utf-16')
    keys_translated = 0
    keys_referenced = 0
    keys_intact = 0
    for line in tqdm(file, unit="line", file=sys.stdout):
        match = re.fullmatch(r"({.*})(.*)", line.rstrip())
        if match and len(match.groups()) == 2:
            key = match.group(1)
            value = match.group(2)
            try:
                comment = ""
                # Translate string
                text = ref_translator.get_ref(value)
                if text is None:
                    text = t.translate(value, source_lang, target_lang)
                    if text is None:
                        text = value
                        keys_intact = keys_intact + 1
                    else:
                        comment = f"¬>>>>> AUTO TRANSLATION >>>>> {value}\n"
                        keys_translated = keys_translated + 1
                else:
                    keys_referenced = keys_referenced + 1
                # Sanitize text
                text.replace('\u200c', '')
                # Write to file
                new.write(comment + key + text + '\n')
            except Exception as e:
                raise RuntimeError(f"Cannot translate {key}{value} to {text}") from e
        else:
            new.write(line)

    return keys_referenced, keys_translated, keys_intact


def translate_dir(dirpath: Path, source_lang: str, target_lang: str, ref_translator: rt.RefTranslator) -> None:
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

    return translated_dir


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


def input_num(prompt, max_limit, min_limit=0):
    response = min_limit - 1
    try:
        response = int(input(prompt))
    except:
        pass
    while response > max_limit or response < min_limit:
        try:
            response = int(input(f"please choose number from range [{min_limit}, {max_limit}]: "))
        except:
            pass
    return response


def resolve_duplicates_by_user(ref_translator, reference, translation, duplicates):
    class DuplicatesEnv(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, rt.DuplicateTranslation):
                return {'file': str(obj.file), 'line': obj.line, 'hits': obj.hits, 'text': obj.text}
            return json.JSONEncoder.default(self, obj)

    print()
    print(textwrap.fill("Program will open file editor for you to review duplicates. " +
                        "File will be formatted as JSON (www.json.org) and " +
                        "will be opened by editor associated with .json extension."))
    print()
    print("If you wish to remove reference translation, remove JSON entry.")
    print("To select one translation, remove the others from the list associated with text")
    print()

    new_duplicates = edit_data(duplicates, encoding="utf16", cls=DuplicatesEnv)
    print(f"Using {len(new_duplicates)} fixed reference translations...")
    removed = 0
    overwritten = 0
    for orig, trans in duplicates.items():
        if orig not in new_duplicates or not new_duplicates[orig]:
            ref_translator.delete_translation(reference, trans, orig)
            removed = removed + 1
        else:
            if len(new_duplicates[orig]) > 1:
                print(f"Warning (too many translations): Choosing first translation for {orig}")
            ref_translator.update_translation(reference, translation, orig, new_duplicates[orig][0])
            overwritten = overwritten + 1

    print(f"Removed {removed} reference translations, overwritten {overwritten} translations")


def find_unfitting_translations(translations, source_lang) -> set[str]:
    """
    Return translations that are wrong in given list.
    This may mean:
    - partial text (compared to other elements in the list)
    - text in source_language (not a translation)

    :param translations:
    :param source_lang:
    :return:
    """
    to_remove = set()
    for i, translation in enumerate(translations.copy()):
        lang = t.detect_language(translation.text)
        for j in range(i + 1, len(translations)):
            if translations[j].text.startswith(translation.text):
                to_remove.add(translation.text)
                break
        if lang == source_lang:
            to_remove.add(translation.text)
    return to_remove


def autoresolve_duplicates(ref_translator, duplicates, source_lang, ref_dir, trans_dir):
    duplicates_count = len(duplicates)

    for orig, translations in tqdm(duplicates.copy().items(), total=duplicates_count, file=sys.stdout):
        translations.sort(key=lambda x: x.text)
        to_remove = find_unfitting_translations(translations, source_lang)
        duplicates[orig] = [x for x in duplicates[orig] if x.text not in to_remove]
        if len(duplicates[orig]) == 1:
            ref_translator.update_translation(orig, ref_dir, trans_dir, duplicates[orig][0].text)
            duplicates.pop(orig)
        elif len(duplicates[orig]) == 0:  # all duplicated should have been removed
            ref_translator.delete_translation(orig, ref_dir, trans_dir)

    print(
        f"{duplicates_count - len(duplicates)} duplications resolved! Cannot autoresolve {len(duplicates)} duplicates.")
    print("What do you want to do?")
    action_for_reference_translation(ref_translator, duplicates, source_lang, ref_dir, trans_dir,
                                     autoresolve_option=False)


def action_for_reference_translation(ref_translator, duplicates, source_lang, ref_dir, trans_dir, autoresolve_option):
    selection = [
        "Automatically resolve duplicates",
        "Resolve duplicates manually",
        "Don't use those translations"
    ]
    if not autoresolve_option:
        selection.pop(0)

    for n, x in enumerate(selection):
        print(f"\t{n + 1}) {x}")
    choice = input_num("Please select an option:", len(selection), 1)

    if choice == (len(selection) - 2):
        autoresolve_duplicates(ref_translator, duplicates, source_lang, ref_dir, trans_dir)
    elif choice == (len(selection) - 1):
        resolve_duplicates_by_user(ref_translator, ref_dir, trans_dir, duplicates)
    elif choice == len(selection):
        for orig, trans_dir in duplicates.items():
            ref_translator.delete_translation(ref_dir, trans_dir, orig)


def input_reference_translations(source_lang):
    ref_translator = rt.RefTranslator()

    first_question = True
    another = ""
    while True:
        if not first_question:
            another = "another "
        ref_translation_needed = input(f'Do you want to add {another}reference translation? (y/n):')
        if ref_translation_needed == 'y':
            ref_dir = input_dir('Enter reference mod text directory:')
            trans_dir = input_dir('Enter reference translation directory:')
            duplicates = ref_translator.add_ref(ref_dir, trans_dir)
            print("Duplicated translations detected! What do you want to do?")
            action_for_reference_translation(ref_translator, duplicates, source_lang, ref_dir, trans_dir,
                                             autoresolve_option=True)

        if ref_translation_needed == 'n':
            break
        first_question = False

    return ref_translator


def switch_dirs(source: Path, target: Path):
    # Set desired paths
    orig_path = target
    backup_path = Path(str(target) + "-backup")

    # rename paths
    print(f"Moving {target.name} to {backup_path.name}")
    target.rename(backup_path)
    print(f"Moving {source.name} to {target.name}")
    source.rename(orig_path)


if __name__ == "__main__":
    try:
        source_lang, target_lang = input_lang()
        moddir = input_dir('Enter a mod directory:')
        ref_translator = input_reference_translations(source_lang)

        # translation
        trandir = translate_dir(moddir, source_lang, target_lang, ref_translator)
        switch_dirs(trandir, moddir)

        print(f"Files in {moddir} replaced with {target_lang} translation!")
    except Exception:
        print("Something went wrong, details:")
        traceback.print_exc()

    sys.stderr.flush()
    print()
    input("Press any key to proceed...")
