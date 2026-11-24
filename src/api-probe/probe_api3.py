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
        return r.status, json.loads(r.read().decode("utf-8", "replace"))


status, j = get("/api/v1/recordings", {"page": 1, "size": 5})
print("envelope keys:", list(j.keys()))
for k, v in j.items():
    if k != "items":
        print(f"  {k} = {v}")
print("items:", len(j.get("items", [])))
print("item keys:", list(j["items"][0].keys()) if j.get("items") else [])

# 翻页验证
_, j2 = get("/api/v1/recordings", {"page": 2, "size": 5})
ids1 = [x["token_id"] for x in j.get("items", [])]
ids2 = [x["token_id"] for x in j2.get("items", [])]
print("\npage1 ids:", ids1[:2])
print("page2 ids:", ids2[:2])
print("两页是否重叠:", bool(set(ids1) & set(ids2)))

# 抓一页大 size 看上限
for s in (100, 200):
    try:
        st, jj = get("/api/v1/recordings", {"page": 1, "size": s})
        print(f"size={s} -> status={st} items={len(jj.get('items', []))} total={jj.get('total')}")
    except Exception as e:
        print(f"size={s} -> ERROR {e}")

# refresh token 检查
import glob
import os
for f in glob.glob(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\edge_ss\*"):
    if os.path.isdir(f):
        continue
    data = open(f, "rb").read()
    for key in (b"refresh_token", b"r\x00e\x00f\x00r\x00e\x00s\x00h\x00_\x00t\x00o\x00k\x00e\x00n"):
        if key in data:
            print(f"\n{os.path.basename(f)} 含 refresh_token 标记: {key!r}")
