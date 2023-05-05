import translate as t
import reference_translation as rt
from pathlib import Path


def translate_file(filename, newfilename, lang):
    import re
    file = open(filename, encoding='utf-16')
    new = open(newfilename, 'w', encoding='utf-16')
    for line in file:
        match = re.fullmatch(r"({.*})(.*)", line.rstrip())
        if match and len(match.groups()) == 2:
            key = match.group(1)
            value = match.group(2)
            text = t.translate(value, lang)
            new.write(key + text + '\n')
        else:
            new.write(line)


def translate_dir(dirname: str, lang: str) -> None:
    # Create Path object from string
    dirpath = Path(dirname)

    # Create directory to store translations
    translated_dir = dirpath.parent / (dirpath.name + "-" + lang)
    if not translated_dir.exists():
        translated_dir.mkdir()

    # Translate file-by-file
    for orig_file in dirpath.glob('*.txt'):
        translated_file = translated_dir / orig_file.name
        print(f"Translating {orig_file} to {translated_file} ({lang})")
        translate_file(orig_file, translated_file, lang)

    # Set desired paths
    orig_path = dirpath
    backup_path = Path(str(dirpath) + "-orig")

    # rename paths
    print(f"Moving {dirpath.name} to {backup_path.name}")
    dirpath.rename(backup_path)
    print(f"Moving {translated_dir.name} to {orig_path.name}")
    translated_dir.rename(orig_path)


if __name__ == "__main__":
    langdict = t.get_available_languages()
    print("Avaliable languages:")
    for full_lang_name, abbr in langdict.items():
        print(f"{full_lang_name} ({abbr})")

    while True:
        lang = input("Enter target languague:")
        if lang not in langdict.keys() and lang not in langdict.values():
            print("Wrong language. Try again.")
        else:
            break

    moddir = input('Enter a mod directory:')

    # translation
    translate_dir(moddir, lang)
