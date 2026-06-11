import importlib.util
from PhseXlib.locals import CONFIG
import os

request_op_path = os.path.join(CONFIG["PhseX_library"],"process","request.py")
request_spec = importlib.util.spec_from_file_location("request_op",request_op_path)
request_module = importlib.util.module_from_spec(request_spec) # type: ignore
request_spec.loader.exec_module(request_module) # type: ignore

EXPORT = {
    "Process.create_process":request_module.create_process
}