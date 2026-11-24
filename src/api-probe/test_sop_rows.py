"""把「看图」生成的任务名/描述/SOP 写进已有草稿，验证 EgoOps 里是分开的多行。"""
import json
import sys
import time

sys.path.insert(0, "viewer")

import agent_fill as af  # noqa: E402
import egoops_auth as ea  # noqa: E402
import extras  # noqa: E402
import urllib.request  # noqa: E402

API = "https://mrobo.uav.meituan.com/egoops"
RELAY = "https://<FILL_ME>/relay"
TSID = "105525515"


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + ea.token_of())
    with urllib.request.urlopen(req, timeout=90) as r:
        t = r.read().decode()
    return json.loads(t) if t else {}


def main():
    from api import Api
    r = Api(RELAY)
    r.login("看图写SOP")
    site = r.sites()[0]
    detail = r.site(site["id"])
    task = [t for t in detail["tasks"] if t["name"] != "采集点-门头与全景"][0]
    photos = [extras.fetch_to_temp(RELAY, r.token, f, "vis5") for f in task["photos"][:4]]
    videos = [extras.fetch_to_temp(RELAY, r.token, f, "vis5") for f in task["videos"][:2]]

    t0 = time.time()
    content, src = af.generate_task_content_from_media(detail, task, photos, videos)
    print("来源:", src, "| %.0fs" % (time.time() - t0))
    print("任务名称:", content.get("name"))
    print("描述:", content["desc"])
    print("SOP %d 条:" % len(content["sop"]))
    for i, x in enumerate(content["sop"], 1):
        print("  %d. %s" % (i, x))

    tasks = api("GET", f"/api/v1/task-sets/{TSID}/tasks?include_stats=false&include_assignments=false").get("records") or []
    tid = tasks[0]["task_id"]
    api("PATCH", "/api/v1/tasks/" + tid, {
        "task_name": content.get("name") or task["name"],
        "description": content["desc"],
        "required_duration": int(float(content["hours"]) * 3600),
        "sop": {"steps": content["sop"]},
    })
    got = (api("GET", f"/api/v1/task-sets/{TSID}/tasks?include_stats=false&include_assignments=false").get("records") or [{}])[0]
    print("\n== 回查 ==")
    print("任务名:", got.get("task_name"))
    steps = (got.get("sop") or {}).get("steps") or []
    print("SOP 条数:", len(steps))
    for i, x in enumerate(steps, 1):
        print("  第 %d 行: %s" % (i, x))


if __name__ == "__main__":
    main()
