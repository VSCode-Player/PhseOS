import importlib.util
import os
from PhseXlib.locals import CONFIG

file_op_path = os.path.join(CONFIG["PhseX_library"],"FileIO","file_op.py")
file_op_spec = importlib.util.spec_from_file_location("file_op",file_op_path)
file_op_module = importlib.util.module_from_spec(file_op_spec) # type: ignore
file_op_spec.loader.exec_module(file_op_module) # type: ignore

EXPORT = {
    "CRT_F":file_op_module.create_file,
    "DEL_F":file_op_module.delete_file,
    "WRT_F":file_op_module.write_file,
}