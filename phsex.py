import json
from pathlib import Path
import importlib.util
import os

CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))
CODE = Path("main.phx").open("r",encoding="utf-8").read()

code_line = CODE.split("\n")
imported_package = []
code_list = []

for line in code_line:
    code_list.append(
        {
            "name":line[:line.find(" ")].lstrip(), 
            "args":line[line.find(" "):].lstrip()
            })
    
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
    else:
        for i in imported_package:
            if code["name"] in i:
                args = code["args"].split(",")
                i[code["name"]](*args)