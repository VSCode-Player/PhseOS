from PhseXlib.locals import * # type: ignore
from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_data_transform, op_stop_os
from phsex import symbol_table
from pathlib import Path
import json
import re

Encode_dict = GetEncoding("PhseEncode")

def msg(*string):
    '''
    用法:
    MSG "STR"
    MSG [POINT], INT/STR    ;二进制转字符串字符串仅支持PhseEncode字符集
    MSG                     ;打印PC标签的内容
    '''
    
    if string:  # 如果有参数
        first_arg = addres_transformer(string[0]) # 解析第一个参数
        if first_arg["file"] in ["TYPE:STRING", "TYPE:POINT"]:
            if first_arg["file"] == "TYPE:STRING": # 如果是字符串
                print(first_arg["key"])

            else: # 如果是指针
                second_arg = string[1] if len(string) >= 2 else op_stop_os("MSG Point mode need 2 arguments.",1)

                point_name = first_arg["key"]
                if point_name in symbol_table:
                    point_addr = symbol_table[point_name]
                    point_addr_dict = addres_transformer(point_addr)
                    point_data = json.load(Path(point_addr_dict["file"]).open("r",encoding="utf-8"))[point_addr_dict["key"]]
                    if second_arg in ["INT","STR"]:
                        if second_arg == "INT":
                            print(op_data_transform(point_data, BIN_TO_INT))
                        elif second_arg == "STRING":
                            print(op_data_transform(point_data, BIN_TO_CHAR))
                    else:
                        op_stop_os("MSG Point mode second argument must be INT or STR.",1)
                else:
                    op_stop_os(f"{point_name} is not found in symbol table.",1)
    else:
        op_stop_os("MSG must use 1 argument or use more.",1)

def OS_STOP(*args):
    op_stop_os("OS stopped by OS_STOP instruction.", 0)