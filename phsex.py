import json
from pathlib import Path
import importlib.util
import os
import re

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))
args_partten = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
lable_partten = r"^(?!\\d+$).+$"
symbol_table = {}
lable_table = {}
imported_package = []

def run_code(file):
    CODE = Path(file).open("r",encoding="utf-8").read()

    code_line = CODE.split("\n")
    
    code_list = []
    in_lable = False
    current_lable = ""

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
        if not in_lable:
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
            elif code["name"] == "LABLE" and not code["args"].strip().isdigit():
                in_lable = True
                current_lable = code["args"][:-1]
                lable_table[code["args"][:-1]] = []
            elif code["name"] in lable_table:
                # 标签调用，执行标签内代码块
                for block in lable_table[code["name"]]:
                    if block["name"] == "LABLE_END":
                        break
                    elif block["name"] in imported_package[0]:
                        args = [a.strip() for a in re.split(args_partten, block['args'])]
                        imported_package[0][block["name"]](*args)
                    elif block["name"] == "POINT":
                        args = [a.strip() for a in re.split(args_partten, block['args'])]
                        symbol_table[args[0]] = args[1]  # 直接存 name: addr
            else:
                for i in imported_package:
                    if code["name"] in i:
                        args = [a.strip() for a in re.split(args_partten, code['args'])]
                        i[code["name"]](*args)
        else:
            lable_table[current_lable].append(code)
            if code["name"] == "LABLE_END":
                in_lable = False
                lable_table[current_lable].remove(code)
                current_lable = ""