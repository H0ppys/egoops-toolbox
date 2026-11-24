import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://mrobo.uav.meituan.com/egoops"


def q(params):
    url = BASE + "/api/v1/recordings?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    return j


tests = [
    ("默认近7天 record_date 11-13~11-19", {"record_date_from": "2026-11-13", "record_date_to": "2026-11-19"}),
    ("record_date 仅 11-17", {"record_date_from": "2026-11-17", "record_date_to": "2026-11-17"}),
    ("ingest 11-13~11-19", {"ingest_date_from": "2026-11-13", "ingest_date_to": "2026-11-19"}),
    ("ingest 仅 11-17", {"ingest_date_from": "2026-11-17", "ingest_date_to": "2026-11-17"}),
    ("record 近7天 + qc=pass", {"record_date_from": "2026-11-13", "record_date_to": "2026-11-19", "qc_status": "pass"}),
    ("tet_domain=commercial_service", {"tet_domain": "commercial_service"}),
]

for label, params in tests:
    try:
        j = q({**params, "page": 1, "size": 20})
        print(f"{label:44s} total={j.get('total')}")
    except Exception as e:
        print(f"{label:44s} ERROR {e}")

# 取一条完整记录看 UI 展示字段的映射
j = q({"record_date_from": "2026-11-13", "record_date_to": "2026-11-19", "page": 1, "size": 1})
it = j["items"][0]
for k in ("token_id", "task_name", "tet_node_path", "collector_name", "actor_name",
          "collect_mode", "duration_secs", "file_size_bytes", "qc_status", "qc_result",
          "created_at", "record_time", "void", "split_result", "human_qc_status", "anno_status"):
    print(f"  {k:18s} = {it.get(k)}")
