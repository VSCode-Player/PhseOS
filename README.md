# Phse OS文档
> **相关链接**
>> Github: [VSCode-Player](https://github.com/VSCode-Player/)<br>Bilibili:  [锟斤拷Unicode](https://space.bilibili.com/3546674351835820)<br>E-mail: <python2024123@163.com>
## 关于Phse OS
**Phse OS**是由VSCode-Player使用**Python**开发的**伪OS**.
* 注意：此项目为**伪OS**,即用高级语言模拟低级硬件环境，比如使用JSON模拟内存，并非广义上使用UEFI\BIOS的**OS(操作系统)**
* **Phse OS**中的**Phse**是**Python Hardware Software Emulator**，顾名思义，这是使用Python制作的模拟软件、硬件的项目
* ***!!请不要将此项目当做操作系统项目看待!!***

## 1. *PhseOS介绍*
***Phse OS项目***核心由`PhseOS`与`PhseX`组成。<br>
`PhseOS`所包含的核心文件有`build.json`与`init.py`两个，它们分别负责`PhseOS`的 **配置** 与 **初始化**。
> **build.json**<br>
> * `build.json`存储了`PhseOS`的配置信息，`init.py`在运行时会读取这些信息。<br>
> * `build.json`被读取为`CONFIG`字典在`locals.py`中，用于为其他程序更便携得读取。<br>

## 2. *PhseX库*
`PhseX` 的库都放在 `hardware/DISK/system/phsex/library` 下，每个库是一个目录，
里面至少包含 `package.py`（导出指令表）和具体实现文件。`.phx` 程序通过 `LOAD <库名>` 加载，
例如：

```asm
LOAD stdio
LOAD FileIO
```

目前内置的库：

| 库 | 说明 |
| --- | --- |
| `stdio` | 数学运算、数据搬运、跳转、输入输出（`ADD`/`MOV`/`MSG`/`INP`…） |
| `FileIO` | 完整的文件与目录操作（读写、复制、移动、遍历、描述符 IO） |
| `Process` | 进程创建与内存申请 |

### FileIO
`FileIO` 把 `hardware/DISK` 当作一块磁盘，提供 20+ 条文件系统调用：

```asm
LOAD FileIO

CREATE_FILE "/home/hello.txt"
WRITE_FILE "/home/hello.txt", "Hello, PhseOS!"
APPEND_FILE "/home/hello.txt", "\nSecond line"
READ_FILE "/home/hello.txt"
FILE_INFO "/home/hello.txt"
LIST_DIR "/home", "*.txt"
```

所有路径都相对于 `STORAGE_dir`，`"/home/a.txt"` 即 `hardware/DISK/home/a.txt`；
路径越界（含 `..`、符号链接）会被直接拒绝。完整指令表和参数规则见
[`FileIO/README.md`](hardware/DISK/system/phsex/library/FileIO/README.md)，
可运行的示例见 `hardware/DISK/home/fileio_demo.phx`。

## 3. *测试*
```bash
python3 tests/test_fileio.py
```
