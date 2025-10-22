import json, re, os
from pathlib import Path

# ---------- 正则 & 配置 ----------
HEX_PATTERN = re.compile(r'^0[xX][0-9a-fA-F]+$')
REG_PATTERN = re.compile(r'^R\d+$')
IMM_PATTERN = re.compile(r'^i\d+$')
STR_PATTERN = re.compile(r'^s"([^"]*)"$')
CONFIG = json.loads(Path("build.json").read_text())

# ---------- 地址解析器 ----------
def parse_operand(op: str):
    if IMM_PATTERN.fullmatch(op):
        return int(op[1:])
    if STR_PATTERN.fullmatch(op):
        return STR_PATTERN.fullmatch(op).group(1)  # type: ignore
    if HEX_PATTERN.fullmatch(op):
        return json.loads(Path(CONFIG["RAM_file"]).read_text())[op]
    if REG_PATTERN.fullmatch(op):
        return json.loads(Path(CONFIG["REG_file"]).read_text())[op]
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
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
        flush_file(f)

def flush_file(file):
    file.flush()
    os.fsync(file.fileno())

# ---------- 多行块解析器 ----------
def expand_multiline(lines: list[str], first: int, last: int) -> list[str]:
    return [
        ln.split(";;", 1)[0].strip()
        for ln in lines[first:last+1]
        if ln.split(";;", 1)[0].strip()
        and not ln.strip().startswith("LABLE ")
        and ln.strip() != "DONE"
    ]

# ---------- 数学运算模板 ----------
def alu_line(line: str, op):
    try:
        src_op, dst_op = (p.strip() for p in line.split(maxsplit=1)[1].split(",", 1))
        src_val = parse_operand(src_op)
        dst_val = parse_operand(dst_op)
        result = int(op(src_val, dst_val))
        write_operand(src_op, result)
    except Exception as e:
        return str(e)
    return True

# ---------- 逻辑运算模板 ----------
def logic_line(line: str, op):
    try:
        src_op, dst_op = (p.strip() for p in line.split(maxsplit=1)[1].split(",", 1))
        src_val = parse_operand(src_op)
        dst_val = parse_operand(dst_op)
        result = int(op(src_val, dst_val))
        reg_f_path = Path(CONFIG["REG_F_file"])
        reg_data = json.loads(reg_f_path.read_text())
        reg_data["LX"] = result
        with reg_f_path.open("w", encoding="utf-8") as f:
            json.dump(reg_data, f, separators=(",", ":"))
            flush_file(f)
    except Exception as e:
        return str(e)

# ---------- 单条指令实现 ----------
def run_MOV(line: str):
    try:
        src_op, dst_op = (p.strip() for p in line.split(maxsplit=1)[1].split(",", 1))
        write_operand(dst_op, parse_operand(src_op))
    except Exception as e:
        return str(e)
    return True

def run_NOT(line: str):
    try:
        src_op = line.split(maxsplit=1)[1].strip()
        val = parse_operand(src_op)
        result = int(not val)
        reg_f_path = Path(CONFIG["REG_F_file"])
        reg_data = json.loads(reg_f_path.read_text())
        reg_data["LX"] = result
        with reg_f_path.open("w", encoding="utf-8") as f:
            json.dump(reg_data, f, separators=(",", ":"))
            flush_file(f)
    except Exception as e:
        return str(e)
    return True

def run_JMP(line: str):
    try:
        _, label = line.split(maxsplit=1)
    except ValueError:
        return "JMP need 1 arg"
    src_lines = [ln.rstrip() for ln in Path("main.phx").open(encoding="utf-8")]
    in_block = False
    start_line = 0
    for idx, ln in enumerate(src_lines, 1):
        if ln.startswith("LABLE ") and ln.split(" ", 1)[1] == label and not in_block:
            in_block = True
            start_line = idx
            continue
        if ln.strip() == "DONE" and in_block:
            body = expand_multiline(src_lines, start_line, idx)
            for sub_ln in body:
                op = sub_ln.split(maxsplit=1)[0]
                KEYWORD_TABLE[op](sub_ln)
            return True
    return f"undefined label: {label}"

# ---------- 指令表 ----------
run_ADD = lambda line: alu_line(line, lambda s, d: s + d)
run_SUB = lambda line: alu_line(line, lambda s, d: s - d)
run_MUL = lambda line: alu_line(line, lambda s, d: s * d)
run_DIV = lambda line: alu_line(line, lambda s, d: s // d if d else 0)
run_XOR = lambda line: alu_line(line, lambda s, d: s ^ d)
run_AND = lambda line: logic_line(line, lambda s, d: s and d)
run_OR  = lambda line: logic_line(line, lambda s, d: s or d)

KEYWORD_TABLE = {
    "MOV": run_MOV, "ADD": run_ADD, "SUB": run_SUB,
    "MUL": run_MUL, "DIV": run_DIV, "NOT": run_NOT,
    "XOR": run_XOR, "AND": run_AND, "OR": run_OR,
    "JMP": run_JMP
}

# ---------- 主循环 ----------
if __name__ == "__main__":
    src_lines = Path("main.phx").read_text(encoding="utf-8").splitlines()
    in_label_block = False
    for raw in src_lines:
        line = raw.split(";;", 1)[0].strip()
        if not line:
            continue
        if line.startswith("LABLE "):
            in_label_block = True
            continue
        if line.strip() == "DONE":
            in_label_block = False
            continue
        if in_label_block:
            continue
        op, *_ = line.split(maxsplit=1)
        if op in KEYWORD_TABLE:
            KEYWORD_TABLE[op](line)