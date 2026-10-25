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
