from PhseXlib.addres import * # type: ignore
from PhseXlib.op_lib import op_write, op_stop_os, op_data_transform
from PhseXlib.locals import * # type: ignore
from phsex import symbol_table
import json

# CONFIG = json.load(Path("build.json").open("r",encoding="utf-8"))

def add(first_addr, second_addr, result_addr=None):
    '''
    first_addr: 支持立即数、寄存器地址、内存地址、指针
    second_addr: 支持立即数、寄存器地址、内存地址、指针
    result_addr: 支持内存地址、寄存器地址、指针、空
    '''
    first_addr_dict = address_transformer(first_addr)
    second_addr_dict = address_transformer(second_addr)
    if not result_addr:
        result_addr_dict = None
    else:
        result_addr_dict = address_transformer(result_addr)
    first_number = 0
    second_number = 0
    # first number
    if is_address(first_addr_dict):
        first_number = load_addr_file(first_addr_dict)[first_addr_dict["key"]]
    elif first_addr_dict["file"] == "TYPE:INT":
        first_number = get_value(first_addr_dict)
    elif first_addr_dict["file"] == "TYPE:POINT":
        first_temp = get_point_value(first_addr_dict) 
        try:
            first_number = first_temp # type: ignore
        except TypeError:
            op_stop_os("First number must be int",1)
    # second number
    if is_address(second_addr_dict):
        second_number = load_addr_file(second_addr_dict)[second_addr_dict["key"]]
    elif second_addr_dict["file"] == "TYPE:INT":
        second_number = op_data_transform(str(get_value(second_addr_dict)),INT_TO_BIN)
    elif second_addr_dict["file"] == "TYPE:POINT":
        second_temp = get_point_value(second_addr_dict) 
        try:
            second_number = second_temp # type: ignore
        except TypeError:
            op_stop_os("Second number must be int",1)
    # 结果地址
    if is_address(result_addr_dict): # type: ignore
        target_addr = result_addr_dict
    elif result_addr_dict["file"] == "TYPE:POINT": # type: ignore
        target_addr = address_transformer(symbol_table[result_addr_dict["key"]]) # type: ignore
    else:
        op_stop_os("Result addr must be address or point",1)
    result = op_data_transform(first_number,BIN_TO_INT) + op_data_transform(second_number,BIN_TO_INT) # type: ignore
    op_write(op_data_transform(result,INT_TO_BIN),target_addr) # type: ignore

def sub(first_addr, second_addr, result_addr=None):
    '''
    first_addr: 支持立即数、寄存器地址、内存地址、指针
    second_addr: 支持立即数、寄存器地址、内存地址、指针
    result_addr: 支持内存地址、寄存器地址、指针、空
    '''
    first_addr_dict = address_transformer(first_addr)
    second_addr_dict = address_transformer(second_addr)
    if not result_addr:
        result_addr_dict = None
    else:
        result_addr_dict = address_transformer(result_addr)
    first_number = 0
    second_number = 0
    # first number
    if is_address(first_addr_dict):
        first_number = load_addr_file(first_addr_dict)[first_addr_dict["key"]]
    elif first_addr_dict["file"] == "TYPE:INT":
        first_number = get_value(first_addr_dict)
    elif first_addr_dict["file"] == "TYPE:POINT":
        first_temp = get_point_value(first_addr_dict) 
        try:
            first_number = first_temp # type: ignore
        except TypeError:
            op_stop_os("First number must be int",1)
    # second number
    if is_address(second_addr_dict):
        second_number = load_addr_file(second_addr_dict)[second_addr_dict["key"]]
    elif second_addr_dict["file"] == "TYPE:INT":
        second_number = op_data_transform(str(get_value(second_addr_dict)),INT_TO_BIN)
    elif second_addr_dict["file"] == "TYPE:POINT":
        second_temp = get_point_value(second_addr_dict) 
        try:
            second_number = second_temp # type: ignore
        except TypeError:
            op_stop_os("Second number must be int",1)
    # 结果地址
    if is_address(result_addr_dict): # type: ignore
        target_addr = result_addr_dict
    elif result_addr_dict["file"] == "TYPE:POINT": # type: ignore
        target_addr = address_transformer(symbol_table[result_addr_dict["key"]]) # type: ignore
    else:
        op_stop_os("Result addr must be address or point",1)
    result = op_data_transform(first_number,BIN_TO_INT) - op_data_transform(second_number,BIN_TO_INT) # type: ignore
    op_write(op_data_transform(result,INT_TO_BIN),target_addr) # type: ignore

