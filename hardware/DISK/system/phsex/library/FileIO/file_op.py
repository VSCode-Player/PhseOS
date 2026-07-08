from PhseXlib.locals import CONFIG
from PhseXlib.op_lib import op_stop_os
from PhseXlib.addres import addres_transformer,get_value
import os

STORAGE_PATH = os.path.abspath(CONFIG["STORAGE_dir"])

def create_file(path):
    if not os.path.exists(os.path.join(STORAGE_PATH,path)):
        with open(os.path.join(STORAGE_PATH,path),"w",encoding="utf-8") as file:
            file.write("")
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} exists.",1,os.path.join(STORAGE_PATH,path))

def write_file(path,content):
    content_dict:dict = addres_transformer(content)
    if os.path.exists(os.path.join(STORAGE_PATH,path)):
        with open(os.path.join(STORAGE_PATH,path),"w",encoding="utf-8") as file:
            file.write(get_value(content_dict)) # type: ignore
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} does not exists.",1,os.path.join(STORAGE_PATH,path))

def delete_file(path):
    if os.path.exists(os.path.join(STORAGE_PATH,path)):
        os.remove(os.path.join(STORAGE_PATH,path))
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} does not exists.",1,os.path.join(STORAGE_PATH,path))

def create_dir(path):
    if not os.path.exists(os.path.join(STORAGE_PATH,path)):
        os.mkdir(os.path.join(STORAGE_PATH,path))
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} exists.",1,os.path.join(STORAGE_PATH,path))

def delete_dir(path):
    if os.path.exists(os.path.join(STORAGE_PATH,path)):
        os.rmdir(os.path.join(STORAGE_PATH,path))
    else:
        op_stop_os(f"{os.path.join(STORAGE_PATH,path)} does not exists.",1,os.path.join(STORAGE_PATH,path))