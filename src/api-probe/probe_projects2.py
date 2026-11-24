import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://mrobo.uav.meituan.com/egoops"


def get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


p = get("/api/v1/projects", {"size": 100})
recs = p["records"]
print("第一条项目原始结构:")
print(json.dumps(recs[0], ensure_ascii=False)[:800])

print("\n=== 名称含 盛宴/MT/MTSY 的项目 ===")
for r in recs:
    name = str(r.get("name") or "")
    if any(k in name for k in ("盛宴", "MT", "mtsy", "MTSY", "美团")):
        print(f"  {r}")

print("\n=== 全部项目名 ===")
print(" | ".join(str(r.get("name")) for r in recs[:40]))
