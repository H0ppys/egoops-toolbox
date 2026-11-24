import io
import json
import os
import subprocess

CLI = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BASE = "<FILL_ME>"
TABLE = "tbln9OE8dCkeBOrE"
os.environ["LARK_HOME"] = os.path.abspath(".tmp/larkhome")

path = f"/open-apis/bitable/v1/apps/{BASE}/tables/{TABLE}/records"
r = subprocess.run([CLI, "api", "GET", path, "--params", json.dumps({"page_size": 200})],
                   capture_output=True, text=True, encoding="utf-8")
print("rc:", r.returncode)
print("stdout:", (r.stdout or "")[:400])
print("stderr:", (r.stderr or "")[:400])
if r.stdout:
    io.open("sim/lark_records.json", "w", encoding="utf-8").write(r.stdout)
