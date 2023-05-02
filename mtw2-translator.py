import translate.translate as t


def translate_file(filename):
    import re
    file = open(filename, encoding='utf-16')
    new = open(input('Enter a file name:'), 'w', encoding='utf-16')
    for line in file:
        match = re.fullmatch(r"({.*})(.*)", line.rstrip())
        if match and len(match.groups()) == 2:
            key = match.group(1)
            value = match.group(2)
            text = t.translate(value, "pl")
            new.write(key + text + '\n')
        else:
            new.write(line)


if __name__ == "__main__":
    fname = input('Enter file name:')
    try:
        fhand = open(fname)
    except:
        print('File', fname, 'cannot be opened')
        exit()
    translate_file(fname)
