import json
import re
import os
from PhseXlib.addres import * # type: ignore
from PhseXlib.op_lib import * # type: ignore
from PhseXlib.locals import * # type: ignore
from PhseXlib.code_expand import memory_usage_check
from phsex import label_table, imported_package,args_partten
from pathlib import Path

# CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def mov(first_addr, second_addr):
    try:
        first_addr_dict = address_transformer(first_addr)
        second_addr_dict = address_transformer(second_addr)
    except Exception as e:
        op_stop_os(f"Address transformation failed: {str(e)}", 1)
        return
    
    if first_addr_dict["file"] == "TYPE:STRING":
        try:
            op_write(op_data_transform(first_addr_dict["key"][1], CHAR_TO_BIN), second_addr_dict)
        except Exception as e:
            op_stop_os(f"Failed to write string data: {str(e)}", 1)
    elif first_addr_dict["file"] == "TYPE:INT":
        try:
            op_write(op_data_transform(first_addr_dict["key"], INT_TO_BIN), second_addr_dict)
        except Exception as e:
            op_stop_os(f"Failed to write integer data: {str(e)}", exit_code=1)
    else:
        try:
            with open(first_addr_dict["file"], "r+", encoding="utf-8") as first_file:
                first_file_dict = json.load(first_file)
                if first_addr_dict["key"] not in first_file_dict:
                    op_stop_os(f"Key '{first_addr_dict['key']}' not found in file '{first_addr_dict['file']}'", 1)
                    return
                op_write(first_file_dict[first_addr_dict["key"]], second_addr_dict)
        except FileNotFoundError:
            op_stop_os(f"File not found: {first_addr_dict['file']}", 1)
        except json.JSONDecodeError:
            op_stop_os(f"Invalid JSON format in file: {first_addr_dict['file']}", 1)
        except Exception as e:
            op_stop_os(f"Error in mov operation: {str(e)}",error_args=f"{first_addr}\n{second_addr}", exit_code=1)

def left_shift(addr, num):
    try:
        addr_dict = address_transformer(addr)
    except Exception as e:
        op_stop_os(f"Address transformation failed: {str(e)}", 1)
        return
    
    try:
        num = int(num)
    except ValueError:
        op_stop_os(f"Invalid shift amount: '{num}' must be an integer", 1)
        return
    
    try:
        with open(addr_dict["file"], "r+", encoding="utf-8") as FILE:
            try:
                FILE_DICT = json.load(FILE)
            except json.JSONDecodeError:
                op_stop_os(f"Invalid JSON format in file: {addr_dict['file']}", 1)
                return
            
            if addr_dict["key"] not in FILE_DICT:
                op_stop_os(f"Key '{addr_dict['key']}' not found in file", 1)
                return
            
            data = FILE_DICT[addr_dict["key"]]
            if not isinstance(data, str):
                op_stop_os(f"Data must be string type for shift operation", 1)
                return
            
            result = data[num:] + "0" * num
            op_write(result, addr_dict)
    except FileNotFoundError:
        op_stop_os(f"File not found: {addr_dict['file']}", 1)
    except Exception as e:
        op_stop_os(f"Error in left_shift: {str(e)}", 1)

def right_shift(addr, num):
    try:
        addr_dict = address_transformer(addr)
    except Exception as e:
        op_stop_os(f"Address transformation failed: {str(e)}", 1)
        return
    
    try:
        num = int(num)
    except ValueError:
        op_stop_os(f"Invalid shift amount: '{num}' must be an integer", 1)
        return
    
    try:
        with open(addr_dict["file"], "r+", encoding="utf-8") as FILE:
            try:
                FILE_DICT = json.load(FILE)
            except json.JSONDecodeError:
                op_stop_os(f"Invalid JSON format in file: {addr_dict['file']}", 1)
                return
            
            if addr_dict["key"] not in FILE_DICT:
                op_stop_os(f"Key '{addr_dict['key']}' not found in file", 1)
                return
            
            data = FILE_DICT[addr_dict["key"]]
            if not isinstance(data, str):
                op_stop_os(f"Data must be string type for shift operation", 1)
                return
            
            result = "0" * num + data[:-num]
            op_write(result, addr_dict)
    except FileNotFoundError:
        op_stop_os(f"File not found: {addr_dict['file']}", 1)
    except Exception as e:
        op_stop_os(f"Error in right_shift: {str(e)}", 1)

def set_flag(data, flag):
    try:
        with open(CONFIG["REG_flag_file"], "r+", encoding="utf-8") as REG_F_file:
            try:
                REG_F_dict = json.load(REG_F_file)
            except json.JSONDecodeError:
                op_stop_os(f"Invalid JSON format in flag file: {CONFIG['REG_flag_file']}", 1)
                return
            
            if flag not in REG_F_dict:
                op_stop_os(f"Flag '{flag}' not found.", 1)
                return
            
            try:
                op_write(int(data), {"file": CONFIG["REG_flag_file"], "key": flag})
            except ValueError:
                if isinstance(data, str) and len(data) >= 2 and data[0] == "\"" and data[-1] == "\"":
                    op_write(data[1:-1], {"file": CONFIG["REG_flag_file"], "key": flag})
                else:
                    op_stop_os(f"Invalid data type for flag '{flag}'.", 1)
    except FileNotFoundError:
        op_stop_os(f"Flag file not found: {CONFIG['REG_flag_file']}", 1)
    except Exception as e:
        op_stop_os(f"Error in set_flag: {str(e)}", 1)

