import phsex
from init import init,CONFIG
from phsex import run_code
from os.path import join

init() # 初始化系统环境
file_path = join(CONFIG["STORAGE_dir"],"home","main.phx")
run_code(file_path) # 运行主程序