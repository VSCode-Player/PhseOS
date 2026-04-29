from PhseXlib.addres import * # type: ignore
from PhseXlib.op_lib import op_write, op_stop_os, op_data_transform
from PhseXlib.locals import * # type: ignore
import json

# CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def add(first_addr, second_addr, result_addr=None):
    first_addr_dict = addres_transformer(first_addr)    # 第个地址的文件数据，类型dict
    second_addr_dict = addres_transformer(second_addr) # 第二个地址的文件数据，类型dict
    # 第三个参数，即结果写入地址
    if result_addr is not None:
        if is_addres(result_addr):
            target_addr = addres_transformer(result_addr)
        else:
            op_stop_os(f"Error from ADD:If the third argument is not None, the third argument must be addres.",1,error_args=f"{result_addr}")
    else:
        target_addr = second_addr_dict
    # 第一个参数，即第一个加数
    if is_addres(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]],2)
    elif first_addr_dict["file"] == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from ADD:First addres must be addres or int.",1,error_args=f"{first_addr}")
    # 第二个参数，即第二个加数
    if is_addres(second_addr_dict):
        second_addr_file_dict = load_addr_file(second_addr_dict)
        second_num = int(second_addr_file_dict[second_addr_dict["key"]],2)
    # 如果第三个参数为空，则自动把结果写入第二个参数的地址
    elif target_addr == second_addr_dict: # type: ignore 
        op_stop_os(f"Error from ADD:If the third argument is None, the second argument must be addres.",1,error_args=f"{second_addr}")
    else:
        second_num = get_value(second_addr_dict)

    result = first_num + second_num # type: ignore
    op_write(op_data_transform(result, INT_TO_BIN), target_addr) # type: ignore

