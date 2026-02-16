from PhseXlib.locals import * # type: ignore
from PhseXlib.addres import addres_transformer
from phsex import symbol_table
from pathlib import Path
import json
Encode_dict = GetEncoding("PhseEncode")

def msg(*string):
    if string == ("",): # 判断是否输出标签PC的内容
        print(json.load(
            Path(CONFIG["REG_flag_file"]).open("r",encoding="utf-8"))["PC"]
            )
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