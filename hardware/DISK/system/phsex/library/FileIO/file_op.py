"""PhseOS FileIO —— 完整的文件 IO 系统调用库

本模块把 PhseOS 的“磁盘”（hardware/DISK 目录）包装成一个以小目录为根的
文件系统，供 .phx 程序在 `LOAD FileIO` 之后直接调用。

虚拟路径
--------
所有路径都相对于 CONFIG["STORAGE_dir"]（默认 hardware/DISK）：

    "/"             磁盘根目录
    "/home/a.txt"   ->  hardware/DISK/home/a.txt
    "home/a.txt"    同上（开头有没有 "/" 都可以）

路径中出现 ".."、指向磁盘之外、或者本身是符号链接时一律拒绝，
保证 .phx 程序不会跑到宿主机上读写别的文件。

参数约定
--------
PhseX 会把每条指令按逗号切成字符串参数，因此：

* 路径、内容、模式等文本参数建议用双引号包裹，例如 `"/home/a.txt"`；
  支持 \\n \\t \\r \\b \\0 \\" \\\\ 这些转义。
* 内容参数也可以直接写整数（`65`）、寄存器（`R0`）、内存（`0x00000005`）
  或指针（`[PTR]`），模块会按“文本”语义取值（8 位二进制会转成十进制）。
* 布尔参数接受 TRUE/FALSE、1/0、YES/NO、ON/OFF。

错误处理
--------
与其它 PhseX 模块保持一致：致命错误（路径非法、目标不存在、读写失败）
统一走 op_stop_os 停机；可预期的“存在/不存在”则通过返回 0/1 表示。
"""

import datetime
import fnmatch
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from PhseXlib.locals import CONFIG, CHAR_TO_BIN, INT_TO_BIN
from PhseXlib.op_lib import op_data_transform, op_stop_os, op_write
from PhseXlib.addres import address_transformer, is_address, load_addr_file

STORAGE_PATH = os.path.abspath(CONFIG["STORAGE_dir"])
STATUS_FILE_NAME = "status.json"

_ESCAPE_MAP = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "b": "\b",
    "0": "\0",
    '"': '"',
    "\\": "\\",
}
_STRING_LITERAL = re.compile(r'"([^"\\]|\\.)*"')
_UINT = re.compile(r"[0-9]+")
_BIN8 = re.compile(r"[01]{8}")
_TRUE_WORDS = {"1", "true", "yes", "y", "on", "enable", "enabled"}
_FALSE_WORDS = {"0", "false", "no", "n", "off", "disable", "disabled", "none"}

# 打开的文件描述符表：fd -> {"handle": TextIOWrapper, "path": Path, "mode": str}
_FD_TABLE: dict = {}


# ------------------------------------------------------------------ 内部工具

def _fatal(message, *args):
    """致命错误：打印原因并停机，保证 .phx 不会带着坏状态继续跑。"""
    op_stop_os(message, 1, error_args=", ".join(str(a) for a in args) if args else "")


def _decode_string_literal(text):
    """把 PhseX 层的字符串字面量 '"abc\\n"' 还原成真实文本；非字面量原样返回。"""
    if not (isinstance(text, str) and len(text) >= 2 and text[0] == '"' and text[-1] == '"'):
        return text
    body = text[1:-1]
    result = []
    index = 0
    while index < len(body):
        char = body[index]
        if char == "\\" and index + 1 < len(body):
            result.append(_ESCAPE_MAP.get(body[index + 1], body[index + 1]))
            index += 2
        else:
            result.append(char)
            index += 1
    return "".join(result)


def _plain_text(operand):
    """把参数当作纯文本处理：去引号、还原转义，不做地址解析。"""
    if operand is None:
        return ""
    return _decode_string_literal(str(operand).strip())


def _read_cell(route, operand=""):
    """读取一次地址（寄存器 / 内存 / 标志位）里存的值。"""
    data = load_addr_file(route)
    if route["key"] not in data:
        _fatal(f"Key '{route['key']}' not found in '{route['file']}'.", operand)
    return data[route["key"]]


def _address_to_text(value):
    """把内存单元里的值转成文本：8 位二进制按十进制解释，其余原样输出。"""
    if isinstance(value, str) and _BIN8.fullmatch(value):
        return str(int(value, 2))
    return str(value)


