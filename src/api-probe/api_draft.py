"""用接口创建一份「申请采集点」草稿（等价于点页面填写后保存草稿），只建草稿、不提交审核。"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402
from address_parse import parse as parse_addr  # noqa: E402

BASE = "https://mrobo.uav.meituan.com/egoops"
AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def token():
    data = json.load(open(AUTH, encoding="utf-8"))
    for scope in ("session", "local"):
        for k, v in (data["storage"].get(scope) or {}).items():
            if v and k.startswith("oidc.user") and "access_token" in v:
                return json.loads(v)["access_token"]
    raise SystemExit("没有 token")


TOK = token()


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("Accept", "application/json, text/plain, */*")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            txt = r.read().decode()
    except urllib.error.HTTPError as e:
        raise RuntimeError("%s %s -> %s %s" % (method, path, e.code, e.read().decode()[:300])) from None
    return json.loads(txt) if txt else {}


def main():
    site = json.load(open(sys.argv[1], encoding="utf-8"))
    tasks_in = site.get("tasks") or []
    addr = parse_addr("广东省湛江市赤坎区人民大道88号")
    full_addr = addr["province"] + addr["city"] + addr["district"] + addr["street"]

    if len(sys.argv) > 2:
        tsid = sys.argv[2]
        log("1) 复用已有草稿", tsid)
    else:
        log("1) 建草稿")
        draft = call("POST", "/api/v1/task-sets/allocate-draft", {})
        tsid = draft.get("task_set_id")
        log("   task_set_id =", tsid, "| 初始状态", draft.get("review_status"))

    log("2) 查默认任务")
    tl = call("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid)
    recs = tl.get("records") or []
    if not recs:
        log("   没有默认任务，创建一个")
        nt = call("POST", "/api/v1/task-sets/%s/tasks/allocate-draft" % tsid, {})
        default_task = nt if nt.get("task_id") else (nt.get("task") or {})
        if not default_task.get("task_id"):
            tl2 = call("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid)
            default_task = (tl2.get("records") or [{}])[0]
    else:
        default_task = recs[0]
    log("   默认任务", default_task.get("task_id"))

    desc, _ = generate_description(site)
    log("3) 填采集点字段")
    call("PATCH", "/api/v1/task-sets/%s" % tsid, {
        "name": site.get("name") or "",
        "address": full_addr,
        "tet_node_path": site.get("scene") or "restaurant/restaurant",
        "description": desc,
    })
    log("   名称/地址/场景/描述 已写入")

    tk = tasks_in[0] if tasks_in else {"name": "任务1"}
    content, _ = generate_task_content(site, tk)
    log("4) 填任务")
    call("PATCH", "/api/v1/tasks/%s" % default_task.get("task_id"), {
        "task_name": tk.get("name") or "任务1",
        "tet_node_path": site.get("scene") or "restaurant/restaurant",
        "description": content["desc"],
        "required_duration": int(float(content["hours"]) * 3600),
        "collect_mode": "passive",
        "sop": {"steps": content["sop"]},
    })
    log("   任务名/描述/时长/SOP 已写入")

    log("5) 回查")
    got = call("GET", "/api/v1/task-sets/%s" % tsid)
    log("   名称:", got.get("name"))
    log("   地址:", got.get("address"))
    log("   场景:", got.get("tet_node_path"))
    log("   状态:", got.get("review_status"))
    log("   描述:", (got.get("description") or "")[:60], "...")
    print("\n草稿 ID:", tsid, "（在 EgoOps 申报 → 草稿 里能看到）")


if __name__ == "__main__":
    main()
