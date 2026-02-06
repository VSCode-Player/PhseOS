from PhseXlib.locals import *
from pathlib import Path
from PhseXlib.op_lib import op_stop_os, op_string_format
import os

root_path = CONFIG["STORAGE_dir"]

def create_file(*args):
    # 如果参数长度小于1，则报错，否则将文件名设为第一个参数
    file_name = args[0] if len(args) > 0 else op_stop_os("CRT_F need 1 argument(s)",1)
    # 如果参数长度小于2，则创建在根目录下，否则在指定目录下创建
    file_path = Path(root_path) / args[1] / file_name if len(args) > 1 else Path(root_path) / file_name 
    try:
        Path(file_path).open("w")
    except FileNotFoundError:
        os.makedirs(Path(file_path).parent,exist_ok=True)
        Path(file_path).open("w")

def create_dir(*args):
    # 如果参数长度小于1，则报错，否则将目录名设为第一个参数
    dir_name = args[0] if len(args) > 0 else op_stop_os("CRT_D need 1 argument(s)",1)
    # 如果参数长度小于2，则创建在根目录下，否则在指定目录下创建
    dir_path = Path(root_path) / args[1] / dir_name if len(args) > 1 else Path(root_path) / dir_name 
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        op_stop_os("directory already exists",1)

def delete_file(file_path):
    path = Path(root_path) / file_path
    if os.path.exists(path):
        os.remove(path)
    else:
        op_stop_os("file not found",1)

def delete_dir(dir_path):
    path = Path(root_path) / dir_path
    if os.path.exists(path):
        os.removedirs(path)
    else:
        op_stop_os("directory not found",1)

def write_file(data, file_path, mode):
    '''
    :param data: 写入的数据
    :param file_path: 文件路径
    :param mode: 写入模式
    '''
    path = Path(root_path) / file_path
    if os.path.exists(path):
        if mode == "w":
            Path(path).open("w").write(op_string_format(data[1:-1]))
        elif mode == "a":
            Path(path).open("a").write(op_string_format(data[1:-1]))
        else:
            op_stop_os("invalid mode",1)
    else:
        op_stop_os("file not found",1)