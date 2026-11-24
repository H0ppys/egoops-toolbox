import json
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://mrobo.uav.meituan.com/egoops"


def get(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


j = get("/api/v1/tet-snapshots/active")
s = json.dumps(j, ensure_ascii=False)
print("长度:", len(s))
print(s[:2500])
