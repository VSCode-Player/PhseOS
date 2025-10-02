import json
from os.path import exists,isdir,isfile

with open("build.json","r",encoding="utf-8") as build_info:
    build_dict = json.loads(build_info.read())

    if exists(build_dict["RAM_file"]) and isfile(build_dict["RAM_file"]): # 如果内存文件存在且是文件
        if exists(build_dict["REG_file"]) and isfile(build_dict["REG_file"]): # 如果寄存器文件存在且是文件
            if exists(build_dict["STORAGE_file"]) and isdir(build_dict["STORAGE_file"]): # 如果硬盘文件夹存在且是文件夹
                if exists(build_dict["RAM_status_file"]) and isfile(build_dict["RAM_status_file"]): # 如果内存状态文件存在且是个文件
                    if exists(build_dict["REG_status_file"]) and isfile(build_dict["REG_status_file"]): # 如果寄存器状态文件存在且是个文件
                        if exists(build_dict["REG_F_file"]) and isfile(build_dict["REG_F_file"]):
                            with open(build_dict["RAM_file"],"w",encoding="utf-8") as RAM_file: # 打开内存文件为RAM_file
                                with open(build_dict["REG_file"],"w",encoding="utf-8") as REG_file: # 打开寄存器文件为REG_file
                                    with open(build_dict["RAM_status_file"],"w",encoding="utf-8") as RAM_status: # 打开内存占用状态文件为RAM_status
                                        with open(build_dict["REG_status_file"],"w",encoding="utf-8") as REG_status: # 打开寄存器占用状态为REG_status
                                            with open(build_dict["REG_F_file"],"w",encoding="utf-8") as REG_F_file: # 打开寄存器特殊位文件为REG_F_file
                                                RAM_file.write(json.dumps({f"0x{i:04X}":"" for i in range(0,build_dict["memory_size"])})) # 写入内存到RAM_file.json
                                                REG_file.write(json.dumps({f"R{i}":"0"*build_dict["reg_set"]["reg_width"] for i in range(0,build_dict["reg_set"]["reg_count"])}))# 写入寄存器数据到REG_file.json
                                                RAM_status.write(json.dumps({f"0x{i:04X}":False for i in range(0,build_dict["memory_size"])})) # 写入内存状态到status.json
                                                REG_status.write(json.dumps({f"R{i}":False for i in range(0,build_dict["reg_set"]["reg_count"])})) # 写入寄存器数据到REG_file.json
                                                REG_F_file.write(json.dumps({"LX":0}))
                    else:
                        print("Register Status file not found")
                else:
                    print("Memory Status file not found")
            else:
                print("Disk not found") # 硬盘文件未找到
        else:
            print("Register not found") # 寄存器未找到
    else:
        print("Memory not found") # 内存文件未找到