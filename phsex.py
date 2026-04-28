import json
from pathlib import Path
import importlib.util
import os
import re

CONFIG = json.load(Path("build.json").open("r", encoding="utf-8"))
args_partten = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
lable_partten = r"^(?!\\d+$).+$"
symbol_table = {}
lable_table = {}
imported_package = []

def run_code(file):
    CODE = Path(file).open("r", encoding="utf-8").read()
    code_line = CODE.split("\n")

    code_list = []
    in_lable = False
    current_lable = ""

    # 第一步：解析所有代码行
    for line in code_line:
        line = line.strip()
        if not line:
            continue
        
        code_block_dict = {}
        if " " in line:
            code_block_dict["name"] = line[:line.find(" ")].lstrip()
            code_block_dict["args"] = line[line.find(" "):].lstrip()
        else:
            code_block_dict["name"] = line
            code_block_dict["args"] = ""
        code_list.append(code_block_dict)

    # 第二步：构建标签表 + 执行全局指令
    for code in code_list:
        if not in_lable:
            # 加载库
            if code["name"] == "LOAD":
                pack_path = os.path.join(CONFIG["STORAGE_dir"], "system/phsex/library", code["args"])
                pkg_file = os.path.join(pack_path, "package.py")
                if os.path.exists(pkg_file):
                    spec = importlib.util.spec_from_file_location(code["args"], pkg_file)
                    mod = importlib.util.module_from_spec(spec) # type: ignore
                    spec.loader.exec_module(mod) # type: ignore
                    EXPORT = mod.EXPORT
                    imported_package.append(EXPORT)
            
            # 定义变量
            elif code["name"] == "POINT":
                args = [a.strip() for a in re.split(args_partten, code['args'])]
                if len(args) >= 2:
                    symbol_table[args[0]] = args[1]
            
            # 开始定义标签
            elif code["name"] == "LABLE" and not code["args"].strip().isdigit():
                in_lable = True
                current_lable = code["args"].strip().rstrip(":")
                lable_table[current_lable] = []
            
            # 调用标签（核心：支持 BREAK 提前退出）
            elif code["name"] in lable_table:
                break_flag = False  # 中断标记
                for block in lable_table[code["name"]]:
                    # 触发 BREAK，直接结束标签执行
                    if break_flag:
                        break
                    
                    # 识别 BREAK 指令
                    if block["name"] == "BREAK":
                        break_flag = True
                        continue

                    # 执行库函数
                    for pkg in imported_package:
                        if block["name"] in pkg:
                            args = [a.strip() for a in re.split(args_partten, block['args'])] if block["args"] else []
                            pkg[block["name"]](*args)
                            break
            
            # 执行全局普通指令
            else:
                for pkg in imported_package:
                    if code["name"] in pkg:
                        args = [a.strip() for a in re.split(args_partten, code['args'])] if code["args"] else []
                        pkg[code["name"]](*args)
                        break

        # 标签内部内容收集
        else:
            if code["name"] == "LABLE_END":
                in_lable = False
                current_lable = ""
            else:
                lable_table[current_lable].append(code)