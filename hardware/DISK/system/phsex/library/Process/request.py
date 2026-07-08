from phsex import label_table,process_list
from PhseXlib.op_lib import op_stop_os

def create_process(label_name):
    if label_name in label_table:
        PID = process_list[-1]["PID"]+1 if process_list else "0"
        process_info_dict = {"PID":PID,"label_name":label_name}
        process_list.append(process_info_dict)
    else:
        op_stop_os(f"{label_name} not found in label_table.",1,label_name)

def allocate_memroy(process_name,size):
    if process_name in process_list:
        pass
    else:
        op_stop_os(f"Cannot find process {process_name}.",1,process_name)