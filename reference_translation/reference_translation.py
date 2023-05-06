"""
This is the reference translation module.


"""

from pathlib import Path
from dataclasses import dataclass

GameTextData = dict[str, str]
Translation = dict[str, str]


@dataclass
class Translation:
    file: Path
    line: int
    key: str
    text: str


@dataclass
class DuplicateTranslation(Translation):
    hits: int

    def __init__(self, t: Translation, hits: int = 1):
        self.file = t.file
        self.line = t.line
        self.key = t.key
        self.text = t.text
        self.hits = hits


class RefTranslator:
    translations = []

    def __init__(self, interactive=False):
        self.interactive = interactive

    def add_ref(self, original_dir: str, reference_dir: str) -> dict[str, Translation]:
        """Return a

        >>> r = RefTranslator()
        >>> r.add_ref("./examples/prio1/org", "./examples/prio1/ref")
        There are 12 characters to translate!
        Found 0 duplications in translation!
        Collected 1 translated keys (100%)!
        {}
        >>> r.add_ref("./examples/prio2/org", "./examples/prio2/ref")
        There are 38 characters to translate!
        Found 0 duplications in translation!
        Collected 3 translated keys (100%)!
        {}

        :param original_dir:
        :param reference_dir:
        """

        def get_filedata(fname: Path) -> GameTextData:
            import re
            res = {}
            with open(fname, encoding="utf16") as f:
                last_key = None
                for n, line in enumerate(f):
                    line = line.rstrip()
                    match = re.fullmatch(r"{(.*)}(.*)", line)
                    if match and len(match.groups()) == 2:
                        last_key = match.group(1)
                        res[last_key] = Translation(fname, n, last_key, match.group(2))
                    # Sometimes key is in one line and value in other
                    # If last key do not have value this code assumes it is in the next line
                    elif last_key and res[last_key].text == "":
                        if not line.startswith("¬"):
                            res[last_key].text = line
            return res

        def get_dirdata(dname: Path) -> GameTextData:
            res = {}
            for filepath in dname.iterdir():
                try:
                    keys = get_filedata(filepath)
                    res.update(keys)
                except Exception as e:
                    print(f"Cannot process {filepath} ({e})! Continue to the next file...")
            return res

        def get_translation(o: GameTextData, r: GameTextData) -> Translation:
            allkeys = set(o)
            allkeys.update(r)
            res = {}
            duplicates = {}
            for key in allkeys:
                if key in orig and key in ref:
                    o = orig[key].text
                    r = ref[key]
                    if o != r:
                        if o in res and res[o].text != r.text:
                            if o in duplicates:
                                already_added = False
                                for existing_duplicate in duplicates[o]:
                                    if r.text == existing_duplicate.text:
                                        existing_duplicate.hits = existing_duplicate.hits + 1
                                        already_added = True
                                if not already_added:
                                    duplicates[o].append(DuplicateTranslation(r))
                            else:
                                duplicates[o] = [DuplicateTranslation(res[o]), DuplicateTranslation(r)]
                        res[o] = r
            for k, v in res.items():
                v = v.text
            return res, allkeys, duplicates

        orig = get_dirdata(Path(original_dir))
        ref = get_dirdata(Path(reference_dir))

        translation, keys, duplicates = get_translation(orig, ref)
        percentage = (len(translation) / len(keys)) * 100
        n = sum(len(o.rstrip()) for o in orig)
        print(f"There are {n} characters to translate!")
        print(f"Found {len(duplicates)} duplications in translation!")
        print(f"Collected {len(translation)} translated keys ({percentage:.0f}%)!")
        self.translations.append({
            "orig": original_dir,
            "ref": reference_dir,
            "translation": translation
        })
        return duplicates

    def update_translation(self, original_dir, reference_dir, original_text, translated_text):
        for t in self.translations:
            if t["orig"] == original_dir and t["ref"] == reference_dir:
                t["translation"][original_text] = translated_text

    def delete_translation(self, original_dir, reference_dir, original_text):
        for t in self.translations:
            if t["orig"] == original_dir and t["ref"] == reference_dir:
                t["translation"].pop(original_text)

    def get_ref(self, text: str) -> str | None:
        """Return a

        >>> r = RefTranslator()
        >>> r.add_ref("./examples/prio1/org", "./examples/prio1/ref")
        There are 12 characters to translate!
        Found 0 duplications in translation!
        Collected 1 translated keys (100%)!
        {}
        >>> r.add_ref("./examples/prio2/org", "./examples/prio2/ref")
        There are 38 characters to translate!
        Found 0 duplications in translation!
        Collected 3 translated keys (100%)!
        {}
        >>> r.get_ref("Fire of Udûn")
        'Ogień Udunu'
        >>> r.get_ref("Ent Rage")
        'Szał Entów'

        :param text:
        :return:
        """
        for tinfo in self.translations:
            t = tinfo["translation"]
            if text in t:
                return t[text].text
        return None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
