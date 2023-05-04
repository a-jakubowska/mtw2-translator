import translate.translate as t


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


    fname = input('Enter an original file name:')
    nfile = input('Enter a new file name:')

    try:
        fhand = open(fname)
    except:
        print('File', fname, 'cannot be opened')
        exit()

    try:
        translate_file(fname, nfile, lang)
    except Exception as e:
        print(f"File {fname} cannot be translated ({e})")
