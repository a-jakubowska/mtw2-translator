import translate as t
import reference_translation as rt
from cli import *

import re
import sys
import logging
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


def translate_dir(dirname: str, source_lang: str, target_lang: str, ref_translator: rt.RefTranslator) -> None:
    # Create Path object from string
    dirpath = Path(dirname)

    # Create directory to store translations
    translated_dir = dirpath.parent / (dirpath.name + "-" + target_lang)
    if not translated_dir.exists():
        translated_dir.mkdir()

    logging.info(f"Translating {dirname} directory ({source_lang} -> {target_lang})...")

    # Translate file-by-file
    keys_referenced = 0
    keys_translated = 0
    keys_intact = 0
    for orig_file in dirpath.glob('*.txt'):
        translated_file = translated_dir / orig_file.name
        logging.info(
            f"Translating {orig_file} to {translated_file} ({target_lang}). Please be patient, it can take few minutes.")
        try:
            ref, trans, intact = translate_file(orig_file, translated_file, source_lang, target_lang, ref_translator)
            logging.info(
                f"{orig_file} translated ({ref} from reference translations, {trans} translated, {intact} left intact)")
            keys_referenced = keys_referenced + ref
            keys_translated = keys_translated + trans
            keys_intact = keys_intact + intact
        except Exception as e:
            logging.error(f"Cannot process {orig_file} ({e})! Continue to the next file...")

    # Summary
    logging.info(f"Directory {dirpath} translated with:")
    keys_total = keys_referenced + keys_translated + keys_intact
    logging.info(f"\t*{keys_total} strings translated")
    ref_percent = (keys_referenced / keys_total) * 100
    logging.info(f"\t*{keys_referenced} strings taken from reference translations ({ref_percent:.0f}%)")
    trans_percent = (keys_translated / keys_total) * 100
    logging.info(f"\t*{keys_translated} strings machine translated ({trans_percent:.0f}%)")
    intact_percent = (keys_intact / keys_total) * 100
    logging.info(f"\t*{keys_intact} strings left intact ({intact_percent:.0f}%)")

    # Set desired paths
    orig_path = dirpath
    backup_path = Path(str(dirpath) + "-backup")

    # rename paths
    logging.info(f"Moving {dirpath.name} to {backup_path.name}")
    dirpath.rename(backup_path)
    logging.info(f"Moving {translated_dir.name} to {orig_path.name}")
    translated_dir.rename(orig_path)


def configure_logger():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create handler that writes logs to logfile
    logfile_handler = logging.FileHandler('log.txt')
    logfile_handler.setLevel(logging.INFO)
    logfile_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logfile_handler.setFormatter(logfile_formatter)
    logger.addHandler(logfile_handler)

    logging.info("=" * 40 + " START " + "=" * 40)

    # Create handler that writes logs to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_formatter = logging.Formatter('%(message)s')
    stdout_handler.setFormatter(stdout_formatter)
    logger.addHandler(stdout_handler)


if __name__ == "__main__":
    try:
        configure_logger()

        source_lang, target_lang = input_lang()
        moddir = input_dir('Enter a mod directory:')
        ref_translator = input_reference_translations()

        # translation
        translate_dir(moddir, source_lang, target_lang, ref_translator)

        logging.info(f"Files in {moddir} replaced with {target_lang} translation!")
    except Exception:
        logging.error("Something went wrong, details:")
        logging.error(traceback.format_exc())

    print()
    input("Press any key to proceed...")
