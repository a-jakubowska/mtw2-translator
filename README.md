# mtw2-translator
Translator for Medieval Total War II mods

# Usage

Steps to Follow:

1. Optional - Install Pthon version
2. Download and run mtw2-translator exe file
4. In opened console type language and folder name (see example)
5. In case you have any referance translation, you can also use them
6. ❗Program is using web version of Google Translator,it can take long time to process. 
7. Remove .bin files in Medieval Total War II Mod folder. 
8. Restart the game and enjoy!


## Example


```commandline
Avaliable languages:
afrikaans (af)
(...)
zulu (zu)
Enter target languague:pl
Enter a mod directory:D:/mods/DaC_v5/data/text
Do you want to add reference translation? (y/n):y
Enter reference mod text directory:D:/mods/DaC_v4/data/text
Enter reference translation directory:D:/mods/DaC_v4_PL
There are 670286 characters to translate!
Collected 9833 translated keys (33%)!
Do you want to add another reference translation? (y/n):n
Translating D:\mods\DaC_v5\data\text\battle.txt to D:\mods\DaC_v5\data\text-pl\battle.txt (pl). Please be patient, it can take few minutes.
(...)
Moving D:\mods\DaC_v5\data\text to D:\mods\DaC_v5\data\text-backup
Moving D:\mods\DaC_v5\data\text-pl to D:\mods\DaC_v5\data\text
```

# Experimental 

## DeepL

You can use DeepL translation, but you need to provide API key
You need to execute script from .py, not from exe!

```commandline
set DEEPL_API_KEY="asd...43fsat"
py mtw2-translator.py
```
