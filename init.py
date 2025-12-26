import json
from pathlib import Path
from PhseXlib.op_lib import op_stop_os
from os.path import exists,isdir,isfile

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))
RAM_addr_len = len(hex(CONFIG["memory_size"])) if CONFIG["Base"] == 2 else len(CONFIG["memory_size"])
REG_addr_len = len(hex(CONFIG["memory_size"]))

def os_init(base):
    if base == 2:
        RAM_dict = {f"{i:#010x}":0 for i in range(CONFIG["memory_size"])}
        REG_dict = {f"R{str(i)}":0 for i in range(CONFIG["reg_set"]["reg_count"])}
        Path(CONFIG["RAM_file"]).open("w",encoding="utf-8").write(json.dumps(RAM_dict))
        Path(CONFIG["REG_file"]).open("w",encoding="utf-8").write(json.dumps(REG_dict))
    elif base == 10:
        RAM_dict = {f"{i:#010x}":0 for i in range(CONFIG["memory_size"])}
        REG_dict = {f"R{i*CONFIG["reg_set"]["reg_width"]}":0 for i in range(CONFIG["reg_set"]["reg_count"])}
        Path(CONFIG["RAM_file"]).open("w",encoding="utf-8").write(json.dumps(RAM_dict))
        Path(CONFIG["REG_file"]).open("w",encoding="utf-8").write(json.dumps(REG_dict))

if exists(CONFIG["RAM_file"]) and isfile(CONFIG["RAM_file"]):
    if exists(CONFIG["REG_file"]) and isfile(CONFIG["REG_file"]): 
        if exists(CONFIG["RAM_status_file"]) and isfile(CONFIG["RAM_status_file"]):
            if exists(CONFIG["REG_flag_file"]) and isfile(CONFIG["REG_flag_file"]):
                if exists(CONFIG["REG_status_file"]) and isfile(CONFIG["REG_status_file"]):
                    if exists(CONFIG["STORAGE_dir"]) and isdir(CONFIG["STORAGE_dir"]):
                        os_init(2)
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

