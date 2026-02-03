from PhseXlib.locals import CONFIG
import os
from PhseXlib.op_lib import op_wirte_block_to_memory
from os.path import exists, isfile

def read_file(path):
    file_path = os.path.join(CONFIG["STORAGE_dir"],path)
    if exists(file_path) and isfile(file_path):
        