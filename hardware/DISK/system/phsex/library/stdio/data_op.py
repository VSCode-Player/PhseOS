import json
import re
from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_write,op_data_transform
from PhseXlib.locals import * # type: ignore
from pathlib import Path

# CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def mov(first_addr,second_addr):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)
    if first_addr_dict["file"] == "TYPE:STRING":
        op_write(op_data_transform(first_addr_dict["key"][1],CHAR_TO_BIN),second_addr_dict) # type: ignore
    elif first_addr_dict["file"] == "TYPE:INT":
        op_write(op_data_transform(first_addr_dict["key"],INT_TO_BIN),second_addr_dict)
    else:
        with open(first_addr_dict["file"],"r+",encoding="utf-8") as first_file:
            with open(second_addr_dict["file"],"r+",encoding="utf-8") as second_file:
                first_file_dict = json.load(first_file)
                op_write(first_file_dict[first_addr_dict["key"]],second_addr)