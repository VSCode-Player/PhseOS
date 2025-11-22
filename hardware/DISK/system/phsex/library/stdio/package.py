from PhseXlib.addres import addres_transformer
from pathlib import Path
import json

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def add(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)
    SECOND_ADDR = addres_transformer(second_addr)

    with open(FIRST_ADDR["file"],"r+",encoding="utf-8") as FIRST_FILE:
        with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
            FIRST_DICT = json.load(FIRST_FILE)
            SECOND_DICT = json.load(SECOND_FILE)
            SECOND_DICT[second_addr] = FIRST_DICT[first_addr] + SECOND_DICT[second_addr]
            SECOND_FILE.seek(0)
            SECOND_FILE.truncate()
            SECOND_FILE.write(json.dumps(SECOND_DICT))

EXPORT = {
    "ADD":add
}