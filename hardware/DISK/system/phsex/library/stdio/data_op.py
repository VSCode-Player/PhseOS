import json
import re
from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_write,op_data_transform
from PhseXlib.locals import CHAR_TO_BIN
from pathlib import Path

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))



def mov(first_addr,second_addr):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)
    write_data = first_addr_dict["key"][1] # type: ignore
    if first_addr_dict["file"] == "TYPE:STRING":
        op_write(op_data_transform(write_data,CHAR_TO_BIN),second_addr_dict) # type: ignore
    else:
        with open(first_addr_dict["file"],"r+",encoding="utf-8") as first_file:
            with open(second_addr_dict["file"],"r+",encoding="utf-8") as second_file:
                first_file_dict = json.load(first_file)
                op_write(write_data,second_addr)