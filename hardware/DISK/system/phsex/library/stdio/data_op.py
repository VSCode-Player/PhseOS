import json
import re
from PhseXlib.addres import addres_transformer
from PhseXlib.op_lib import *
from PhseXlib.locals import * # type: ignore
from phsex import lable_table, imported_package, args_partten
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
            # with open(second_addr_dict["file"],"r+",encoding="utf-8") as second_file:
                first_file_dict = json.load(first_file)
                op_write(first_file_dict[first_addr_dict["key"]],second_addr)

def left_shift(addr, num):
    addr = addres_transformer(addr)

    with open(addr["file"],"r+",encoding="utf-8") as FILE:
        FILE_DICT = json.load(FILE)
        op_write(FILE_DICT[addr["key"]][int(num):] + "0"*int(num),addr) # 左移，高位补0

def right_shift(addr, num):
    addr = addres_transformer(addr)

    with open(addr["file"],"r+",encoding="utf-8") as FILE:
        FILE_DICT = json.load(FILE)
        op_write("0"*int(num) + FILE_DICT[addr["key"]][:-int(num)],addr) # 右移，高位补0

def set_flag(data, flag):
    with open(CONFIG["REG_flag_file"],"r+",encoding="utf-8") as REG_F_file:
        REG_F_dict = json.load(REG_F_file)

        if flag in REG_F_dict:
            try:
                op_write(int(data), {"file":CONFIG["REG_flag_file"],"key":flag})
            except ValueError:
                if data[0] == "\"" and data[-1] == "\"":
                    op_write(data[1:-1], {"file":CONFIG["REG_flag_file"],"key":flag})
                else:
                    op_stop_os(f"Invalid data type for flag '{flag}'.",1)
        else:
            op_stop_os(f"Flag '{flag}' not found.",1)

def set_status(addr:str, status:str):
    addr_dict = addres_transformer(addr)
    status_file = os.path.join(os.path.dirname(addr_dict["file"]), "status.json")

    status_dict = json.load(Path(status_file).open("r+",encoding="utf-8"))
    if addr_dict["key"] in status_dict:
        status_dict[addr_dict["key"]] = status
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_dict, f)

def get_input(addr:str, type:str):
    addr_dcict = addres_transformer(addr)
    data = input()
    if type == "INT":
        data = op_data_transform(data, INT_TO_BIN) # type: ignore
    elif type == "STRING":
        if len(data) == 1:
            data = op_data_transform(data, CHAR_TO_BIN) # type: ignore
        else:
            op_stop_os("Only single character input is supported.",1)
    else:
        op_stop_os(f"Invalid data type '{type}' for input.",1)
    
    op_write(data, addr_dcict)

# --- 跳转命令 ---
def jmp(lable):
    if lable in lable_table:
        for i in lable_table[lable]:
            if i["name"] in imported_package[0]:
                args = [a.strip() for a in re.split(args_partten, i['args'])]
                imported_package[0][i["name"]](*args)
    else:
        op_stop_os(f"LABLE '{lable}' not found.", 1)


def jz(label):
    with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
        cmp = int(json.load(f)["CMP"])
    if cmp == 0:
        if label in lable_table:
            for i in lable_table[label]:
                if i["name"] in imported_package[0]:
                    args = [a.strip() for a in re.split(args_partten, i['args'])]
                    imported_package[0][i["name"]](*args)
        else:
            op_stop_os(f"LABLE '{label}' not found.", 1)

def jnz(label):
    with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
        cmp = int(json.load(f)["CMP"])
    if cmp != 0:
        if label in lable_table:
            for i in lable_table[label]:
                if i["name"] in imported_package[0]:
                    args = [a.strip() for a in re.split(args_partten, i['args'])]
                    imported_package[0][i["name"]](*args)
        else:
            op_stop_os(f"LABLE '{label}' not found.", 1)

def jg(label):
    with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
        cmp = int(json.load(f)["CMP"])
    if cmp > 0:
        if label in lable_table:
            for i in lable_table[label]:
                if i["name"] in imported_package[0]:
                    args = [a.strip() for a in re.split(args_partten, i['args'])]
                    imported_package[0][i["name"]](*args)
        else:
            op_stop_os(f"LABLE '{label}' not found.", 1)

def jl(label):
    with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
        cmp = int(json.load(f)["CMP"])
    if cmp < 0:
        if label in lable_table:
            for i in lable_table[label]:
                if i["name"] in imported_package[0]:
                    args = [a.strip() for a in re.split(args_partten, i['args'])]
                    imported_package[0][i["name"]](*args)
        else:
            op_stop_os(f"LABLE '{label}' not found.", 1)

def jge(label):
    with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
        cmp = int(json.load(f)["CMP"])
    if cmp >= 0:
        if label in lable_table:
            for i in lable_table[label]:
                if i["name"] in imported_package[0]:
                    args = [a.strip() for a in re.split(args_partten, i['args'])]
                    imported_package[0][i["name"]](*args)
        else:
            op_stop_os(f"LABLE '{label}' not found.", 1)

def jle(label):
    with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
        cmp = int(json.load(f)["CMP"])
    if cmp <= 0:
        if label in lable_table:
            for i in lable_table[label]:
                if i["name"] in imported_package[0]:
                    args = [a.strip() for a in re.split(args_partten, i['args'])]
                    imported_package[0][i["name"]](*args)
        else:
            op_stop_os(f"LABLE '{label}' not found.", 1)