def _point_route(operand):
    """解析指针 [NAME]，返回它真正指向的地址。"""
    from phsex import symbol_table

    route = address_transformer(operand)
    name = route["key"]
    if name not in symbol_table:
        _fatal(f"Point [{name}] is not defined in symbol table.", operand)
    return address_transformer(symbol_table[name])


def _operand_to_text(operand):
    """把内容参数解析成要写进文件的文本。"""
    text = str(operand).strip() if operand is not None else ""
    if not text:
        _fatal("Content argument is empty.")

    if _STRING_LITERAL.fullmatch(text):
        return _decode_string_literal(text)
    if _UINT.fullmatch(text):
        return text

    route = address_transformer(text)
    if not route.get("file"):
        _fatal(f"Invalid content argument '{text}'.", text)
    if route["file"] == "TYPE:POINT":
        route = _point_route(text)
    if route["file"] == "TYPE:STRING":
        return route["key"]
    if route["file"] == "TYPE:INT":
        return str(int(route["key"]))
    if is_address(route):
        return _address_to_text(_read_cell(route, text))

    _fatal(f"Unsupported content argument '{text}'.", text)


def _operand_to_int(operand):
    """把参数解析成整数（供长度、偏移、尺寸等使用）。"""
    text = _operand_to_text(operand).strip()
    try:
        return int(text, 10)
    except ValueError:
        _fatal(f"'{operand}' is not an integer.", operand)


def _operand_to_bool(operand, default=False):
    """把参数解析成布尔值。"""
    if operand is None:
        return default
    text = _plain_text(operand).strip().lower()
    if not text:
        return default
    if text in _TRUE_WORDS:
        return True
    if text in _FALSE_WORDS:
        return False
    _fatal(f"'{operand}' is not a boolean (use TRUE/FALSE or 1/0).", operand)


def _virtual_path(operand, allow_root=False):
    """把虚拟路径解析成宿主机上的绝对路径，并做越界检查。"""
    text = _plain_text(operand)
    if not text:
        _fatal("Path argument is empty.")
    if "\x00" in text:
        _fatal("Path contains a NUL byte.", text)

    normalized = text.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        _fatal(f"Path '{text}' must not contain '..'.", text)
    if not parts and not allow_root:
        _fatal("Path must not point to the storage root.", text)

    full = os.path.abspath(os.path.join(STORAGE_PATH, *parts) if parts else STORAGE_PATH)
    try:
        inside = os.path.commonpath([full, STORAGE_PATH]) == STORAGE_PATH
    except ValueError:
        inside = False
    if not inside:
        _fatal(f"Path '{text}' escapes the storage directory.", text)
    if os.path.islink(full):
        _fatal(f"Path '{text}' is a symbolic link, which is not allowed.", text)
    return Path(full)


def _virtual_name(path):
    """把宿主机绝对路径转回虚拟路径，用于输出更友好的信息。"""
    relative = os.path.relpath(str(path), STORAGE_PATH).replace(os.sep, "/")
    return "/" if relative == "." else "/" + relative


def _file_path(operand):
    """解析一个必须存在且是普通文件的路径。"""
    path = _virtual_path(operand)
    if not path.exists():
        _fatal(f"{_virtual_name(path)} does not exist.", operand)
    if path.is_dir():
        _fatal(f"{_virtual_name(path)} is a directory, not a file.", operand)
    return path


def _dir_path(operand, allow_root=True):
    """解析一个必须存在且是目录的路径。"""
    path = _virtual_path(operand, allow_root=allow_root)
    if not path.exists():
        _fatal(f"{_virtual_name(path)} does not exist.", operand)
    if not path.is_dir():
        _fatal(f"{_virtual_name(path)} is not a directory.", operand)
    return path


