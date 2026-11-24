"""用 GLM 生成的描述/SOP 更新 EgoOps 草稿（只改草稿，不提交）。"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402

API = "https://mrobo.uav.meituan.com/egoops"
AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")


def tok():
    d = json.load(open(AUTH, encoding="utf-8"))
    for sc in ("session", "local"):
        for k, v in (d["storage"].get(sc) or {}).items():
            if v and k.startswith("oidc.user") and "access_token" in v:
                return json.loads(v)["access_token"]
    raise SystemExit("no token")


TOK = tok()


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + TOK)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
    except urllib.error.HTTPError as e:
        raise RuntimeError("%s %s -> %s %s" % (method, path, e.code, e.read().decode()[:300])) from None
    return json.loads(txt) if txt else {}


def main():
    tsid = sys.argv[1]
    site_path = sys.argv[2]
    site = json.load(open(site_path, encoding="utf-8"))

    real = [t for t in (site.get("tasks") or []) if (t.get("name") or "") != "采集点-门头与全景"]
    tk = real[0] if real else (site.get("tasks") or [{}])[0]
    label = ((tk.get("area") + " ") if (tk.get("area") or "").strip() else "") + (tk.get("name") or "")

    desc, src1 = generate_description(site)
    content, src2 = generate_task_content(site, tk)
    print("来源:", src1, src2, "| 任务:", label, "| 时长", content["hours"])

    cur = api("GET", "/api/v1/task-sets/%s" % tsid)
    api("PATCH", "/api/v1/task-sets/%s" % tsid, {
        "name": cur.get("name") or site.get("name"),
        "address": cur.get("address") or "",
        "tet_node_path": cur.get("tet_node_path") or site.get("scene") or "",
        "description": desc,
    })

    tasks = api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid).get("records") or []
    tid = tasks[0].get("task_id")
    api("PATCH", "/api/v1/tasks/%s" % tid, {
        "task_name": label,
        "tet_node_path": cur.get("tet_node_path") or site.get("scene") or "",
        "description": content["desc"],
        "required_duration": int(float(content["hours"]) * 3600),
        "collect_mode": "passive",
        "sop": {"steps": content["sop"]},
    })

    got = api("GET", "/api/v1/task-sets/%s" % tsid)
    t2 = (api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid).get("records") or [{}])[0]
    print("\n== 回查 ==")
    print("采集点:", got.get("name"), "| 状态", got.get("review_status"))
    print("描述:", (got.get("description") or "")[:80], "…")
    print("任务:", t2.get("task_name"), "| 时长", t2.get("required_duration"), "秒")
    print("任务描述:", (t2.get("description") or "")[:80], "…")
    print("SOP:")
    for i, s in enumerate((t2.get("sop") or {}).get("steps") or [], 1):
        print("  %d. %s" % (i, s))


if __name__ == "__main__":
    main()
