"""看 EgoOps 的 TET 分类树到底有几层。"""
import json
import sys
import urllib.request

sys.path.insert(0, "viewer")
import egoops_auth as ea
import tls

tok = ea.token_of()
req = urllib.request.Request("https://mrobo.uav.meituan.com/egoops/api/v1/tet-snapshots/active")
req.add_header("Authorization", "Bearer " + tok)
data = json.loads(tls.urlopen(req, timeout=30).read())
io_root = data.get("data") or data
nodes = io_root.get("nodes") if isinstance(io_root, dict) else None
if not nodes:
    print("返回结构:", list(data.keys())[:5], str(data)[:300])
    sys.exit(0)

print("顶层节点数:", len(nodes))


def depth(node, d=1):
    kids = node.get("children") or {}
    if not kids:
        return d, 1
    mx, cnt = d, 0
    for k, v in kids.items():
        dd, cc = depth(v, d + 1)
        mx = max(mx, dd)
        cnt += cc
    return mx, max(cnt, len(kids))


for k, v in list(nodes.items())[:3]:
    print(" 顶层:", k, v.get("name_zh"), "| children:", len(v.get("children") or {}))
    for k2, v2 in list((v.get("children") or {}).items())[:3]:
        print("   二层:", k2, v2.get("name_zh"), "| children:", len(v2.get("children") or {}))
        for k3, v3 in list((v2.get("children") or {}).items())[:3]:
            print("     三层:", k3, v3.get("name_zh"), "| children:", len(v3.get("children") or {}))

maxd, _ = depth({"children": nodes})
print("\n最大层级:", maxd)
