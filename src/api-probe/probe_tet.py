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


for gb in ("tet_task", "collector", "device", "task_set"):
    try:
        j = get("/api/v1/recordings/group-stats", {"group_by": gb})
        items = j.get("items") or []
        print(f"\n[{gb}] 分组数={len(items)} group_by={j.get('group_by')}")
        for it in items[:4]:
            print("   ", json.dumps(it, ensure_ascii=False)[:420])
    except Exception as e:
        print(f"\n[{gb}] ERROR {e}")
