"""
This is the reference translation module.


"""

GameTextData = dict[str, str]
Translation = dict[str, str]


class RefTranslator:
    translations = []

    def add_ref(self, original_dir: str, reference_dir: str) -> None:
        """Return a

        >>> r = RefTranslator()
        >>> r.add_ref("./examples/prio1/org", "./examples/prio1/ref")
        Collected 1 translated keys (100%)!
        >>> r.add_ref("./examples/prio2/org", "./examples/prio2/ref")
        Collected 3 translated keys (100%)!

        :param original_dir:
        :param reference_dir:
        """
        from pathlib import Path

        def get_filedata(fname: Path) -> GameTextData:
            import re
            res = {}
            with open(fname, encoding="utf16") as f:
                last_key = None
                for line in f:
                    line = line.rstrip()
                    match = re.fullmatch(r"{(.*)}(.*)", line)
                    if match and len(match.groups()) == 2:
                        last_key = match.group(1)
                        res[last_key] = match.group(2)
                    elif last_key and res[last_key] == "":
                        if not line.startswith("¬"):
                            res[last_key] = line
            return res

        def get_dirdata(dname: Path) -> GameTextData:
            res = {}
            for filepath in dname.iterdir():
                try:
                    keys = get_filedata(filepath)
                    res.update(keys)
                except Exception as e:
                    print(f"Cannot process {filepath}!")
                    print(e)
                    print("Continue to the next file...")
            return res

        def get_translation(o: GameTextData, r: GameTextData) -> Translation:
            allkeys = set(o)
            allkeys.update(r)
            # print(f"Collected {len(allkeys)} unique keys!")
            res = {}
            for key in allkeys:
                if key in orig and key in ref:
                    o = orig[key]
                    r = ref[key]
                    if o != r:
                        res[o] = r
            return res, allkeys

        orig = get_dirdata(Path(original_dir))
        # print(f"Collected {len(orig)} keys from original directory!")
        ref = get_dirdata(Path(reference_dir))
        # print(f"Collected {len(ref)} keys from reference translation directory!")

        translation, keys = get_translation(orig, ref)
        percentage = (len(translation) / len(keys)) * 100
        n = sum(len(o.rstrip()) for o in orig)
        print(f"There are {n} characters to translate!")
        print(f"Collected {len(translation)} translated keys ({percentage:.0f}%)!")
        self.translations.append({
            "orig": original_dir,
            "ref": reference_dir,
            "translation": translation
        })

    def get_ref(self, text: str) -> str | None:
        """Return a

        >>> r = RefTranslator()
        >>> r.add_ref("./examples/prio1/org", "./examples/prio1/ref")
        Collected 1 translated keys (100%)!
        >>> r.add_ref("./examples/prio2/org", "./examples/prio2/ref")
        Collected 3 translated keys (100%)!
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
                return t[text]
        return None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