def _atomic_write(path, text):
    """原子写入：先写临时文件再改名，避免掉电/中断留下半截文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".phse-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _target_route(operand):
    """解析一个可写地址（寄存器 / 内存 / 指针）。"""
    text = str(operand).strip() if operand is not None else ""
    if not text:
        _fatal("Target address is empty.")
    route = address_transformer(text)
    if not route.get("file"):
        _fatal(f"Invalid target address '{text}'.", text)
    if route["file"] == "TYPE:POINT":
        route = _point_route(text)
    if not is_address(route):
        _fatal(f"Target '{text}' must be a register, memory address or point.", text)
    return route


def _memory_cells(route, count):
    """从起始地址往后取 count 个连续单元，空间不足则停机。"""
    keys = list(load_addr_file(route).keys())
    if route["key"] not in keys:
        _fatal(f"Key '{route['key']}' not found in '{route['file']}'.")
    start = keys.index(route["key"])
    cells = keys[start:start + count]
    if len(cells) < count:
        _fatal(f"Not enough continuous space: need {count} cell(s), only {len(cells)} left.")
    return cells


def _mark_used(route, keys):
    """把写入过的单元在 status.json 里标记为 used（文件不存在则跳过）。"""
    status_path = os.path.join(os.path.dirname(route["file"]), STATUS_FILE_NAME)
    try:
        if not os.path.isfile(status_path):
            return
        data = json.loads(Path(status_path).read_text(encoding="utf-8"))
        changed = False
        for key in keys:
            if key in data and data[key] != "used":
                data[key] = "used"
                changed = True
        if changed:
            temp = status_path + ".tmp"
            Path(temp).write_text(json.dumps(data), encoding="utf-8")
            os.replace(temp, status_path)
    except (OSError, ValueError):
        # 状态文件只用于调试，标记失败不应该影响读写本身
        pass


def _store_text(text, target_operand):
    """把文本按 PhseEncode 编码后逐字符写入连续的内存/寄存器单元。"""
    route = _target_route(target_operand)
    codes = []
    for char in text:
        code = op_data_transform(char, CHAR_TO_BIN)
        if not (isinstance(code, str) and _BIN8.fullmatch(code)):
            _fatal(f"Character {char!r} is not in the PhseEncode charset.", char)
        codes.append(code)
    cells = _memory_cells(route, len(codes))
    for code, key in zip(codes, cells):
        op_write(code, {"file": route["file"], "key": key})
    _mark_used(route, cells)
    return route


def _store_value(value, target_operand):
    """把一个整数按 8 位二进制写入地址。"""
    op_write(op_data_transform(int(value), INT_TO_BIN), _target_route(target_operand))


def _fd_entry(fd_operand):
    fd = _operand_to_int(fd_operand)
    if fd not in _FD_TABLE:
        _fatal(f"File descriptor {fd} is not open.", fd_operand)
    return fd, _FD_TABLE[fd]


# ------------------------------------------------------------------ 文件操作

def create_file(path):
    """CREATE_FILE <path> —— 新建空文件；文件已存在时报错。"""
    target = _virtual_path(path)
    if target.exists():
        _fatal(f"{_virtual_name(target)} already exists.", path)
    try:
        _atomic_write(target, "")
    except OSError as exc:
        _fatal(f"Cannot create {_virtual_name(target)}: {exc}", path)


def touch_file(path):
    """TOUCH_FILE <path> —— 文件不存在则创建，存在则刷新修改时间。"""
    target = _virtual_path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
    except OSError as exc:
        _fatal(f"Cannot touch {_virtual_name(target)}: {exc}", path)


def write_file(path, content, mode=None):
    """WRITE_FILE <path>, <content>[, <mode>]

    mode: "w" 覆盖（默认）、"a" 追加、"x" 仅当文件不存在时创建。
    父目录不存在会自动创建。
    """
    target = _virtual_path(path)
    text = _operand_to_text(content)
    mode_text = (_plain_text(mode) or "w").lower()

    if target.is_dir():
        _fatal(f"{_virtual_name(target)} is a directory, not a file.", path)

    try:
        if mode_text in ("w", "write", "overwrite", "truncate"):
            _atomic_write(target, text)
        elif mode_text in ("a", "append"):
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "a", encoding="utf-8", newline="") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
        elif mode_text in ("x", "exclusive", "create"):
            if target.exists():
                _fatal(f"{_virtual_name(target)} already exists.", path)
            _atomic_write(target, text)
        else:
            _fatal(f"Unsupported write mode '{mode_text}' (use w/a/x).", mode)
    except OSError as exc:
        _fatal(f"Cannot write {_virtual_name(target)}: {exc}", path)


def append_file(path, content):
    """APPEND_FILE <path>, <content> —— 在文件末尾追加内容（不存在则创建）。"""
    write_file(path, content, "a")


def read_file(path, target=None, mode=None):
    """READ_FILE <path>[, <target>[, <mode>]]

    * 不给 target：直接把文件内容打印到屏幕（类似 cat）。
    * 给 target 且 mode=STR（默认）：把文本按 PhseEncode 逐字符写进
      从 target 开始的连续单元（每格一个字节）。
    * 给 target 且 mode=INT：把文件里的整数写成 8 位二进制写入 target。
    """
    source = _file_path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        _fatal(f"{_virtual_name(source)} is not a UTF-8 text file.", path)

    target_text = _plain_text(target)
    if not target_text:
        print(text, end="")
        return

    mode_text = (_plain_text(mode) or "STR").upper()
    if mode_text == "INT":
        try:
            value = int(text.strip(), 10)
        except ValueError:
            _fatal(f"{_virtual_name(source)} does not contain an integer.", path)
        _store_value(value, target_text)
    elif mode_text == "STR":
        _store_text(text, target_text)
    else:
        _fatal(f"Unsupported read mode '{mode_text}' (use STR/INT).", mode)


def read_lines(path, start="1", count=None):
    """READ_LINES <path>[, <start>[, <count>]] —— 按行读取（行号从 1 开始）。"""
    source = _file_path(path)
    try:
        lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        _fatal(f"{_virtual_name(source)} is not a UTF-8 text file.", path)

    start_line = max(_operand_to_int(start), 1)
    selected = lines[start_line - 1:]
    count_text = _plain_text(count)
    if count_text:
        count_int = _operand_to_int(count_text)
        if count_int < 0:
            _fatal(f"Line count must not be negative: {count_int}.", count)
        selected = selected[:count_int]
    print("".join(selected), end="")


def delete_file(path):
    """DELETE_FILE <path> —— 删除文件。"""
    target = _file_path(path)
    try:
        os.remove(target)
    except OSError as exc:
        _fatal(f"Cannot delete {_virtual_name(target)}: {exc}", path)


def copy_file(src, dst, overwrite=None):
    """COPY_FILE <src>, <dst>[, <overwrite>] —— 复制文件（保留元数据）。"""
    source = _file_path(src)
    target = _virtual_path(dst)

    if os.path.abspath(target) == os.path.abspath(source):
        _fatal("Source and destination are the same file.", src)
    if target.exists():
        if target.is_dir():
            _fatal(f"{_virtual_name(target)} is a directory, not a file.", dst)
        if not _operand_to_bool(overwrite):
            _fatal(f"{_virtual_name(target)} already exists (set overwrite=TRUE).", dst)

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    except OSError as exc:
        _fatal(f"Cannot copy {_virtual_name(source)} -> {_virtual_name(target)}: {exc}", src, dst)


def move_file(src, dst, overwrite=None):
    """MOVE_FILE <src>, <dst>[, <overwrite>] —— 移动/重命名文件。"""
    source = _file_path(src)
    target = _virtual_path(dst)

    if os.path.abspath(target) == os.path.abspath(source):
        _fatal("Source and destination are the same file.", src)
    if target.exists():
        if target.is_dir():
            _fatal(f"{_virtual_name(target)} is a directory, not a file.", dst)
        if not _operand_to_bool(overwrite):
            _fatal(f"{_virtual_name(target)} already exists (set overwrite=TRUE).", dst)

    try:
        if target.exists():
            os.remove(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
    except OSError as exc:
        _fatal(f"Cannot move {_virtual_name(source)} -> {_virtual_name(target)}: {exc}", src, dst)


def rename_file(src, dst, overwrite=None):
    """RENAME_FILE <src>, <dst>[, <overwrite>] —— MOVE_FILE 的别名。"""
    move_file(src, dst, overwrite)


def truncate_file(path, size=None):
    """TRUNCATE_FILE <path>[, <size>] —— 把文件截断/补零到 size 字节（默认 0）。

    按字节计算，文件不存在时按 POSIX 语义创建空文件。
    """
    target = _virtual_path(path)
    size_int = 0 if _plain_text(size) == "" else _operand_to_int(size)
    if size_int < 0:
        _fatal(f"File size must not be negative: {size_int}.", size)
    if target.is_dir():
        _fatal(f"{_virtual_name(target)} is a directory, not a file.", path)

    try:
        if not target.exists():
            _atomic_write(target, "")
        os.truncate(target, size_int)
    except OSError as exc:
        _fatal(f"Cannot truncate {_virtual_name(target)}: {exc}", path)


def file_size(path, target=None):
    """FILE_SIZE <path>[, <target>] —— 输出文件字节数（屏幕或写入地址）。"""
    size = _file_path(path).stat().st_size
    if _plain_text(target):
        _store_value(size, target)
    else:
        print(size)


def file_exists(path, target=None):
    """FILE_EXISTS <path>[, <target>] —— 存在返回 1，否则 0。"""
    exists = _virtual_path(path).exists()
    if _plain_text(target):
        _store_value(1 if exists else 0, target)
    else:
        print(1 if exists else 0)


def dir_exists(path, target=None):
    """DIR_EXISTS <path>[, <target>] —— 目录存在返回 1，否则 0。"""
    exists = _virtual_path(path, allow_root=True).is_dir()
    if _plain_text(target):
        _store_value(1 if exists else 0, target)
    else:
        print(1 if exists else 0)


def file_type(path):
    """FILE_TYPE <path> —— 输出 FILE / DIR / NONE。"""
    target = _virtual_path(path, allow_root=True)
    if not target.exists():
        print("NONE")
    elif target.is_dir():
        print("DIR")
    else:
        print("FILE")


def file_info(path):
    """FILE_INFO <path> —— 输出路径、类型、大小、时间戳和权限。"""
    target = _virtual_path(path, allow_root=True)
    if not target.exists():
        _fatal(f"{_virtual_name(target)} does not exist.", path)

    info = target.stat()
    kind = "DIR" if target.is_dir() else "FILE"

    def _time(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    print(f"Path      : {_virtual_name(target)}")
    print(f"Type      : {kind}")
    print(f"Size      : {info.st_size} B")
    print(f"Created   : {_time(info.st_ctime)}")
    print(f"Modified  : {_time(info.st_mtime)}")
    print(f"Accessed  : {_time(info.st_atime)}")
    print(f"Mode      : {oct(info.st_mode)[-4:]}")


# ------------------------------------------------------------------ 目录操作

def create_dir(path, recursive=None):
    """CREATE_DIR <path>[, <recursive>] —— 新建目录（recursive=TRUE 时逐级创建）。"""
    target = _virtual_path(path)
    if target.exists():
        _fatal(f"{_virtual_name(target)} already exists.", path)

    try:
        if _operand_to_bool(recursive):
            target.mkdir(parents=True)
        else:
            target.mkdir()
    except FileNotFoundError:
        _fatal(f"Parent directory of {_virtual_name(target)} does not exist (use recursive=TRUE).", path)
    except OSError as exc:
        _fatal(f"Cannot create directory {_virtual_name(target)}: {exc}", path)


def delete_dir(path, recursive=None):
    """DELETE_DIR <path>[, <recursive>] —— 删除目录（recursive=TRUE 时递归删除）。"""
    target = _dir_path(path, allow_root=False)

    try:
        if _operand_to_bool(recursive):
            shutil.rmtree(target)
        else:
            os.rmdir(target)
    except OSError as exc:
        _fatal(
            f"Cannot remove {_virtual_name(target)}: {exc} "
            f"(use recursive=TRUE for a non-empty directory).",
            path,
        )


def copy_dir(src, dst, overwrite=None):
    """COPY_DIR <src>, <dst>[, <overwrite>] —— 递归复制目录。"""
    source = _dir_path(src, allow_root=False)
    target = _virtual_path(dst)

    if os.path.abspath(target) == os.path.abspath(source):
        _fatal("Source and destination are the same directory.", src)
    if target.exists():
        if not _operand_to_bool(overwrite):
            _fatal(f"{_virtual_name(target)} already exists (set overwrite=TRUE).", dst)

    try:
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                os.remove(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
    except OSError as exc:
        _fatal(f"Cannot copy {_virtual_name(source)} -> {_virtual_name(target)}: {exc}", src, dst)


def list_dir(path="/", pattern=None):
    """LIST_DIR <path>[, <pattern>] —— 列出目录内容，支持通配符（如 "*.phx"）。"""
    directory = _dir_path(path)
    pattern_text = _plain_text(pattern)

    entries = [entry for entry in directory.iterdir()
               if not pattern_text or fnmatch.fnmatch(entry.name, pattern_text)]
    entries.sort(key=lambda entry: (not entry.is_dir(), entry.name.lower()))

    if not entries:
        print("(empty)")
        return
    for entry in entries:
        if entry.is_dir():
            print(f"{entry.name}/")
        else:
            print(f"{entry.name}\t{entry.stat().st_size}B")


# ------------------------------------------------------------------ 描述符 IO

def open_file(path, mode=None, fd_target=None):
    """OPEN_FILE <path>[, <mode>[, <fd_target>]] —— 打开文件，返回文件描述符。

    mode 支持 r / r+ / w / w+ / a / a+ 六种文本模式，默认 r。
    fd 从 3 开始分配，可直接写入寄存器或内存地址。
    """
    mode_text = (_plain_text(mode) or "r").lower()
    if "b" in mode_text:
        _fatal("Binary modes are not supported (use text modes r/r+/w/w+/a/a+).", mode)
    if mode_text not in ("r", "r+", "w", "w+", "a", "a+"):
        _fatal(f"Unsupported open mode '{mode_text}'.", mode)

    target = _virtual_path(path)
    if mode_text in ("r", "r+") and not target.exists():
        _fatal(f"{_virtual_name(target)} does not exist.", path)
    if target.is_dir():
        _fatal(f"{_virtual_name(target)} is a directory, not a file.", path)
    if mode_text == "r" and not os.access(target, os.R_OK):
        _fatal(f"{_virtual_name(target)} is not readable.", path)

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        handle = open(target, mode_text, encoding="utf-8", newline="")
    except OSError as exc:
        _fatal(f"Cannot open {_virtual_name(target)}: {exc}", path)

    fd = 3
    while fd in _FD_TABLE:
        fd += 1
    _FD_TABLE[fd] = {"handle": handle, "path": target, "mode": mode_text}

    if _plain_text(fd_target):
        _store_value(fd, fd_target)
    else:
        print(fd)


def close_file(fd):
    """CLOSE_FILE <fd> —— 关闭文件描述符。"""
    fd_int, entry = _fd_entry(fd)
    try:
        entry["handle"].close()
    except OSError as exc:
        _fatal(f"Cannot close file descriptor {fd_int}: {exc}", fd)
    del _FD_TABLE[fd_int]


def read_fd(fd, count=None, target=None):
    """READ_FD <fd>[, <count>[, <target>]] —— 从描述符读取（默认读到末尾）。"""
    _, entry = _fd_entry(fd)
    handle = entry["handle"]
    if not handle.readable():
        _fatal(f"File descriptor {fd} is not readable (mode {entry['mode']}).", fd)

    count_text = _plain_text(count)
    try:
        if count_text:
            count_int = _operand_to_int(count_text)
            if count_int < 0:
                _fatal(f"Read count must not be negative: {count_int}.", count)
            text = handle.read(count_int)
        else:
            text = handle.read()
    except OSError as exc:
        _fatal(f"Cannot read file descriptor {fd}: {exc}", fd)

    if _plain_text(target):
        _store_text(text, target)
    else:
        print(text, end="")


def read_line(fd):
    """READ_LINE <fd> —— 读取描述符中的一行。"""
    _, entry = _fd_entry(fd)
    try:
        line = entry["handle"].readline()
    except OSError as exc:
        _fatal(f"Cannot read file descriptor {fd}: {exc}", fd)
    print(line, end="")


def write_fd(fd, content):
    """WRITE_FD <fd>, <content> —— 向描述符写入内容。"""
    _, entry = _fd_entry(fd)
    handle = entry["handle"]
    if not handle.writable():
        _fatal(f"File descriptor {fd} is not writable (mode {entry['mode']}).", fd)

    text = _operand_to_text(content)
    try:
        handle.write(text)
        handle.flush()
    except OSError as exc:
        _fatal(f"Cannot write file descriptor {fd}: {exc}", fd)


def seek_fd(fd, offset):
    """SEEK_FD <fd>, <offset> —— 定位读写指针，输出新位置。"""
    _, entry = _fd_entry(fd)
    offset_int = _operand_to_int(offset)
    try:
        position = entry["handle"].seek(offset_int)
    except (OSError, ValueError) as exc:
        _fatal(f"Cannot seek file descriptor {fd}: {exc}", fd)
    print(position)


def tell_fd(fd, target=None):
    """TELL_FD <fd>[, <target>] —— 输出当前读写指针位置。"""
    _, entry = _fd_entry(fd)
    position = entry["handle"].tell()
    if _plain_text(target):
        _store_value(position, target)
    else:
        print(position)


def list_fds():
    """LIST_FD —— 列出当前所有打开的文件描述符。"""
    if not _FD_TABLE:
        print("(no open files)")
        return
    for fd, entry in sorted(_FD_TABLE.items()):
        print(f"{fd}\t{entry['mode']}\t{_virtual_name(entry['path'])}")
