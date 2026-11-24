import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://mrobo.uav.meituan.com/egoops"


def total(params):
    url = BASE + "/api/v1/recordings?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())["total"]


cases = [
    ("11-13~11-19", "2026-11-13", "2026-11-19"),
    ("11-13~11-18", "2026-11-13", "2026-11-18"),
    ("11-17~11-18", "2026-11-17", "2026-11-18"),
    ("11-17~11-19", "2026-11-17", "2026-11-19"),
    ("11-16~11-17", "2026-11-16", "2026-11-17"),
    ("11-18~11-19", "2026-11-18", "2026-11-19"),
    ("11-10~11-16", "2026-11-10", "2026-11-16"),
    ("11-01~11-30", "2026-11-01", "2026-11-30"),
]
for label, a, b in cases:
    print(f"{label:16s} total={total({'record_date_from': a, 'record_date_to': b, 'page': 1, 'size': 20})}")

print()
print("=== 带时间的格式 ===")
for label, a, b in [("11-17 00:00 ~ 11-19 23:59", "2026-11-17 00:00:00", "2026-11-19 23:59:59")]:
    print(f"{label:28s} total={total({'record_date_from': a, 'record_date_to': b, 'page': 1, 'size': 20})}")

print()
print("=== 最新数据的 record_date 分布（不限日期，取前 3 页）===")
from collections import Counter
c = Counter()
for page in (1, 2, 3):
    url = BASE + "/api/v1/recordings?" + urllib.parse.urlencode({"page": page, "size": 20, "sort": "record_time:desc"})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode())
    for it in j["items"]:
        c[str(it.get("record_time"))[:10]] += 1
print(dict(c))