def mul(first_addr, second_addr, result_addr=None):
    '''
    first_addr: 支持立即数、寄存器地址、内存地址、指针
    second_addr: 支持立即数、寄存器地址、内存地址、指针
    result_addr: 支持内存地址、寄存器地址、指针、空
    '''
    first_addr_dict = address_transformer(first_addr)
    second_addr_dict = address_transformer(second_addr)
    if not result_addr:
        result_addr_dict = None
    else:
        result_addr_dict = address_transformer(result_addr)
    first_number = 0
    second_number = 0
    # first number
    if is_address(first_addr_dict):
        first_number = load_addr_file(first_addr_dict)[first_addr_dict["key"]]
    elif first_addr_dict["file"] == "TYPE:INT":
        first_number = get_value(first_addr_dict)
    elif first_addr_dict["file"] == "TYPE:POINT":
        first_temp = get_point_value(first_addr_dict) 
        try:
            first_number = first_temp # type: ignore
        except TypeError:
            op_stop_os("First number must be int",1)
    # second number
    if is_address(second_addr_dict):
        second_number = load_addr_file(second_addr_dict)[second_addr_dict["key"]]
    elif second_addr_dict["file"] == "TYPE:INT":
        second_number = op_data_transform(str(get_value(second_addr_dict)),INT_TO_BIN)
    elif second_addr_dict["file"] == "TYPE:POINT":
        second_temp = get_point_value(second_addr_dict) 
        try:
            second_number = second_temp # type: ignore
        except TypeError:
            op_stop_os("Second number must be int",1)
    # 结果地址
    if is_address(result_addr_dict): # type: ignore
        target_addr = result_addr_dict
    elif result_addr_dict["file"] == "TYPE:POINT": # type: ignore
        target_addr = address_transformer(symbol_table[result_addr_dict["key"]]) # type: ignore
    else:
        op_stop_os("Result addr must be address or point",1)
    result = op_data_transform(first_number,BIN_TO_INT) * op_data_transform(second_number,BIN_TO_INT) # type: ignore
    op_write(op_data_transform(result,INT_TO_BIN),target_addr) # type: ignore

def div(first_addr, second_addr, result_addr=None):
    '''
    first_addr: 支持立即数、寄存器地址、内存地址、指针
    second_addr: 支持立即数、寄存器地址、内存地址、指针
    result_addr: 支持内存地址、寄存器地址、指针、空
    '''
    first_addr_dict = address_transformer(first_addr)
    second_addr_dict = address_transformer(second_addr)
    if not result_addr:
        result_addr_dict = None
    else:
        result_addr_dict = address_transformer(result_addr)
    first_number = 0
    second_number = 0
    # first number
    if is_address(first_addr_dict):
        first_number = load_addr_file(first_addr_dict)[first_addr_dict["key"]]
    elif first_addr_dict["file"] == "TYPE:INT":
        first_number = get_value(first_addr_dict)
    elif first_addr_dict["file"] == "TYPE:POINT":
        first_temp = get_point_value(first_addr_dict) 
        try:
            first_number = first_temp # type: ignore
        except TypeError:
            op_stop_os("First number must be int",1)
    # second number
    if is_address(second_addr_dict):
        second_number = load_addr_file(second_addr_dict)[second_addr_dict["key"]]
    elif second_addr_dict["file"] == "TYPE:INT":
        second_number = op_data_transform(str(get_value(second_addr_dict)),INT_TO_BIN)
    elif second_addr_dict["file"] == "TYPE:POINT":
        second_temp = get_point_value(second_addr_dict) 
        try:
            second_number = second_temp # type: ignore
        except TypeError:
            op_stop_os("Second number must be int",1)
    # 结果地址
    if is_address(result_addr_dict): # type: ignore
        target_addr = result_addr_dict
    elif result_addr_dict["file"] == "TYPE:POINT": # type: ignore
        target_addr = address_transformer(symbol_table[result_addr_dict["key"]]) # type: ignore
    else:
        op_stop_os("Result addr must be address or point",1)

    if second_number == op_data_transform(0,INT_TO_BIN):
        op_stop_os("The divisor can't be zero",1)

    result = op_data_transform(first_number,BIN_TO_INT) / op_data_transform(second_number,BIN_TO_INT) # type: ignore
    op_write(op_data_transform(result,INT_TO_BIN),target_addr) # type: ignore
def cmp(first_addr, second_addr):
    """
    比较函数通常固定写入标志寄存器，不建议随意更改写入地址，
    除非有明确需求。此处保持原样，或可根据需要添加 result_addr 但通常无用。
    """
    first_addr_dict = address_transformer(first_addr)
    second_addr_dict = address_transformer(second_addr)
    target_addr = {"file":CONFIG["REG_flag_file"],"key":"CMP"}

    if is_address(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict["file"] == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from CMP: First address must be address or int.", 1, error_args=f"{first_addr}")

    if is_address(second_addr_dict):
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
    first_addr_dict = address_transformer(first_addr)
    second_addr_dict = address_transformer(second_addr)

    # 1. 确定目标地址
    if result_addr is not None:
        if is_address(result_addr):
            target_addr = address_transformer(result_addr)
        else:
            op_stop_os(f"Error from REM: If the third argument is not None, it must be a valid address.", 1, error_args=f"{result_addr}")
    else:
        target_addr = second_addr_dict

    # 2. 解析第一个操作数
    if is_address(first_addr_dict):
        first_addr_file_dict = load_addr_file(first_addr_dict)
        first_num = int(first_addr_file_dict[first_addr_dict["key"]], 2)
    elif first_addr_dict.get("file") == "TYPE:INT":
        first_num = get_value(first_addr_dict)
    else:
        op_stop_os(f"Error from REM: First address must be address or int.", 1, error_args=f"{first_addr}")

    # 3. 解析第二个操作数
    if is_address(second_addr_dict):
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