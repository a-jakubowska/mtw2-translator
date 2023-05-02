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
        Collected 1 translated keys!
        >>> r.add_ref("./examples/prio2/org", "./examples/prio2/ref")
        Collected 3 translated keys!

        :param original_dir:
        :param reference_dir:
        """
        from pathlib import Path

        def get_filedata(fname: Path) -> GameTextData:
            import re
            res = {}
            with open(fname, encoding="utf16") as f:
                for line in f:
                    match = re.fullmatch(r"{(.*)}(.*)", line.rstrip())
                    if match and len(match.groups()) == 2:
                        res[match.group(1)] = match.group(2)
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
            return res

        orig = get_dirdata(Path(original_dir))
        # print(f"Collected {len(orig)} keys from original directory!")
        ref = get_dirdata(Path(reference_dir))
        # print(f"Collected {len(ref)} keys from reference translation directory!")

        translation = get_translation(orig, ref)
        print(f"Collected {len(translation)} translated keys!")
        self.translations.append({
            "orig": original_dir,
            "ref": reference_dir,
            "translation": translation
        })

    def get_ref(self, text: str) -> str | None:
        """Return a

        >>> r = RefTranslator()
        >>> r.add_ref("./examples/prio1/org", "./examples/prio1/ref")
        Collected 1 translated keys!
        >>> r.add_ref("./examples/prio2/org", "./examples/prio2/ref")
        Collected 3 translated keys!
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
