import json, re, os
from pathlib import Path

# ---------- 正则 & 配置 ----------
HEX_PATTERN = re.compile(r'^0[xX][0-9a-fA-F]+$')
REG_PATTERN = re.compile(r'^R\d+$')
IMM_PATTERN = re.compile(r'^i\d+$')
STR_PATTERN = re.compile(r'^s"([^"]*)"$')   # 捕获引号内内容
CONFIG = json.loads(Path("build.json").read_text())

# ---------- 地址解析器（一次性解析） ----------
def parse_operand(op: str):
    """返回立即值/字符串/内存或寄存器中的当前值"""
    if IMM_PATTERN.fullmatch(op):
        return int(op[1:])
    if STR_PATTERN.fullmatch(op):
        return STR_PATTERN.fullmatch(op).group(1)  # type: ignore
    if HEX_PATTERN.fullmatch(op):
        return json.loads(Path(CONFIG["RAM_file"]).read_text())[op]
    if REG_PATTERN.fullmatch(op):
        return json.loads(Path(CONFIG["REG_file"]).read_text())[op]
    raise ValueError(f"Invalid operand: {op}")

# ---------- 数据写入器（自带落盘） ----------
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
        flush_file(f)          # <-- 落盘

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
        and not ln.strip().startswith("LABLE ")  # ✅ 过滤 LABLE 行
        and ln.strip() != "DONE"                 # ✅ 过滤 DONE 行
    ]

# ---------- 数学运算模板（名字不变） ----------
def alu_line(line: str, op):
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "ALU need 2 args"
    src_op, dst_op = (p.strip() for p in parts[1].split(",", 1))

    try:
        src_val = parse_operand(src_op)      # 一次性解析
        dst_val = parse_operand(dst_op)
        result = int(op(src_val, dst_val))
        write_operand(src_op, result)        # 内部已落盘
    except Exception as e:
        return str(e)
    return True
# ---------- 逻辑运算模板（名字不变） ----------
def logic_line(line: str, op):
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "Logic need 2 args"
    src_op, dst_op = (p.strip() for p in parts[1].split(",", 1))

    try:
        src_val = parse_operand(src_op)      # 一次性解析
        dst_val = parse_operand(dst_op)
        result = int(op(src_val, dst_val))
        # 写标志寄存器
        reg_f_path = Path(CONFIG["REG_F_file"])
        reg_data = json.loads(reg_f_path.read_text())
        reg_data["LX"] = result
        with reg_f_path.open("w", encoding="utf-8") as f:
            json.dump(reg_data, f, separators=(",", ":"))
            flush_file(f)                    # <-- 落盘
    except Exception as e:
        return str(e)

# ---------- 非模板指令实现（统一格式） ----------
def run_MOV(line: str):
    """MOV dst,src  把 src 的值写进 dst"""
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "MOV need 2 args"
    src_op, dst_op = (p.strip() for p in parts[1].split(",", 1))

    try:
        val = parse_operand(src_op)   # 解析
        write_operand(dst_op, val)    # 写回（已落盘）
    except Exception as e:
        return str(e)
    return True


def run_NOT(line: str):
    """NOT src  对 src 取反，结果写标志寄存器 LX"""
    parts = line.split(maxsplit=1)
    if len(parts) != 2:
        return "NOT need 1 arg"
    src_op = parts[1].strip()

    try:
        val = parse_operand(src_op)            # 解析
        result = int(not val)                  # 运算
        # 写标志寄存器
        reg_f_path = Path(CONFIG["REG_F_file"])
        reg_data = json.loads(reg_f_path.read_text())
        reg_data["LX"] = result
        with reg_f_path.open("w", encoding="utf-8") as f:
            json.dump(reg_data, f, separators=(",", ":"))
            flush_file(f)                      # 落盘
    except Exception as e:
        return str(e)
    return True

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
    line_count = 0
    LABLE_line = 0          # 0 表示当前不在任何块内
    LABLE_name = ""
    LABLE_list = []
    for i in lines:
        line_count += 1
        if i.startswith("LABLE ") and LABLE_line == 0:  # 只在块外响应新块
            LABLE_line = line_count
            LABLE_name = i.split(" ", 1)[1]
        elif i.strip() == "DONE" and LABLE_line != 0:  # 块内遇到 DONE
            LABLE_list.append([
                LABLE_name,
                expand_multiline(lines, LABLE_line, line_count)
            ])
            LABLE_line = 0      # 清零 -> 回到块外，可继续收下一个块
                
    print("LABLE_BLOCK:", LABLE_list)