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
> 截止目前，`build.json`中所包含的内容如下所示:
```json
{
    "RAM_file" : "hardware\\RAM\\memory.json",
    "RAM_status_file" : "hardware\\RAM\\status.json",
    "REG_file" : "hardware\\CPU\\register.json",
    "REG_flag_file": "hardware\\CPU\\F.json",
    "REG_status_file" : "hardware\\CPU\\status.json",
    "STORAGE_dir" : "hardware\\DISK",
    "PhseX_library":"hardware\\DISK\\system\\phsex\\library",
    "memory_size" : 1024,
    "PhseX":{
        "debug_mode":true,
        "data_security_mode":false
    },
    "reg_set" : {
        "reg_width" : 8,
        "reg_count" : 8
    }
}
```
以上内容是`build.json`的默认内容，也是最推荐的格式，不建议更改。<br>
| 项 | 文件类型 | 描述
| - | - | - |
| `RAM_file`  | `Json文件`| 内存文件的路径 |
| `RAM_status_file`  |`Json文件`| 内存状态文件的路径 |
| `REG_file`  |`Json文件`| 寄存器文件的路径 |
| `REG_status_file`  |`Json文件`| 寄存器状态文件的路径 | 
| `REG_flag_file`  | `Json文件` | 寄存器标志位文件的路径 | 
| `STORAGE_dir` | `Json文件` | 内部存储路径 |
| `PhseX_library` | `文件夹` | `PhseX`外部库路径 |
| `memory_size` | `整数` | 内存大小，单位为`byte`，这将会影响`RAM_file`与`RAM_status_file`的内容 |
| `PhseX.debug_mode` | `布尔值` | 是否让PhseX以调试模式运行 |
| `PhseX.data_security_mode` | `布尔值` | 是否开启数据隔离（测试阶段,有BUG）
| `reg_set.reg_width` | `整数` | 每个寄存器位有多少比特组成，这将会影响`REG_file`与`REG_status_file`的内容 |
| `reg_set.reg_count` | `整数` | 有多少寄存器，这将会影响`REG_file`与`REG_status_file`的内容 |