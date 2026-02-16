from PhseXlib.locals import * # type: ignore
from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_data_transform
from phsex import symbol_table
from pathlib import Path
import json
import re

Encode_dict = GetEncoding("PhseEncode")
point = re.compile(r"^\[(?![0-9]+$)[a-zA-Z0-9_]+\]$")

def msg(*string):
    if string == ("",): # 判断是否输出标签PC的内容
        print(json.load(
            Path(CONFIG["REG_flag_file"]).open("r",encoding="utf-8"))["PC"]
            )
    elif re.fullmatch(point, string[0]):
        key = string[0][1:-1]  # 去掉 [A] 的中括号，得到 "A"
        if key in symbol_table:
            data_file_dict = addres_transformer(symbol_table[key])
            with open(data_file_dict["file"], "r", encoding="utf-8") as data_file:
                data_dict = json.load(data_file)
                print(op_data_transform(data_dict[data_file_dict["key"]], BIN_TO_CHAR))
    else:    
        for i in string:
            if not i:
                continue
            if i[0] == "b":
                print(Encode_dict[i[1:]])
            else:
                # 保留原来去掉首尾字符的行为（如果字符串有引号），否则使用原串
                inner = i[1:-1] if len(i) >= 2 else i
                # 使用映射进行字符串替换，例如 "\\n" -> "\n"
                for key, val in format_dict.items(): # format_dict在local.py中定义
                    inner = inner.replace("\\" + key, val)
                print(inner, end="")