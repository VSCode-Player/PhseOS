from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_write,op_stop_os
from sys import exit
import json
from pathlib import Path

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
            result = FIRST_DICT[first_addr] + SECOND_DICT[second_addr]
            op_write(result,SECOND_ADDR)

def sub(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    with open(FIRST_ADDR["file"],"r+",encoding="utf-8") as FIRST_FILE:
        with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
            # 加载两个文件为dict
            FIRST_DICT = json.load(FIRST_FILE)
            SECOND_DICT = json.load(SECOND_FILE)
            # 算出结果并写入
            result = FIRST_DICT[first_addr] - SECOND_DICT[second_addr]
            op_write(result,SECOND_ADDR)

def mul(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    with open(FIRST_ADDR["file"],"r+",encoding="utf-8") as FIRST_FILE:
        with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
            # 加载两个文件为dict
            FIRST_DICT = json.load(FIRST_FILE)
            SECOND_DICT = json.load(SECOND_FILE)
            # 算出结果并写入
            result = FIRST_DICT[first_addr] * SECOND_DICT[second_addr]
            op_write(result,SECOND_ADDR)

def div(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    with open(FIRST_ADDR["file"],"r+",encoding="utf-8") as FIRST_FILE:
        with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
            # 加载两个文件为dict
            FIRST_DICT = json.load(FIRST_FILE)
            SECOND_DICT = json.load(SECOND_FILE)

            if SECOND_DICT[second_addr] == 0:
                op_stop_os(f"The divisor cannot be zero",1)

            # 算出结果并写入
            result = FIRST_DICT[first_addr] / SECOND_DICT[second_addr]
            op_write(result,SECOND_ADDR)
