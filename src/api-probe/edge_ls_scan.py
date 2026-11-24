import re
import glob
import os
import sys

DIR = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\edge_ls"

files = sorted(glob.glob(os.path.join(DIR, "*")))
print("扫描文件:", len(files))

hits = []
for f in files:
    if os.path.isdir(f):
        continue
    try:
        data = open(f, "rb").read()
    except Exception as e:
        print("读取失败", f, e)
        continue

    # ASCII 可打印串
    for m in re.finditer(rb"[\x20-\x7e]{20,}", data):
        s = m.group().decode("ascii", "replace")
        if "egoops" in s or s.startswith("eyJ") or "access_token" in s:
            hits.append((os.path.basename(f), s[:600]))

    # UTF-16LE 串
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){12,}", data):
        s = m.group().decode("utf-16-le", "replace")
        if "egoops" in s or s.startswith("eyJ") or "access_token" in s:
            hits.append((os.path.basename(f) + " [utf16]", s[:600]))

seen = set()
for name, s in hits:
    key = s[:120]
    if key in seen:
        continue
    seen.add(key)
    print("\n---", name)
    print(s)

print("\n总命中:", len(seen))
