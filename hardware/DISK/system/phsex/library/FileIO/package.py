"""FileIO 包入口：把 file_op.py 里的系统调用注册成 PhseX 指令。

指令名统一使用“大写下划线”风格，与 stdio 包的 ADD/MOV/MSG 保持一致；
同时保留一套小写别名，旧版 .phx 里的 `create_file path` 写法仍然可用。
"""

import importlib.util
from PhseXlib.locals import CONFIG
import os

file_op_path = os.path.join(CONFIG["PhseX_library"], "FileIO", "file_op.py")
file_spec = importlib.util.spec_from_file_location("file_op", file_op_path)
file_module = importlib.util.module_from_spec(file_spec)  # type: ignore
file_spec.loader.exec_module(file_module)  # type: ignore

# 指令名 -> file_op 中的函数名
COMMANDS = {
    # 文件
    "CREATE_FILE": "create_file",
    "TOUCH_FILE": "touch_file",
    "WRITE_FILE": "write_file",
    "APPEND_FILE": "append_file",
    "READ_FILE": "read_file",
    "READ_LINES": "read_lines",
    "DELETE_FILE": "delete_file",
    "COPY_FILE": "copy_file",
    "MOVE_FILE": "move_file",
    "RENAME_FILE": "rename_file",
    "TRUNCATE_FILE": "truncate_file",
    "FILE_SIZE": "file_size",
    "FILE_EXISTS": "file_exists",
    "FILE_TYPE": "file_type",
    "FILE_INFO": "file_info",
    # 目录
    "CREATE_DIR": "create_dir",
    "DELETE_DIR": "delete_dir",
    "COPY_DIR": "copy_dir",
    "DIR_EXISTS": "dir_exists",
    "LIST_DIR": "list_dir",
    # 描述符 IO
    "OPEN_FILE": "open_file",
    "CLOSE_FILE": "close_file",
    "READ_FD": "read_fd",
    "READ_LINE": "read_line",
    "WRITE_FD": "write_fd",
    "SEEK_FD": "seek_fd",
    "TELL_FD": "tell_fd",
    "LIST_FD": "list_fds",
}

EXPORT = {name: getattr(file_module, func) for name, func in COMMANDS.items()}

# 兼容旧接口：小写函数名和原始写法都能继续调用
for _name, _func in COMMANDS.items():
    EXPORT[_func] = EXPORT[_name]
