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


print("=== 项目列表 ===")
p = get("/api/v1/projects", {"size": 100})
items = p.get("items") or p.get("records") or []
print("envelope:", list(p.keys()), "数量:", len(items))
for it in items[:20]:
    print(f"  id={it.get('id')} name={it.get('name')} code={it.get('code')}")

print("\n=== 用 project_id 过滤后的总数 ===")
pid = items[0].get("id") if items else None
for it in items[:5]:
    j = get("/api/v1/recordings", {"page": 1, "size": 20, "project_id": it.get("id")})
    print(f"  project {it.get('name')} ({it.get('id')}): total={j.get('total')}")

print("\n=== 试其他过滤参数（看 total 是否变化）===")
base_total = get("/api/v1/recordings", {"page": 1, "size": 20}).get("total")
print("  无过滤 total =", base_total)
for params in [
    {"created_from": "2026-11-17"},
    {"created_after": "2026-11-17"},
    {"start_date": "2026-11-17"},
    {"record_date": "2026-11-17"},
    {"qc_status": "pass"},
    {"tet_node_path": "commercial_service/nursing_home"},
]:
    try:
        j = get("/api/v1/recordings", {"page": 1, "size": 20, **params})
        print(f"  {params} -> total={j.get('total')}")
    except Exception as e:
        print(f"  {params} -> ERROR {e}")
