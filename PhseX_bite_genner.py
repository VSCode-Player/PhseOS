from pathlib import Path
import json

a = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()<>?\\|/[]{}"
b = {}
for i,j in zip(range(0,100),a):
    b[bin(i)[2:].rjust(8,"0")] = j

Path(r"D:\黄开立\Python\Practice\Computer\PhseOS\hardware\DISK\system\CharSet\PhseEncode.json").open("w",encoding="utf-8").write(json.dumps(b))
print(b)