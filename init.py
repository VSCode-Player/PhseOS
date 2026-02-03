import json
from pathlib import Path
from PhseXlib.op_lib import op_stop_os
from os.path import exists,isdir,isfile

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))
RAM_addr_len = 8
REG_addr_len = 1

def RAM_init():
    RAM_dict = {f"{i:#010x}":"00000000" for i in range(CONFIG["memory_size"]) }
    RAM_status_dict = {f"{i:#010x}":"free" for i in range(CONFIG["memory_size"]) }
    Path(CONFIG["RAM_file"]).open("w",encoding="utf-8").write(json.dumps(RAM_dict))
    Path(CONFIG["RAM_status_file"]).open("w",encoding="utf-8").write(json.dumps(RAM_status_dict))


def REG_init():
    REG_dict = {f"R{str(i)}":"00000000" for i in range(CONFIG["reg_set"]["reg_count"]) }
    REG_status_dict = {f"R{str(i)}":"free" for i in range(CONFIG["reg_set"]["reg_count"]) }
    REG_flag_dict = {"PC":""}
    Path(CONFIG["REG_file"]).open("w",encoding="utf-8").write(json.dumps(REG_dict))
    Path(CONFIG["REG_status_file"]).open("w",encoding="utf-8").write(json.dumps(REG_status_dict))
    Path(CONFIG["REG_flag_file"]).open("w",encoding="utf-8").write(json.dumps(REG_flag_dict))

if exists(CONFIG["RAM_file"]) and isfile(CONFIG["RAM_file"]):
    if exists(CONFIG["REG_file"]) and isfile(CONFIG["REG_file"]): 
        if exists(CONFIG["RAM_status_file"]) and isfile(CONFIG["RAM_status_file"]):
            if exists(CONFIG["REG_flag_file"]) and isfile(CONFIG["REG_flag_file"]):
                if exists(CONFIG["REG_status_file"]) and isfile(CONFIG["REG_status_file"]):
                    if exists(CONFIG["STORAGE_dir"]) and isdir(CONFIG["STORAGE_dir"]):
                        RAM_init()
                        REG_init()
                    else:
                        op_stop_os(f"STORAGE folder '{CONFIG["STORAGE_dir"]}' not found.",1)
                else:
                    op_stop_os(f"REG status file '{CONFIG["REG_status_file"]}' not found.",1)
            else:
                op_stop_os(f"REG flag file '{CONFIG["REG_flag_file"]}' not found.",1)
        else:
            op_stop_os(f"RAM status file '{CONFIG["RAM_status_file"]}' not found.",1)
    else:
        op_stop_os(f"REG file '{CONFIG["REG_file"]}' not found.",1)
else:
    op_stop_os(f"RAM file '{CONFIG["RAM_file"]}' not found.",1)

