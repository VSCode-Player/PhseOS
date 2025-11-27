import json
from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import op_write
from pathlib import Path

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def mov(first_addr,second_addr):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)
    with open(first_addr_dict["file"],"r+",encoding="utf-8") as first_file:
        with open(second_addr_dict["file"],"r+",encoding="utf-8") as second_file:
            first_dict = json.load(first_file)
            # second_dict = json.load(second_file)
            op_write(first_dict[first_addr_dict["key"]],second_addr_dict)