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


print("=== vendors ===")
try:
    v = get("/api/v1/vendors", {"size": 100})
    recs = v.get("records") or v.get("items") or []
    print("数量:", len(recs), "keys:", list(v.keys()))
    for r in recs[:10]:
        print("  ", json.dumps(r, ensure_ascii=False)[:200])
except Exception as e:
    print("  vendors 读取失败:", e)

print("\n=== vendor_id 过滤 ===")
for vid in ("tenant_8a4ea824",):
    for label, extra in [
        ("仅 vendor", {}),
        ("vendor + 近7天 record_date", {"record_date_from": "2026-11-13", "record_date_to": "2026-11-19"}),
        ("vendor + ingest 11-17", {"ingest_date_from": "2026-11-17", "ingest_date_to": "2026-11-17"}),
    ]:
        try:
            j = get("/api/v1/recordings", {"page": 1, "size": 20, "vendor_id": vid, **extra})
            print(f"  {vid} {label:30s} total={j.get('total')}")
        except Exception as e:
            print(f"  {vid} {label:30s} ERROR {e}")

print("\n=== 当前数据里出现的 vendor_id 分布（前 3 页）===")
seen = {}
for page in (1, 2, 3):
    j = get("/api/v1/recordings", {"page": page, "size": 20, "record_date_from": "2026-11-13", "record_date_to": "2026-11-19"})
    for it in j["items"]:
        seen[it["vendor_id"]] = seen.get(it["vendor_id"], 0) + 1
print(seen)
