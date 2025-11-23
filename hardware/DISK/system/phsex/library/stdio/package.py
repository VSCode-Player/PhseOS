from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_write
from pathlib import Path
import json

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def add(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    with open(FIRST_ADDR["file"],"r+",encoding="utf-8") as FIRST_FILE:
        with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
            # 加载两个文件为dict
            FIRST_DICT = json.load(FIRST_FILE)
            SECOND_DICT = json.load(SECOND_FILE)
            # 算出结果并写入
            SECOND_DICT[second_addr] = FIRST_DICT[first_addr] + SECOND_DICT[second_addr]
            op_write(json.dumps(SECOND_DICT),SECOND_ADDR)