import json
from pathlib import Path
import importlib.util
import os
import re

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))
args_partten = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
symbol_table = {}

def run_code(file):
    CODE = Path(file).open("r",encoding="utf-8").read()

    code_line = CODE.split("\n")
    imported_package = []
    code_list = []

    for line in code_line:
        code_block_dict = {}
        if " " in line:
            code_block_dict["name"] = line[:line.find(" ")].lstrip()
            code_block_dict["args"] = line[line.find(" "):].lstrip()
        else:
            code_block_dict["name"] = line
            code_block_dict["args"] = ""
        code_list.append(code_block_dict)

    for code in code_list:
        if code["name"] == "LOAD":
            pack_path = os.path.join(CONFIG["STORAGE_dir"],
                                     "system/phsex/library", code["args"])
            pkg_file = os.path.join(pack_path, "package.py")
            if os.path.exists(pkg_file):
                # 动态加载 .py
                spec = importlib.util.spec_from_file_location(code["args"], pkg_file)
                mod = importlib.util.module_from_spec(spec) # type: ignore
                spec.loader.exec_module(mod) # type: ignore
                EXPORT = mod.EXPORT          # 拿到字典
                imported_package.append(EXPORT)   # 如果后面要调用函数，存字典即可
        elif code["name"] == "POINT":
            args = [a.strip() for a in re.split(args_partten, code['args'])]
            symbol_table[args[0]] = args[1]  # 直接存 name: addr
        else:
            for i in imported_package:
                if code["name"] in i:
                    args = [a.strip() for a in re.split(args_partten, code['args'])]
                    i[code["name"]](*args)