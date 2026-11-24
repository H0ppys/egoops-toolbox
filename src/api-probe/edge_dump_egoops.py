import re

f = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\edge_ls\001106.ldb"
data = open(f, "rb").read()
print("文件大小:", len(data))

for m in re.finditer(rb"egoops", data):
    s = max(0, m.start() - 300)
    e = min(len(data), m.start() + 900)
    chunk = data[s:e]
    txt = "".join(chr(b) if 32 <= b < 127 else ("\u00b7" if b != 0 else "") for b in chunk)
    print("\n===== 偏移", m.start(), "=====")
    print(txt)

print("\n\n===== 所有含 token 的 ASCII 串 =====")
for m in re.finditer(rb"[\x20-\x7e]{12,}", data):
    s = m.group().decode("ascii", "replace")
    if "token" in s.lower() or s.startswith("eyJ"):
        print(s[:300])
