"""用保存的 token 查一下线上有没有「美宜佳」这个采集点（只读）。"""
import json
import os
import urllib.parse
import urllib.request

AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")
data = json.load(open(AUTH, encoding="utf-8"))
storage = data.get("storage") or {}

tok = None
for scope in ("session", "local"):
    for k, v in (storage.get(scope) or {}).items():
        if not v:
            continue
        if k.startswith("oidc.user") and '"access_token"' in v:
            tok = json.loads(v)["access_token"]
if not tok:
    print("没有 access_token")
    raise SystemExit(1)

BASE = "https://mrobo.uav.meituan.com/egoops"


def get(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", "Bearer " + tok)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


for status in ("draft,submitted,rejected,approved", "draft", "submitted"):
    q = urllib.parse.urlencode({"work_mode": "site_organization", "review_status": status,
                                "page": 1, "size": 5, "keyword": "美宜佳"})
    try:
        d = get("/api/v1/task-sets?" + q)
        recs = d.get("records") or []
        print("[%s] total=%s -> %s" % (status, d.get("total"), [r.get("name") for r in recs]))
    except Exception as e:
        print("[%s] 失败 %s" % (status, e))
