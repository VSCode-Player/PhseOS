from PhseXlib.locals import CONFIG
from PhseXlib.op_lib import op_stop_os
import os

STORAGE_PATH = os.path.abspath(CONFIG["STORAGE_dir"])

def create_file(path):
    if not os.path.exists(os.path.join(STORAGE_PATH,path)):
        with open(os.path.join(STORAGE_PATH,path),"w",encoding="utf-8") as file:
            file.write("")
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} exists.",1,os.path.join(STORAGE_PATH,path))

def write_file(path,content):
    if os.path.exists(os.path.join(STORAGE_PATH,path)):
        with open(os.path.join(STORAGE_PATH,path),"w",encoding="utf-8") as file:
            file.write(content)
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} does not exists.",1,os.path.join(STORAGE_PATH,path))
