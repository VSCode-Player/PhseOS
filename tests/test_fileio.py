"""FileIO 模块测试

运行方式：
    python3 tests/test_fileio.py

测试分两层：
1. 单元测试：直接调用 file_op 里的系统调用，用临时目录模拟 hardware/DISK；
2. 集成测试：用真实的 init.py + phsex.py 跑一个 .phx 程序，验证 LOAD FileIO
   之后指令能正常分发。
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE_PACKAGES = REPO / "venv" / "Lib" / "site-packages"
FILE_OP = REPO / "hardware" / "DISK" / "system" / "phsex" / "library" / "FileIO" / "file_op.py"
LIBRARY_DIR = REPO / "hardware" / "DISK" / "system" / "phsex" / "library"
CHARSET = REPO / "hardware" / "DISK" / "system" / "CharSet" / "PhseEncode.json"

warnings.filterwarnings("ignore", category=ResourceWarning)

sys.path.insert(0, str(SITE_PACKAGES))
sys.path.insert(0, str(REPO))


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def build_sandbox():
    """搭一个和真实 hardware/ 结构一致的最小磁盘。"""
    root = Path(tempfile.mkdtemp(prefix="phse-fileio-"))
    hardware = root / "hardware"
    disk = hardware / "DISK"
    ram = hardware / "RAM"
    cpu = hardware / "CPU"

    (disk / "home").mkdir(parents=True)
    (disk / "system" / "CharSet").mkdir(parents=True)
    shutil.copy2(CHARSET, disk / "system" / "CharSet" / "PhseEncode.json")

    # 用软链接把真正的库目录挂进来，LOAD 才能找到 stdio/FileIO
    (disk / "system" / "phsex").mkdir(parents=True, exist_ok=True)
    os.symlink(LIBRARY_DIR, disk / "system" / "phsex" / "library")

    cells = {f"{i:#010x}": "00000000" for i in range(64)}
    _write_json(ram / "memory.json", cells)
    _write_json(ram / "status.json", {key: "free" for key in cells})
    registers = {f"R{i}": "00000000" for i in range(8)}
    _write_json(cpu / "register.json", registers)
    _write_json(cpu / "status.json", {key: "free" for key in registers})
    _write_json(cpu / "F.json", {"PC": "", "CMP": 0})

    config = {
        "RAM_file": "hardware/RAM/memory.json",
        "RAM_status_file": "hardware/RAM/status.json",
        "REG_file": "hardware/CPU/register.json",
        "REG_flag_file": "hardware/CPU/F.json",
        "REG_status_file": "hardware/CPU/status.json",
        "STORAGE_dir": "hardware/DISK",
        "PhseX_library": "hardware/DISK/system/phsex/library",
        "memory_size": 64,
        "PhseX": {"debug_mode": False, "data_security_mode": False},
        "reg_set": {"reg_width": 8, "reg_count": 8},
    }
    (root / "build.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    return root


def capture(func, *args):
    """执行函数并返回它打印的内容。"""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        func(*args)
    return buffer.getvalue()


class FileIOTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = build_sandbox()
        os.chdir(cls.root)

        # phsex 在运行期才会被 import，这里先放一个桩，供 symbol_table 使用
        stub = types.ModuleType("phsex")
        stub.symbol_table = {"PTR": "0x00000000"}
        stub.label_table = {}
        stub.process_list = []
        stub.imported_package = {}
        sys.modules["phsex"] = stub
        cls.phsex_stub = stub

        spec = importlib.util.spec_from_file_location("file_op", FILE_OP)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.fio = module

    # ---------------------------------------------------------- 文件基础操作

    def test_create_write_read(self):
        fio = self.fio
        fio.create_file('"/home/a.txt"')
        fio.write_file('"/home/a.txt"', '"hello"')
        self.assertEqual(capture(fio.read_file, '"/home/a.txt"'), "hello")

        fio.write_file('"/home/a.txt"', "65")
        self.assertEqual(capture(fio.read_file, '"/home/a.txt"'), "65")

        fio.append_file('"/home/a.txt"', '", world"')
        self.assertEqual(capture(fio.read_file, '"/home/a.txt"'), "65, world")
        self.assertEqual(capture(fio.file_size, '"/home/a.txt"').strip(), str(len("65, world")))
        self.assertEqual(capture(fio.file_exists, '"/home/a.txt"').strip(), "1")
        self.assertEqual(capture(fio.file_type, '"/home/a.txt"').strip(), "FILE")
        self.assertIn("Type      : FILE", capture(fio.file_info, '"/home/a.txt"'))

    def test_create_file_twice_stops_os(self):
        fio = self.fio
        fio.create_file('"/home/dup.txt"')
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            fio.create_file('"/home/dup.txt"')

    def test_touch_and_exclusive_write(self):
        fio = self.fio
        fio.touch_file('"/home/touch.txt"')
        self.assertTrue((self.root / "hardware/DISK/home/touch.txt").exists())
        fio.touch_file('"/home/touch.txt"')  # 已存在不报错

        fio.write_file('"/home/x.txt"', '"one"', '"x"')
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            fio.write_file('"/home/x.txt"', '"two"', '"x"')

    def test_copy_move_rename_delete(self):
        fio = self.fio
        fio.write_file('"/home/src.txt"', '"payload"')
        fio.copy_file('"/home/src.txt"', '"/home/copy.txt"')
        self.assertEqual(capture(fio.read_file, '"/home/copy.txt"'), "payload")

        fio.move_file('"/home/copy.txt"', '"/home/moved.txt"')
        self.assertEqual(capture(fio.file_exists, '"/home/copy.txt"').strip(), "0")
        self.assertEqual(capture(fio.read_file, '"/home/moved.txt"'), "payload")

        fio.rename_file('"/home/moved.txt"', '"/home/renamed.txt"')
        self.assertEqual(capture(fio.read_file, '"/home/renamed.txt"'), "payload")

        fio.delete_file('"/home/renamed.txt"')
        self.assertEqual(capture(fio.file_exists, '"/home/renamed.txt"').strip(), "0")

    def test_copy_without_overwrite_stops_os(self):
        fio = self.fio
        fio.write_file('"/home/o1.txt"', '"a"')
        fio.write_file('"/home/o2.txt"', '"b"')
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            fio.copy_file('"/home/o1.txt"', '"/home/o2.txt"')
        fio.copy_file('"/home/o1.txt"', '"/home/o2.txt"', "TRUE")
        self.assertEqual(capture(fio.read_file, '"/home/o2.txt"'), "a")

    def test_truncate_and_read_lines(self):
        fio = self.fio
        fio.write_file('"/home/lines.txt"', '"one\\ntwo\\nthree"')
        self.assertEqual(capture(fio.read_lines, '"/home/lines.txt"', "2"), "two\nthree")
        self.assertEqual(capture(fio.read_lines, '"/home/lines.txt"', "2", "1"), "two\n")

        fio.truncate_file('"/home/lines.txt"', "5")
        self.assertEqual(capture(fio.file_size, '"/home/lines.txt"').strip(), "5")

    # ---------------------------------------------------------- 内容寻址

    def test_write_from_register_and_memory(self):
        fio = self.fio
        register_file = self.root / "hardware/CPU/register.json"
        registers = json.loads(register_file.read_text(encoding="utf-8"))
        registers["R0"] = "01000001"          # 65
        _write_json(register_file, registers)

        memory_file = self.root / "hardware/RAM/memory.json"
        memory = json.loads(memory_file.read_text(encoding="utf-8"))
        memory["0x00000005"] = "00000101"      # 5
        _write_json(memory_file, memory)

        fio.write_file('"/home/from_reg.txt"', "R0")
        self.assertEqual(capture(fio.read_file, '"/home/from_reg.txt"'), "65")

        fio.write_file('"/home/from_mem.txt"', "0x00000005")
        self.assertEqual(capture(fio.read_file, '"/home/from_mem.txt"'), "5")

    def test_point_content(self):
        fio = self.fio
        memory_file = self.root / "hardware/RAM/memory.json"
        memory = json.loads(memory_file.read_text(encoding="utf-8"))
        memory["0x00000000"] = "00000011"
        _write_json(memory_file, memory)

        fio.write_file('"/home/from_point.txt"', "[PTR]")
        self.assertEqual(capture(fio.read_file, '"/home/from_point.txt"'), "3")

    def test_read_file_into_memory(self):
        fio = self.fio
        fio.write_file('"/home/bin.txt"', '"AB"')
        fio.read_file('"/home/bin.txt"', "0x00000001")

        memory = json.loads((self.root / "hardware/RAM/memory.json").read_text(encoding="utf-8"))
        # PhseEncode 是自定义字符集（不是 ASCII），用同一个转换函数算期望值
        self.assertEqual(memory["0x00000001"], fio.op_data_transform("A", fio.CHAR_TO_BIN))
        self.assertEqual(memory["0x00000002"], fio.op_data_transform("B", fio.CHAR_TO_BIN))

        status = json.loads((self.root / "hardware/RAM/status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["0x00000001"], "used")

    def test_read_file_int_mode_and_exists_to_register(self):
        fio = self.fio
        fio.write_file('"/home/num.txt"', '"42"')
        fio.read_file('"/home/num.txt"', "R1", '"INT"')
        registers = json.loads((self.root / "hardware/CPU/register.json").read_text(encoding="utf-8"))
        self.assertEqual(registers["R1"], "00101010")

        fio.file_exists('"/home/num.txt"', "R2")
        registers = json.loads((self.root / "hardware/CPU/register.json").read_text(encoding="utf-8"))
        self.assertEqual(registers["R2"], "00000001")

    # ---------------------------------------------------------- 路径安全

    def test_path_traversal_rejected(self):
        fio = self.fio
        for bad in ('"/../etc/passwd"', '"/home/../../x"'):
            with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
                fio.create_file(bad)

    def test_storage_root_cannot_be_deleted(self):
        fio = self.fio
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            fio.delete_dir('"/"')

    # ---------------------------------------------------------- 目录

    def test_directories(self):
        fio = self.fio
        fio.create_dir('"/home/d1"')
        self.assertEqual(capture(fio.dir_exists, '"/home/d1"').strip(), "1")
        self.assertEqual(capture(fio.file_type, '"/home/d1"').strip(), "DIR")

        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            fio.create_dir('"/home/d2/sub"')      # 父目录不存在
        fio.create_dir('"/home/d2/sub"', "TRUE")

        fio.write_file('"/home/d2/sub/f.txt"', '"nested"')
        listing = capture(fio.list_dir, '"/home/d2/sub"')
        self.assertIn("f.txt", listing)

        fio.copy_dir('"/home/d2"', '"/home/d3"')
        self.assertEqual(capture(fio.read_file, '"/home/d3/sub/f.txt"'), "nested")

        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            fio.delete_dir('"/home/d2"')          # 非空目录
        fio.delete_dir('"/home/d2"', "TRUE")
        self.assertEqual(capture(fio.dir_exists, '"/home/d2"').strip(), "0")

    def test_list_dir_pattern(self):
        fio = self.fio
        fio.write_file('"/home/p/a.phx"', '"a"')
        fio.write_file('"/home/p/b.txt"', '"b"')
        listing = capture(fio.list_dir, '"/home/p"', '"*.phx"')
        self.assertEqual(listing.strip(), "a.phx\t1B")

    # ---------------------------------------------------------- 描述符 IO

    def test_file_descriptors(self):
        fio = self.fio
        fd = capture(fio.open_file, '"/home/fd.txt"', '"w+"').strip()
        self.assertTrue(fd.isdigit())

        fio.write_fd(fd, '"abcdef"')
        self.assertEqual(capture(fio.seek_fd, fd, "2").strip(), "2")
        self.assertEqual(capture(fio.read_fd, fd, "3"), "cde")
        self.assertEqual(capture(fio.tell_fd, fd).strip(), "5")
        self.assertIn("/home/fd.txt", capture(fio.list_fds))

        fio.close_file(fd)
        self.assertIn("(no open files)", capture(fio.list_fds))


RUNNER = """
import sys
import init
init.init()
import phsex
phsex.run_code(sys.argv[1])
"""

DEMO_PROGRAM = """LOAD stdio
LOAD FileIO

