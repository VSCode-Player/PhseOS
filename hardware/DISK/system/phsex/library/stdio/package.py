import importlib.util
from PhseXlib.locals import CONFIG
import os

# CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

# 导入基本数学运算模块
math_op_path = os.path.join(CONFIG["PhseX_library"],"stdio","math_op.py")
math_spec = importlib.util.spec_from_file_location("math_op", math_op_path)
math_module = importlib.util.module_from_spec(math_spec) # type: ignore
math_spec.loader.exec_module(math_module) # type: ignore

# 导入基本数据操控模块
data_op_path = os.path.join(CONFIG["PhseX_library"],"stdio","data_op.py")
data_spec = importlib.util.spec_from_file_location("data_op",data_op_path)
data_module = importlib.util.module_from_spec(data_spec) # type: ignore
data_spec.loader.exec_module(data_module) # type: ignore

# 导入基本输出模块
output_op_path = os.path.join(CONFIG["PhseX_library"],"stdio","output_op.py")
output_spec = importlib.util.spec_from_file_location("output_op",output_op_path)
output_module = importlib.util.module_from_spec(output_spec) # type: ignore
output_spec.loader.exec_module(output_module) # type: ignore

EXPORT = {
    "ADD":math_module.add,
    "SUB":math_module.sub,
    "MUL":math_module.mul,
    "DIV":math_module.div,
    "SHL":data_module.left_shift,
    "SHR":data_module.right_shift,
    "MOV":data_module.mov,
    "SEF":data_module.set_flag,
    "MSG":output_module.msg,
}