def sub(first_addr, second_addr, result_addr=None):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)

    # 1. 确定目标地址
    if result_addr is not None:
        if is_addres(result_addr):
            target_addr = addres_transformer(result_addr)
        else:
            op_stop_os(f"Error from SUB: If the third argument is not None, it must be a valid address.", 1, error_args=f"{result_addr}")
    else:
        target_addr = second_addr_dict

    # 2. 解析第一个操作数
    if is_addres(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict.get("file") == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from SUB: First address must be address or int.", 1, error_args=f"{first_addr}")

    # 3. 解析第二个操作数
    if is_addres(second_addr_dict):
        second_addr_file_dict = load_addr_file(second_addr_dict)
        second_num = int(second_addr_file_dict[second_addr_dict["key"]], 2)
    elif second_addr_dict.get("file") == "TYPE:INT":
        # 如果第二个数是立即数
        if target_addr == second_addr_dict: # type: ignore
             # 试图将结果写回立即数本身，这是非法的
             op_stop_os(f"Error from SUB: If the third argument is None, the second argument must be an address (cannot write to INT).", 1, error_args=f"{second_addr}")
        else:
            second_num = get_value(second_addr_dict)
    else:
        op_stop_os(f"Error from SUB: Second address must be address or int.", 1, error_args=f"{second_addr}")

    # 4. 计算与写入
    result = first_num - second_num # type: ignore
    op_write(op_data_transform(result, INT_TO_BIN), target_addr) # type: ignore

def mul(first_addr, second_addr, result_addr=None):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)

    # 1. 确定目标地址
    if result_addr is not None:
        if is_addres(result_addr):
            target_addr = addres_transformer(result_addr)
        else:
            op_stop_os(f"Error from MUL: If the third argument is not None, it must be a valid address.", 1, error_args=f"{result_addr}")
    else:
        target_addr = second_addr_dict

    # 2. 解析第一个操作数
    if is_addres(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict.get("file") == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from MUL: First address must be address or int.", 1, error_args=f"{first_addr}")

    # 3. 解析第二个操作数
    if is_addres(second_addr_dict):
        second_addr_file_dict = load_addr_file(second_addr_dict)
        second_num = int(second_addr_file_dict[second_addr_dict["key"]], 2)
    elif second_addr_dict.get("file") == "TYPE:INT":
        if target_addr == second_addr_dict: # type: ignore
             op_stop_os(f"Error from MUL: If the third argument is None, the second argument must be an address (cannot write to INT).", 1, error_args=f"{second_addr}")
        else:
            second_num = get_value(second_addr_dict)
    else:
        op_stop_os(f"Error from MUL: Second address must be address or int.", 1, error_args=f"{second_addr}")

    # 4. 计算与写入
    result = first_num * second_num # type: ignore
    op_write(op_data_transform(result, INT_TO_BIN), target_addr) # type: ignore

def div(first_addr, second_addr, result_addr=None):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)

    # 1. 确定目标地址
    if result_addr is not None:
        if is_addres(result_addr):
            target_addr = addres_transformer(result_addr)
        else:
            op_stop_os(f"Error from DIV: If the third argument is not None, it must be a valid address.", 1, error_args=f"{result_addr}")
    else:
        target_addr = second_addr_dict

    # 2. 解析第一个操作数
    if is_addres(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict.get("file") == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from DIV: First address must be address or int.", 1, error_args=f"{first_addr}")

    # 3. 解析第二个操作数
    if is_addres(second_addr_dict):
        second_addr_file_dict = load_addr_file(second_addr_dict)
        second_num = int(second_addr_file_dict[second_addr_dict["key"]], 2)
    elif second_addr_dict.get("file") == "TYPE:INT":
        if target_addr == second_addr_dict: # type: ignore
             op_stop_os(f"Error from DIV: If the third argument is None, the second argument must be an address (cannot write to INT).", 1, error_args=f"{second_addr}")
        else:
            second_num = get_value(second_addr_dict)
    else:
        op_stop_os(f"Error from DIV: Second address must be address or int.", 1, error_args=f"{second_addr}")

    # 4. 除零检查与计算
    if second_num == 0: # type: ignore
        op_stop_os("Error from DIV: The divisor cannot be 0.", 1, error_args=f"{second_addr}")
    
    # 使用整除 // 以匹配二进制整数存储预期
    result = first_num // second_num # type: ignore
    op_write(op_data_transform(result, INT_TO_BIN), target_addr) # type: ignore
def cmp(first_addr, second_addr):
    """
    比较函数通常固定写入标志寄存器，不建议随意更改写入地址，
    除非有明确需求。此处保持原样，或可根据需要添加 result_addr 但通常无用。
    """
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)
    target_addr = {"file":CONFIG["REG_flag_file"],"key":"CMP"}

    if is_addres(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict["file"] == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from CMP: First address must be address or int.", 1, error_args=f"{first_addr}")

    if is_addres(second_addr_dict):
        second_addr_file_dict = load_addr_file(second_addr_dict)
        second_num = int(second_addr_file_dict[second_addr_dict["key"]], 2)
    elif second_addr_dict["file"] == "TYPE:INT":
        second_num = get_value(second_addr_dict)
    else:
        op_stop_os(f"Error from CMP: Second address must be address or int.", 1, error_args=f"{second_addr}")

    result = first_num - second_num # type: ignore
    if result > 0:
        op_write(1,target_addr)
    elif result < 0:
        op_write(-1,target_addr)
    else:
        op_write(0, target_addr)
def rem(first_addr, second_addr, result_addr=None):
    first_addr_dict = addres_transformer(first_addr)
    second_addr_dict = addres_transformer(second_addr)

    # 1. 确定目标地址
    if result_addr is not None:
        if is_addres(result_addr):
            target_addr = addres_transformer(result_addr)
        else:
            op_stop_os(f"Error from REM: If the third argument is not None, it must be a valid address.", 1, error_args=f"{result_addr}")
    else:
        target_addr = second_addr_dict

    # 2. 解析第一个操作数
    if is_addres(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict.get("file") == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from REM: First address must be address or int.", 1, error_args=f"{first_addr}")

    # 3. 解析第二个操作数
    if is_addres(second_addr_dict):
        second_addr_file_dict = load_addr_file(second_addr_dict)
        second_num = int(second_addr_file_dict[second_addr_dict["key"]], 2)
    elif second_addr_dict.get("file") == "TYPE:INT":
        if target_addr == second_addr_dict: # type: ignore
             op_stop_os(f"Error from REM: If the third argument is None, the second argument must be an address (cannot write to INT).", 1, error_args=f"{second_addr}")
        else:
            second_num = get_value(second_addr_dict)
    else:
        op_stop_os(f"Error from REM: Second address must be address or int.", 1, error_args=f"{second_addr}")

    # 4. 除零检查与计算
    if second_num == 0: # type: ignore
        op_stop_os("Error from REM: The divisor cannot be 0.", 1, error_args=f"{second_addr}")
    
    result = first_num % second_num # type: ignore
    op_write(op_data_transform(result, INT_TO_BIN), target_addr) # type: ignore