import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://mrobo.uav.meituan.com/egoops"


def get(path, params=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


print("=== /api/v1/recordings/stats ===")
print(json.dumps(get("/api/v1/recordings/stats"), ensure_ascii=False)[:800])

for gb in ("actor_name", "actor", "executor"):
    try:
        j = get("/api/v1/recordings/group-stats", {"group_by": gb})
        s = json.dumps(j, ensure_ascii=False)
        print(f"\n=== group_by={gb} === len={len(s)}")
        print(s[:900])
    except Exception as e:
        print(f"\n=== group_by={gb} === ERROR {e}")
