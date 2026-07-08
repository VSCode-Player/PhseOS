import importlib.util
from PhseXlib.locals import CONFIG
import os

file_op_path = os.path.join(CONFIG["PhseX_library"],"FileIO","file_op.py")
file_spec = importlib.util.spec_from_file_location("file_op", file_op_path)
file_module = importlib.util.module_from_spec(file_spec) # type: ignore
file_spec.loader.exec_module(file_module) # type: ignore

EXPORT = {
    "create_file":file_module.create_file,
    "write_file":file_module.write_file
}