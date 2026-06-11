from phsex import lable_table,process_list
from PhseXlib.op_lib import op_stop_os

def create_process(lable_name):
    if lable_name in lable_table:
        PID = process_list[-1]["PID"]+1 if process_list else "0"
        process_info_dict = {"PID":PID,"lable_name":lable_name}
        process_list.append(process_info_dict)
    else:
        op_stop_os(f"{lable_name} not found in lable_table.",1,lable_name)