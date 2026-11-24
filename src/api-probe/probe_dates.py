import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://mrobo.uav.meituan.com/egoops"


def total(params):
    url = BASE + "/api/v1/recordings?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    return j.get("total"), len(j.get("items", []))


tests = [
    ("无过滤", {}),
    ("date_from=2026-11-17", {"date_from": "2026-11-17"}),
    ("date_from/date_to=2026-11-17", {"date_from": "2026-11-17", "date_to": "2026-11-17"}),
    ("date_from=2026-11-17 00:00:00", {"date_from": "2026-11-17 00:00:00", "date_to": "2026-11-17 23:59:59"}),
    ("date_from=2026-11-17T00:00:00", {"date_from": "2026-11-17T00:00:00", "date_to": "2026-11-17T23:59:59"}),
    ("近3天 11-17~11-19", {"date_from": "2026-11-17", "date_to": "2026-11-19"}),
    ("qc=pass", {"qc_status": "pass"}),
]

for label, params in tests:
    try:
        t, n = total({**params, "page": 1, "size": 20})
        print(f"{label:38s} total={t} page_items={n}")
    except Exception as e:
        print(f"{label:38s} ERROR {e}")
