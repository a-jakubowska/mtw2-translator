def translate_file(filename):
    import re
    file = open(fname, encoding='utf-16')
    lista = list()
    for line in file:
        line = line.rstrip()
        reg = re.findall('^{.*}(.*)', line)
        lista.append(reg)
    return lista


if __name__ == "__main__":
    fname = input('Enter file name:')
    ready_to_translate = translate_file(fname)

import translate.translate as t
text=list()
for n in ready_to_translate:
    for a in n:
        btext=(t.translate(a, "pl"))
        text.append(btext)
