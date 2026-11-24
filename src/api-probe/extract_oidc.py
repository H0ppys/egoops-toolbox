import glob
import json
import os
import re
import time

DIR = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\edge_ss"
OUT = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json"

def decode_utf16_json(raw: bytes):
    """从 raw 里找第一个 '{'，按 UTF-16LE 解码并用括号配对切出完整 JSON。"""
    start = raw.find(b"{")
    while start >= 0:
        body = raw[start:]
        try:
            text = body.decode("utf-16-le")
        except UnicodeDecodeError:
            start = raw.find(b"{", start + 1)
            continue
        depth = 0
        in_str = False
        esc = False
        for i, ch in enumerate(text):
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[:i + 1])
                    except Exception:
                        break
        start = raw.find(b"{", start + 1)
    return None

found = None
for f in sorted(glob.glob(os.path.join(DIR, "*"))):
    if os.path.isdir(f):
        continue
    data = open(f, "rb").read()
    i = data.find(b"oidc.user")
    if i < 0:
        continue
    # 跳过 key 本身（UTF-16LE 的 key 结束位置）
    seg = data[i:]
    obj = decode_utf16_json(seg)
    if obj and obj.get("access_token"):
        found = (os.path.basename(f), obj)
        break

if not found:
    print("未找到 oidc.user 中的 access_token")
    raise SystemExit(1)

fname, obj = found
tok = obj["access_token"]
now = int(time.time())
exp = obj.get("expires_at")
prof = obj.get("profile") or {}

print(f"来源文件: {fname}")
print(f"token 长度: {len(tok)}，前缀: {tok[:24]}…")
print(f"expires_at: {exp}  ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp)) if exp else 'n/a'})")
print(f"当前时间:   {now}  ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))})")
print(f"已过期: {exp is not None and exp < now}")
print(f"scope: {obj.get('scope')}")
print(f"用户: {prof.get('name')} / {prof.get('mis')} / {prof.get('email')}")

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump({"access_token": tok, "expires_at": exp,
               "profile": prof, "scope": obj.get("scope")}, fh, ensure_ascii=False, indent=2)
print(f"\n已保存到 {OUT}")
