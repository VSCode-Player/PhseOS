from init import init,CONFIG
from phsex import *
from os.path import join

init() # 初始化系统环境
file_path = join(CONFIG["STORAGE_dir"],"home","main.phx")
run_code(file_path) # 运行主程序

if CONFIG["PhseX"]["debug_mode"]:
    print("\n-------------Debug Message------------")
    print(f"进程列表:{process_list}")
    print(f"链接表:{symbol_table}")
    print(f"标签列表:{label_table}")
    print(f"导入的模块:{imported_package}")