def set_status(addr: str, status: str):
    try:
        addr_dict = address_transformer(addr)
    except Exception as e:
        op_stop_os(f"Address transformation failed: {str(e)}", 1)
        return
    
    status_file = os.path.join(os.path.dirname(addr_dict["file"]), "status.json")
    
    try:
        with open(status_file, "r+", encoding="utf-8") as f:
            try:
                status_dict = json.load(f)
            except json.JSONDecodeError:
                op_stop_os(f"Invalid JSON format in status file: {status_file}", 1)
                return
            
            if addr_dict["key"] not in status_dict:
                op_stop_os(f"Key '{addr_dict['key']}' not found in status file", 1)
                return
            
            status_dict[addr_dict["key"]] = status
            f.seek(0)
            json.dump(status_dict, f)
            f.truncate()
    except FileNotFoundError:
        op_stop_os(f"Status file not found: {status_file}", 1)
    except Exception as e:
        op_stop_os(f"Error in set_status: {str(e)}", 1)

def get_input(start_addr:str, type:str):
    input_data = input()
    start_addr_dict = address_transformer(start_addr)
    data_list = []
    if type == "INT":
        int_data = get_value(address_transformer(input_data))
        op_write(op_data_transform(int_data, INT_TO_BIN),start_addr_dict)
    elif type == "STR":
        str_list = []
        for i in input_data:
            str_list.append(op_data_transform(i, CHAR_TO_BIN))
        use_space = _check_memory_space(start_addr_dict,len(str_list))
        if use_space not in ["Not enough memory","Not enough registry"]:
            for j in use_space:
                for k in str_list:
                    op_write(k, address_transformer(j))
    else:
        op_stop_os("Input must be int, string and bin.",1)

def _check_memory_space(start_addr_dict, data_size) -> list | str: # type: ignore
    start_addr = start_addr_dict["key"]
    addr_file_dict = load_addr_file(start_addr_dict)
    addr_file_key_list = list(addr_file_dict.keys())
    free_space = []
    if re.fullmatch(ram,addr_file_key_list[0]):
        with open(CONFIG["RAM_status_file"],"r",encoding="utf-8") as RAM_status_file:
            RAM_status_file = list(json.load(RAM_status_file).values())
            if start_addr in addr_file_key_list:
                start_addr_index = addr_file_key_list.index(start_addr)
                for i in range(0,len(RAM_status_file[start_addr_index:])):
                    if RAM_status_file[i] == "free":
                        free_space.append(addr_file_key_list[i])
                    else:
                        continue

                    if len(free_space) >= data_size:
                        return free_space
    elif re.fullmatch(register, addr_file_key_list[0]):
        with open(CONFIG["REG_status_file"],"r",encoding="utf-8") as REG_status_file:
            REG_status_file_list = list(json.load(REG_status_file).values())
            if start_addr in addr_file_key_list:
                start_addr_index = addr_file_key_list.index(start_addr)
                for i in range(0,len(REG_status_file_list[start_addr_index:])):
                    if REG_status_file_list[i] == "free":
                        free_space.append(addr_file_key_list[i])
                    else:
                        continue
                    
                    if len(free_space) >= data_size:
                        return free_space
    else:
        op_stop_os("start addres is invalid",1)

def _get_cmp_flag():
    """Helper function to get CMP flag value with error handling"""
    try:
        with open(CONFIG["REG_flag_file"], "r", encoding="utf-8") as f:
            try:
                flags = json.load(f)
            except json.JSONDecodeError:
                op_stop_os(f"Invalid JSON format in flag file: {CONFIG['REG_flag_file']}", 1)
                return None
            
            if "CMP" not in flags:
                op_stop_os("CMP flag not found in flag file", 1)
                return None
            
            try:
                return int(flags["CMP"])
            except ValueError:
                op_stop_os("CMP flag value is not a valid integer", 1)
                return None
    except FileNotFoundError:
        op_stop_os(f"Flag file not found: {CONFIG['REG_flag_file']}", 1)
        return None
    except Exception as e:
        op_stop_os(f"Error reading CMP flag: {str(e)}", 1)
        return None

def _execute_label(label):
    code_list = []
    if label in label_table:
        for i in label_table[label]:
            code_list.append(i)
    else:
        op_stop_os(f"Label {label} is not found.",1)
    
    for code in code_list:
        for pkg_name in imported_package:
            found_function = False
            if code["name"] in imported_package[pkg_name]:
                found_function = True
                args = [a.strip() for a in re.split(args_partten, code['args'])] if code["args"] else []
                if CONFIG["PhseX"]["data_security_mode"]:
                    security_func = memory_usage_check(imported_package[pkg_name][code["name"]](*args))
                    try:
                        security_func(*args)
                    except TypeError:
                        pass # 这NoneType Error是什么鬼东西？？？结果都出来了给我来个报错
                else:
                    imported_package[pkg_name][code["name"]](*args)
                break
            else:
                continue
        if found_function: # type: ignore
            pass
        else:
            op_stop_os(f"Function {code["name"]} not found.",1,code["name"])

def jmp(label):
    _execute_label(label)

def jz(label):
    cmp = _get_cmp_flag()
    if cmp is None:
        return
    
    if cmp == 0:
        _execute_label(label)

def jnz(label):
    cmp = _get_cmp_flag()
    if cmp is None:
        return
    
    if cmp != 0:
        _execute_label(label)

def jg(label):
    cmp = _get_cmp_flag()
    if cmp is None:
        return
    
    if cmp > 0:
        _execute_label(label)

def jl(label):
    cmp = _get_cmp_flag()
    if cmp is None:
        return
    
    if cmp < 0:
        _execute_label(label)

def jge(label):
    cmp = _get_cmp_flag()
    if cmp is None:
        return
    
    if cmp >= 0:
        _execute_label(label)

def jle(label):
    cmp = _get_cmp_flag()
    if cmp is None:
        return
    
    if cmp <= 0:
        _execute_label(label)