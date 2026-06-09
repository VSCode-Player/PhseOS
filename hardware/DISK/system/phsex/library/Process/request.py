from PhseXlib.op_lib import op_write
from pathlib import Path
from PhseXlib.locals import CONFIG
from PhseXlib.addres import addres_transformer
from phsex import process_list
import json

def request_memory(size,pid):
    requested_memory = []
    memroy_dict:dict = json.load(Path(CONFIG["RAM_file"]).open("r",encoding="utf-8"))
    memory_status_dict:dict = json.load(Path(CONFIG["RAM_status_file"]).open("r",encoding="utf-8"))
    for i in memroy_dict.keys():
        if memory_status_dict[i] == "free" and len(requested_memory) < int(size):
            requested_memory.append(i)
            RAM_status_file_dict = addres_transformer(i)
            RAM_status_file_dict["file"] = CONFIG["RAM_status_file"]
            op_write(f"{pid}-allocated",RAM_status_file_dict)

def create_process(lable,enable_data_security_mode):
    # lable_dict = addres_transformer(lable)

    process_id = process_list[-1][0]+1 if process_list else 0
    process_list.append({"PID":process_id,"lable_name":lable,"data_security_mode":enable_data_security_mode})