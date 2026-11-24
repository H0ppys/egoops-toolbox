import io
import json
import os
import subprocess

CLI = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BASE = "<FILL_ME>"
TABLE = "tbln9OE8dCkeBOrE"

os.environ["LARK_HOME"] = os.path.abspath(".tmp/larkhome")

q = os.path.abspath("sim/lark_q.json")
io.open(q, "w", encoding="utf-8").write(json.dumps({"limit": 200}))

# 先看字段
r = subprocess.run([CLI, "base", "+field-list", "--base-token", BASE, "--table-id", TABLE],
                   capture_output=True, text=True, encoding="utf-8")
print("字段:", r.stdout[:800] or r.stderr[:400])

r = subprocess.run([CLI, "base", "+record-search", "--base-token", BASE, "--table-id", TABLE,
                    "--json", "@" + q, "--format", "json"],
                   capture_output=True, text=True, encoding="utf-8")
out = r.stdout or ""
io.open("sim/lark_records.json", "w", encoding="utf-8").write(out)
print("记录返回长度:", len(out))
print(out[:600])
