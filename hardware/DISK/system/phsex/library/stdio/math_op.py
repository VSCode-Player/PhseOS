from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_write,op_stop_os,op_data_transform
from PhseXlib.locals import * # type: ignore
import json

# CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def add(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    if not FIRST_ADDR["file"] == "TYPE:INT":
        with open(FIRST_ADDR["file"],"r",encoding="utf-8") as FIRST_FILE:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                FIRST_DICT = json.load(FIRST_FILE)
                SECOND_DICT = json.load(SECOND_FILE)
                result = int(FIRST_DICT[first_addr],2) + int(SECOND_DICT[second_addr],2)
    elif FIRST_ADDR["file"] == "TYPE:INT":
        if not SECOND_ADDR["file"] in ["TYPE:INT","TYPE:STRING"]:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                SECOND_DICT = json.load(SECOND_FILE)
                result = int(SECOND_DICT[second_addr],2) + int(FIRST_ADDR["key"])
        else:
            op_stop_os("Error from ADD:Second addres cannot be INT or STRING.",1,error_args=f"{first_addr} {second_addr}")
    else:
        result = 0
        op_stop_os("Error from ADD:First addres cannot be STRING.",1,error_args=f"{first_addr} {second_addr}")
    
    op_write(op_data_transform(result, INT_TO_BIN),SECOND_ADDR) # type: ignore

def sub(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    if not FIRST_ADDR["file"] == "TYPE:INT":
        with open(FIRST_ADDR["file"],"r",encoding="utf-8") as FIRST_FILE:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                FIRST_DICT = json.load(FIRST_FILE)
                SECOND_DICT = json.load(SECOND_FILE)
                result = int(FIRST_DICT[first_addr],2) - int(SECOND_DICT[second_addr],2)
    elif FIRST_ADDR["file"] == "TYPE:INT":
        if not SECOND_ADDR["file"] in ["TYPE:INT","TYPE:STRING"]:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                SECOND_DICT = json.load(SECOND_FILE)
                result = int(SECOND_DICT[second_addr],2) - int(FIRST_ADDR["key"])
        else:
            op_stop_os("Error from SUB:Second addres cannot be INT or STRING.",1,error_args=f"{first_addr} {second_addr}")
    else:
        result = 0
        op_stop_os("Error from SUB:First addres cannot be STRING.",1,error_args=f"{first_addr} {second_addr}")
    
    op_write(op_data_transform(result, INT_TO_BIN),SECOND_ADDR) # type: ignore

def mul(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    if not FIRST_ADDR["file"] == "TYPE:INT":
        with open(FIRST_ADDR["file"],"r",encoding="utf-8") as FIRST_FILE:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                FIRST_DICT = json.load(FIRST_FILE)
                SECOND_DICT = json.load(SECOND_FILE)
                result = int(FIRST_DICT[first_addr],2) * int(SECOND_DICT[second_addr],2)
    elif FIRST_ADDR["file"] == "TYPE:INT":
        if not SECOND_ADDR["file"] in ["TYPE:INT","TYPE:STRING"]:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                SECOND_DICT = json.load(SECOND_FILE)
                result = int(SECOND_DICT[second_addr],2) * int(FIRST_ADDR["key"])
        else:
            op_stop_os("Error from MUL:Second addres cannot be INT or STRING.",1,error_args=f"{first_addr} {second_addr}")
    else:
        result = 0
        op_stop_os("Error from MUL:First addres cannot be STRING.",1,error_args=f"{first_addr} {second_addr}")
    
    op_write(op_data_transform(result, INT_TO_BIN),SECOND_ADDR) # type: ignore

def div(first_addr, second_addr):
    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    if not FIRST_ADDR["file"] == "TYPE:INT":
        with open(FIRST_ADDR["file"],"r",encoding="utf-8") as FIRST_FILE:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                FIRST_DICT = json.load(FIRST_FILE)
                SECOND_DICT = json.load(SECOND_FILE)

                if SECOND_DICT[second_addr] != bin(0):
                    result = int(FIRST_DICT[first_addr],2) / int(SECOND_DICT[second_addr],2)
                else:
                    op_stop_os("The divisor cannot be 0",1,error_args=second_addr)
    elif FIRST_ADDR["file"] == "TYPE:INT":
        if not SECOND_ADDR["file"] in ["TYPE:INT","TYPE:STRING"]:
            with open(SECOND_ADDR["file"],"r+",encoding="utf-8") as SECOND_FILE:
                SECOND_DICT = json.load(SECOND_FILE)
                if SECOND_DICT[second_addr] != bin(0):
                    result = int(FIRST_ADDR["key"],2) / int(SECOND_DICT[second_addr],2)
                else:
                    op_stop_os("The divisor cannot be 0",1,error_args=second_addr)
        else:
            op_stop_os("Error from DIV:Second addres cannot be INT or STRING.",1,error_args=f"{first_addr} {second_addr}")
    else:
        result = 0
        op_stop_os("Error from DIV:First addres cannot be STRING.",1,error_args=f"{first_addr} {second_addr}")
    
    op_write(op_data_transform(result, INT_TO_BIN),SECOND_ADDR) # type: ignore

def cmp(first_addr, second_addr):

    FIRST_ADDR = addres_transformer(first_addr)    # 第一个地址的文件数据，类型dict
    SECOND_ADDR = addres_transformer(second_addr)  # 第二个地址的文件数据，类型dict

    # 处理第一个操作数
    if FIRST_ADDR.get("file") == "TYPE:INT":
        # 立即数，key 是十进制字符串
        first_value = int(FIRST_ADDR["key"])
    else:
        # 从文件读取，值是二进制字符串
        with open(FIRST_ADDR["file"], "r", encoding="utf-8") as FIRST_FILE:
            FIRST_DICT = json.load(FIRST_FILE)
            first_value = int(FIRST_DICT[FIRST_ADDR["key"]], 2)  # 文件里是二进制

    # 处理第二个操作数
    if SECOND_ADDR.get("file") == "TYPE:INT":
        # 立即数，key 是十进制字符串
        second_value = int(SECOND_ADDR["key"])
    else:
        # 从文件读取，值是二进制字符串
        with open(SECOND_ADDR["file"], "r", encoding="utf-8") as SECOND_FILE:
            SECOND_DICT = json.load(SECOND_FILE)
            second_value = int(SECOND_DICT[SECOND_ADDR["key"]], 2)  # 文件里是二进制

    # 比较并写入结果
    if first_value > second_value:
        op_write(1, {"file": CONFIG["REG_flag_file"], "key": "CMP"})
    elif first_value < second_value:
        op_write(-1, {"file": CONFIG["REG_flag_file"], "key": "CMP"})
    else:
        op_write(0, {"file": CONFIG["REG_flag_file"], "key": "CMP"})