import json
from pathlib import Path
from PhseXlib.op_lib import op_stop_os
from PhseXlib.code_expand import memory_usage_check
import importlib.util
import os
import re

CONFIG = json.load(Path("build.json").open("r", encoding="utf-8"))
args_partten = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
lable_partten = r"^(?!\\d+$).+$"
symbol_table = {}
lable_table = {}
imported_package = {}
process_list = []



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
                    imported_package[code["args"]] = EXPORT
                else:
                    op_stop_os(f"Package {code["args"]} not found in /system/phsex/library.",1,code["args"])
            
            # 定义变量
            elif code["name"] == "POINT":
                args = [a.strip() for a in re.split(args_partten, code['args'])]
                if len(args) >= 2:
                    symbol_table[args[0]] = args[1]
                else:
                    op_stop_os("POINT function needs 2 arguments.",1)
            
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
                    for pkg_name in imported_package:
                        found_function = False
                        if block["name"] in imported_package[pkg_name]:
                            found_function = True
                            args = [a.strip() for a in re.split(args_partten, block['args'])] if block["args"] else []
                            if CONFIG["PhseX"]["data_security_mode"]:
                                security_func = memory_usage_check(imported_package[pkg_name][block["name"]])
                                try:
                                    security_func(*args) # type: ignore
                                except TypeError:
                                    pass # 这NoneType Error是什么鬼东西？？？结果都出来了给我来个报错
                                
                            else:
                                imported_package[pkg_name][block["name"]](*args)
                            break
                        else:
                            continue
                        
                    if found_function: # type: ignore
                        pass
                    else:
                        op_stop_os(f"Function {code["name"]} not found.",1,code["name"])

            
            # 执行全局普通指令
            else:
                for pkg_name in imported_package:
                    found_function = False
                    if code["name"] in imported_package[pkg_name]:
                        found_function = True
                        args = [a.strip() for a in re.split(args_partten, code['args'])] if code["args"] else []
                        if CONFIG["PhseX"]["data_security_mode"]:
                            security_func = memory_usage_check(imported_package[pkg_name][code["name"]](*args))
                            try:
                                security_func(*args)
                            except TypeError:
                                pass # 这NoneType Error是什么鬼东西？？？结果都出来了给我来个报错
                        else:
                            imported_package[pkg_name][code["name"]](*args)
                        break
                    else:
                        continue
                if found_function: # type: ignore
                    pass
                else:
                    op_stop_os(f"Function {code["name"]} not found.",1,code["name"])

        # 标签内部内容收集
        else:
            if code["name"] == "LABLE_END":
                in_lable = False
                current_lable = ""
            else:
                lable_table[current_lable].append(code)