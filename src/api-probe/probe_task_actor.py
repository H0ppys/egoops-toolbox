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


print("=== 任务 1041042328 下的执行者分组 ===")
j = get("/api/v1/recordings/group-stats", {"group_by": "actor_name", "task_id": "1041042328"})
items = j.get("items") or []
print("分组数:", len(items))
for it in items:
    d = float(it.get("total_duration_secs") or 0)
    p = float(it.get("qc_pass_duration_secs") or 0)
    print(f"  {it.get('group_name'):<8} 条数={it.get('recording_count'):>5} 时长={d/3600:6.2f}h 通过={p/3600:6.2f}h 合格率={p/d*100 if d else 0:5.1f}%")

print("\n=== 对照：唐朝阳 的数值应为 523 条 / 31.9h / 81% ===")
