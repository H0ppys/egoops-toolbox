import json
import sys

sys.path.insert(0, r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace")
from egoops_gui import parse_token_input, jwt_payload

real = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]

cases = {
    "纯 token": real,
    "带引号": f'"{real}"',
    "Authorization 头": f"authorization: Bearer {real}",
    "cURL（单引号）": f"curl 'https://mrobo.uav.meituan.com/egoops/api/v1/recordings?page=1&size=20' -H 'accept: application/json' -H 'authorization: Bearer {real}'",
    "cURL（双引号+反斜杠）": f'curl "https://mrobo.uav.meituan.com/egoops/api/v1/recordings" -H "authorization: Bearer {real}"',
    "空内容": "",
}

for name, text in cases.items():
    got = parse_token_input(text)
    ok = got == real
    print(f"{name:22s} -> {'OK' if ok else ('None' if got is None else 'MISMATCH')}")

pl = jwt_payload(real)
print("\ntoken 用户:", pl.get("name"), " 到期:", pl.get("exp"))
