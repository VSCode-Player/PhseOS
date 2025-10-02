import json, re, os
from pathlib import Path

# ---------- 正则 & 配置 ----------
HEX_PATTERN = re.compile(r'^0[xX][0-9a-fA-F]+$')
REG_PATTERN = re.compile(r'^R\d+$')
IMM_PATTERN = re.compile(r'^i\d+$')
STR_PATTERN = re.compile(r'^s"([^"]*)"$')   # 捕获引号内内容
CONFIG = json.loads(Path("build.json").read_text())

# ---------- 地址解析器 ----------
def parse_operand(op: str):
    if IMM_PATTERN.fullmatch(op):
        return lambda: int(op[1:])
    if STR_PATTERN.fullmatch(op):
        return lambda: STR_PATTERN.fullmatch(op).group(1) # type: ignore
    if HEX_PATTERN.fullmatch(op):
        return lambda: json.loads(Path(CONFIG["RAM_file"]).read_text())[op]
    if REG_PATTERN.fullmatch(op):
        return lambda: json.loads(Path(CONFIG["REG_file"]).read_text())[op]
    raise ValueError(f"Invalid operand: {op}")

# ---------- 数据写入器 ----------
def write_operand(op: str, value):
    if HEX_PATTERN.fullmatch(op):
        path = Path(CONFIG["RAM_file"])
    elif REG_PATTERN.fullmatch(op):
        path = Path(CONFIG["REG_file"])
    else:
        raise ValueError(f"Cannot write to operand: {op}")

    data = json.loads(path.read_text())
    data[op] = value
    path.write_text(json.dumps(data, separators=(",", ":")))

def flush_file(file):
    """强制落盘函数，删不得"""
    file.flush()
    os.fsync(file.fileno())

# ---------- 多行块解析器（预留） ----------
def expand_multiline(lines: list[str], first: int, last: int) -> list[str]:
    """
    通用多行展开器：
      lines  : 原始文件行列表（含注释、空行）
      first  : 起始行号（含）
      last   : 结束行号（含）
    返回：
      仅保留有效指令的干净单行列表（去注释、去空行）
    """
    return [
        ln.split("#", 1)[0].strip()
        for ln in lines[first:last+1]
        if ln.split("#", 1)[0].strip()
    ]

# ---------- 数学运算模板 ----------
def alu_line(line: str, op):
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "ALU need 2 args"
    src_op, dst_op = (p.strip() for p in parts[1].split(",", 1))

    try:
        src_val = parse_operand(src_op)()
        dst_val = parse_operand(dst_op)()
        result = int(op(src_val, dst_val))
        write_operand(src_op, result)  # 写回 src
    except Exception as e:
        return str(e)
    return True
# ---------- 逻辑运算模板 ----------
def logic_line(line: str, op):
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "Logic need 2 args"
    src_op, dst_op = (p.strip() for p in parts[1].split(",", 1))

    try:
        src_val = parse_operand(src_op)()
        dst_val = parse_operand(dst_op)()
        result = int(op(src_val, dst_val))
        # 写回标志寄存器
        reg_f_path = Path(CONFIG["REG_F_file"])
        reg_data = json.loads(reg_f_path.read_text())
        reg_data["LX"] = result
        reg_f_path.write_text(json.dumps(reg_data, separators=(",", ":")))
    except Exception as e:
        return str(e)
# ---------- 指令实现 ----------
def run_MOV(line: str):
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "MOV need 2 args"
    src_op, dst_op = (p.strip() for p in parts[1].split(",", 1))

    try:
        val = parse_operand(src_op)()
        write_operand(dst_op, val)
    except Exception as e:
        return str(e)
    return True

def run_NOT(line: str):
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "NOT need 1 arg"
    src_token = parts[1].strip()

    src_file = CONFIG["RAM_file"] if HEX_PATTERN.fullmatch(src_token) else CONFIG["REG_file"]

    with Path(src_file).open(encoding="utf-8") as sf:
        result = not json.load(sf)[src_token]

    with Path(CONFIG["REG_F_file"]).open("r+", encoding="utf-8") as reg_f:
        reg_data = json.load(reg_f)
        reg_data["LX"] = result
        reg_f.seek(0)
        reg_f.truncate()
        reg_f.write(json.dumps(reg_data))
        flush_file(reg_f)

# 数学运算指令
run_ADD = lambda line: alu_line(line, lambda s, d: s + d)
run_SUB = lambda line: alu_line(line, lambda s, d: s - d)
run_MUL = lambda line: alu_line(line, lambda s, d: s * d)
run_DIV = lambda line: alu_line(line, lambda s, d: s // d if d else 0)
run_XOR = lambda line: alu_line(line,lambda s, d: s ^ d) # 异或

# 逻辑运算指令
run_AND = lambda line: logic_line(line,lambda s, d: s and d)
run_OR  = lambda line: logic_line(line,lambda s, d: s or d)

# ---------- 主循环 ----------
KEYWORD_TABLE = {"MOV": run_MOV, "ADD": run_ADD, "SUB": run_SUB,
                 "MUL": run_MUL, "DIV": run_DIV, "NOT": run_NOT,
                 "XOR": run_XOR, "AND": run_AND}

if __name__ == "__main__":
    lines = [ln.rstrip() for ln in Path("main.phx").open(encoding="utf-8")]
    stack = []
    for i in lines:
        print(i[:i.find(" ")])
        print(i[i.find(" "):])