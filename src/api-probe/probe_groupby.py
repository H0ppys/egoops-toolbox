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


cands = ["task_id", "task_name", "task", "tet_node_path", "tet_scene", "tet_action",
         "collector_name", "device_serial", "device_type", "vendor_id", "collect_mode"]
for gb in cands:
    try:
        j = get("/api/v1/recordings/group-stats", {"group_by": gb})
        items = j.get("items") or []
        print(f"[{gb:16s}] OK 分组数={len(items)}")
        if items:
            print("    样例:", json.dumps(items[0], ensure_ascii=False)[:260])
    except Exception as e:
        print(f"[{gb:16s}] {e}")
