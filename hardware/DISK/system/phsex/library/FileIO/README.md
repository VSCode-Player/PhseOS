# FileIO —— PhseOS 文件系统调用库

`FileIO` 把 PhseOS 的“磁盘”（`hardware/DISK`）包装成一个以该目录为根的小型文件系统，
`.phx` 程序执行 `LOAD FileIO` 之后即可使用下表的全部指令。

## 虚拟路径

所有路径都相对于 `build.json` 里的 `STORAGE_dir`：

| 写法 | 实际位置 |
| --- | --- |
| `/` | `hardware/DISK` |
| `/home/a.txt` | `hardware/DISK/home/a.txt` |
| `home/a.txt` | 同上（开头有没有 `/` 都一样） |

- 路径中出现 `..`、指向磁盘之外、或者是符号链接时，一律拒绝执行，避免 `.phx` 跑到宿主机上读写别的文件。
- 目录层级固定用 `/`，Windows 风格的 `\` 会被自动转换。

## 参数约定

PhseX 会按逗号把参数切成字符串，所以：

- 路径、内容、模式这类文本参数用双引号包裹，如 `"/home/a.txt"`、`"hello"`；
  支持 `\n` `\t` `\r` `\b` `\0` `\"` `\\` 转义。
- 内容参数还可以直接写整数（`65`）、寄存器（`R0`）、内存地址（`0x00000005`）或指针（`[PTR]`），
  模块会按“文本”语义取值：8 位二进制会转成十进制，其余原样输出。
- 布尔参数接受 `TRUE/FALSE`、`1/0`、`YES/NO`、`ON/OFF`。
- 可选的“目标地址”参数用于把结果写回寄存器或内存，写成 `R0`、`0x00000010` 或 `[PTR]`。

## 指令表

### 文件

| 指令 | 说明 |
| --- | --- |
| `CREATE_FILE <path>` | 新建空文件，已存在则停机报错 |
| `TOUCH_FILE <path>` | 不存在则创建，存在则刷新修改时间 |
| `WRITE_FILE <path>, <content>[, <mode>]` | 写文件，`mode` 支持 `w` 覆盖（默认）/`a` 追加/`x` 仅新建 |
| `APPEND_FILE <path>, <content>` | 追加内容，文件不存在则创建 |
| `READ_FILE <path>[, <target>[, <mode>]]` | 不给 `target` 时打印全文；给 `target` 时按 `STR`（默认）或 `INT` 写入内存 |
| `READ_LINES <path>[, <start>[, <count>]]` | 按行读取，行号从 1 开始 |
| `DELETE_FILE <path>` | 删除文件 |
| `COPY_FILE <src>, <dst>[, <overwrite>]` | 复制文件（保留元数据） |
| `MOVE_FILE <src>, <dst>[, <overwrite>]` | 移动或重命名 |
| `RENAME_FILE <src>, <dst>[, <overwrite>]` | `MOVE_FILE` 的别名 |
| `TRUNCATE_FILE <path>[, <size>]` | 截断/补零到指定字节数（默认 0） |
| `FILE_SIZE <path>[, <target>]` | 文件字节数，可写回地址 |
| `FILE_EXISTS <path>[, <target>]` | 存在输出 1，否则 0 |
| `FILE_TYPE <path>` | 输出 `FILE` / `DIR` / `NONE` |
| `FILE_INFO <path>` | 输出类型、大小、创建/修改/访问时间与权限 |

### 目录

| 指令 | 说明 |
| --- | --- |
| `CREATE_DIR <path>[, <recursive>]` | 新建目录，`recursive=TRUE` 时逐级创建 |
| `DELETE_DIR <path>[, <recursive>]` | 删除目录，`recursive=TRUE` 时递归删除 |
| `COPY_DIR <src>, <dst>[, <overwrite>]` | 递归复制目录 |
| `DIR_EXISTS <path>[, <target>]` | 目录存在输出 1，否则 0 |
| `LIST_DIR <path>[, <pattern>]` | 列出目录内容，`pattern` 支持 `*.phx` 这类通配符 |

### 描述符 IO

| 指令 | 说明 |
| --- | --- |
| `OPEN_FILE <path>[, <mode>[, <fd_target>]]` | 打开文件并返回 fd（从 3 开始），`mode` 支持 `r/r+/w/w+/a/a+` |
| `CLOSE_FILE <fd>` | 关闭 fd |
| `READ_FD <fd>[, <count>[, <target>]]` | 从 fd 读取，默认读到末尾 |
| `READ_LINE <fd>` | 从 fd 读取一行 |
| `WRITE_FD <fd>, <content>` | 向 fd 写入内容 |
| `SEEK_FD <fd>, <offset>` | 定位读写指针并输出新位置 |
| `TELL_FD <fd>[, <target>]` | 输出当前指针位置 |
| `LIST_FD` | 列出所有打开的 fd |

## 示例

```asm
LOAD stdio
LOAD FileIO

CREATE_FILE "/home/hello.txt"
WRITE_FILE "/home/hello.txt", "Hello, PhseOS!"
READ_FILE "/home/hello.txt"

APPEND_FILE "/home/hello.txt", "\nSecond line"
FILE_SIZE "/home/hello.txt"
FILE_INFO "/home/hello.txt"

OPEN_FILE "/home/hello.txt", "r", R0
READ_FD R0
CLOSE_FILE R0

LIST_DIR "/home", "*.txt"
```

运行（在仓库根目录）：

```bash
python -c "from init import init; import phsex; init.init(); phsex.run_code('hardware/DISK/home/fileio_demo.phx')"
```

## 行为说明

- **写入是原子的**：`WRITE_FILE` 先写同目录临时文件再 `os.replace`，中途断电不会留下半截文件。
- **父目录自动创建**：`WRITE_FILE` / `APPEND_FILE` / `OPEN_FILE(w)` 会自动补全缺失的父目录。
- **负载内容按 UTF-8 文本处理**，非 UTF-8 文件读取时会停机并提示。
- **`READ_FILE <path>, <target>` 使用的是 PhseEncode 字符集**（与 `INP STR`、`MSG [P], STR` 一致），
  只有字符集内的字符能写进内存；同时会把对应单元在 `status.json` 里标记为 `used`。
- **8 位寄存器写回会截断**：`FILE_SIZE` 等结果写进 `R0` 时只保留低 8 位，超过 255 的数值建议直接打印。
- 致命错误统一走 `op_stop_os` 停机，与其它 PhseX 模块行为一致。

## 兼容性

`package.py` 同时导出大写指令名和原来的小写函数名，
旧写法 `create_file "/home/a.txt"` 仍然可以继续使用。

## 测试

```bash
python3 tests/test_fileio.py
```

测试覆盖文件与目录的全部指令、内容寻址（寄存器/内存/指针）、路径越界拦截、
描述符 IO，以及用真实 `phsex.py` 跑通一段 `.phx` 的集成验证。
