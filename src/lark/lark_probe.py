import subprocess
import os
import sys
import json

LARK = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BASE = "<FILL_ME>"
TABLE = "tblc9lzxiDYJZA9d"


def run(args):
    r = subprocess.run([LARK] + args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL)
    try:
        j = json.loads(r.stdout or "")
    except Exception:
        j = None
    return r.returncode, j, (r.stdout or "")[:150].replace("\n", " "), (r.stderr or "")[:150]


print("frozen:", getattr(sys, "frozen", False))

rc, j, out, err = run(["base", "+record-list", "--base-token", BASE, "--table-id", TABLE,
                       "--limit", "1", "--format", "json", "--as", "bot"])
print(f"[bot 读] rc={rc} ok={bool(j and j.get('ok'))} {out}")

rc, j, out, err = run(["base", "+record-list", "--base-token", BASE, "--table-id", TABLE,
                       "--limit", "1", "--format", "json", "--as", "user"])
print(f"[user 读] rc={rc} ok={bool(j and j.get('ok'))} {out}")

# bot 写一条测试记录（Token ID 带 __probe__ 前缀，稍后删除）
rec = {"Token ID": "__probe_bot_write__", "任务": "probe", "QC": ["待质检"]}
tmp = os.path.join(os.environ.get("TEMP", "."), "probe_rec.json")
with open(tmp, "w", encoding="utf-8") as f:
    json.dump({"create_records": [rec]}, f, ensure_ascii=False)
rc, j, out, err = run(["base", "+record-batch-create", "--base-token", BASE, "--table-id", TABLE,
                       "--json", "@" + tmp, "--as", "bot"])
print(f"[bot 写] rc={rc} ok={bool(j and j.get('ok'))} {out} {(err or '')}")
if j and j.get("ok"):
    ids = [r.get("record_id") for r in (j.get("data", {}).get("records") or [])]
    print("  新记录ID:", ids)