MSG "== create/write ==\\n"
CREATE_FILE "/home/demo.txt"
WRITE_FILE "/home/demo.txt", "hello world"
READ_FILE "/home/demo.txt"

MSG "\\n== append ==\\n"
APPEND_FILE "/home/demo.txt", "!!"
READ_FILE "/home/demo.txt"

MSG "\\n== size/type ==\\n"
FILE_SIZE "/home/demo.txt"
MSG "\\n"
FILE_TYPE "/home/demo.txt"
MSG "\\n== list ==\\n"
LIST_DIR "/home"

MSG "== comma ==\\n"
WRITE_FILE "/home/comma.txt", "a,b"
READ_FILE "/home/comma.txt"

MSG "== fd ==\\n"
OPEN_FILE "/home/fd.txt", "w+", R0
WRITE_FD R0, "abc"
SEEK_FD R0, 0
READ_FD R0
CLOSE_FILE R0
MSG "\\n== read into memory ==\\n"
CREATE_FILE "/home/bin.txt"
WRITE_FILE "/home/bin.txt", "AB"
READ_FILE "/home/bin.txt", 0x00000000
POINT P0, 0x00000000
MSG [P0], STR
POINT P1, 0x00000001
MSG [P1], STR
MSG "\\n== done ==\\n"
OS_STOP
"""


class PhseOSIntegrationTest(unittest.TestCase):
    """用真实解释器跑一段 .phx，确认指令名和参数切分都对得上。"""

    def test_demo_program(self):
        root = build_sandbox()
        try:
            program = root / "hardware" / "DISK" / "home" / "demo.phx"
            program.write_text(DEMO_PROGRAM, encoding="utf-8")

            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join([str(REPO), str(SITE_PACKAGES)])
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(
                [sys.executable, "-c", RUNNER, str(program)],
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("hello world!!", result.stdout)
            self.assertIn("13", result.stdout)          # hello world!! 的字节数
            self.assertIn("FILE", result.stdout)
            self.assertIn("demo.txt\t13B", result.stdout)
            self.assertIn("a,b", result.stdout)         # 引号内的逗号没有被当成参数分隔符

            registers = json.loads(
                (root / "hardware/CPU/register.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registers["R0"], "00000011")   # OPEN_FILE 把 fd=3 写成二进制

            memory = json.loads(
                (root / "hardware/RAM/memory.json").read_text(encoding="utf-8")
            )
            charset = json.loads(CHARSET.read_text(encoding="utf-8"))
            expected_a = next(code for code, char in charset.items() if char == "A")
            self.assertEqual(memory["0x00000000"], expected_a)
            self.assertIn("3", result.stdout)           # OPEN_FILE 返回 fd=3
            self.assertIn("abc", result.stdout)         # READ_FD 读回内容
            self.assertIn("AB", result.stdout)          # 从内存单元还原出的字符
            self.assertIn("== done ==", result.stdout)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
