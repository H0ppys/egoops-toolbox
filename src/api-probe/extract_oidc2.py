import glob
import json
import os
import re
import time

DIR = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\edge_ss"
OUT = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json"


def utf16_literal(s: str) -> bytes:
    return s.encode("utf-16-le")


def find_all_utf16(data: bytes, literal: str):
    pat = utf16_literal(literal)
    idx = 0
    while True:
        i = data.find(pat, idx)
        if i < 0:
            return
        idx = i + 1
        yield i


def grab_utf16_value(data: bytes, start: int):
    """start 指向 UTF-16LE 值的第一个字节；读到下一个 \" (UTF-16LE) 为止。"""
    end_quote = b'"\x00'
    j = start
    while True:
        k = data.find(end_quote, j)
        if k < 0:
            return None
        # 必须落在偶数对齐位置（相对于值的起点）
        if (k - start) % 2 == 0:
            raw = data[start:k]
            try:
                return raw.decode("utf-16-le")
            except UnicodeDecodeError:
                return None
        j = k + 1


results = []
for f in sorted(glob.glob(os.path.join(DIR, "*"))):
    if os.path.isdir(f):
        continue
    data = open(f, "rb").read()
    if b"oidc.user" not in data and b"egoops" not in data:
        continue
    for pos in find_all_utf16(data, '"access_token":"'):
        val = grab_utf16_value(data, pos + len(utf16_literal('"access_token":"')))
        if val and val.count(".") == 2 and len(val) > 100:
            results.append((os.path.basename(f), pos, val))

if not results:
    print("仍未找到 JWT 形态的 access_token")
    raise SystemExit(1)

# 去重
uniq = {}
for fname, pos, tok in results:
    uniq.setdefault(tok, (fname, pos))

print(f"找到 {len(results)} 处候选，去重后 {len(uniq)} 个 token\n")
now = int(time.time())
best = None
for tok, (fname, pos) in uniq.items():
    parts = tok.split(".")
    print(f"- {fname} @ {pos}: len={len(tok)} head={tok[:20]}…")
    best = tok

# 解析 JWT payload 看过期时间
def b64d(s):
    import base64
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

payload = json.loads(b64d(best.split(".")[1]))
exp = payload.get("exp")
print("\nJWT payload 关键字段:")
for k in ("sub", "name", "mis", "exp", "iat", "aud", "scope", "typ"):
    if k in payload:
        v = payload[k]
        if k in ("exp", "iat") and isinstance(v, int):
            v = f"{v} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v))})"
        print(f"  {k}: {v}")
print(f"\n当前时间: {now} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))})")
print(f"是否过期: {exp is not None and exp < now}")

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump({"access_token": best, "exp": exp, "payload": payload}, fh, ensure_ascii=False, indent=2)
print(f"已保存到 {OUT}")
