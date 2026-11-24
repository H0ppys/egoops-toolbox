import re
import glob
import os

DIR = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\edge_ss"

for f in sorted(glob.glob(os.path.join(DIR, "*"))):
    if os.path.isdir(f):
        continue
    data = open(f, "rb").read()
    idx = 0
    while True:
        i = data.find(b"oidc.user", idx)
        if i < 0:
            break
        idx = i + 1
        seg = data[i:i + 4000]
        # 只保留可打印字符与换行
        txt = "".join(chr(b) if 32 <= b < 127 else ("\n" if b in (10, 13) else "\u00b7") for b in seg)
        print(f"\n===== {os.path.basename(f)} @ {i} =====")
        print(txt[:3000])

    # 单独把所有 access_token 片段挖出来
    for m in re.finditer(rb'"access_token"\s*:\s*"([^"]{20,})"', data):
        print(f"\n[{os.path.basename(f)}] access_token = {m.group(1).decode('utf-8', 'replace')[:120]}...")
