"""实测：对「盛宴便利店」跑一遍多任务建草稿，并回查每个任务。"""
import json
import sys

sys.path.insert(0, "viewer")

import egoops_draft as ed          # noqa: E402
import egoops_auth as ea           # noqa: E402
from api import Api                # noqa: E402
from egoops_status import fetch_one  # noqa: E402

RELAY = "https://<FILL_ME>/relay"


def main():
    r = Api(RELAY)
    r.login("实测")
    site = next(s for s in r.sites() if s["name"] == "盛宴便利店")
    detail = r.site(site["id"])
    print("采集点:", detail["name"], "| 地址:", detail["address"], "| 场景:", detail["scene_label"])
    for t in detail["tasks"]:
        print("  任务: %r / %r -> 照片 %d, 视频 %d" % (
            t.get("area"), t.get("name"), len(t.get("photos") or []), len(t.get("videos") or [])))

    payload = dict(detail)
    for t in payload["tasks"]:
        for f in (t.get("photos") or []) + (t.get("videos") or []):
            f["url"] = RELAY + "/files/" + f["id"]

    res = ed.create_draft(payload, log=lambda m: print(m, flush=True),
                          progress=lambda p, t: None)
    print("\n== 结果 ==")
    print("草稿:", res["task_set_id"], "| 任务数:", len(res["tasks"]))
    for t in res["tasks"]:
        print("  · %s -> 照片 %d, 视频 %d, SOP %d 步" % (t["name"], t["photos"], t["videos"], t["sop"]))

    print("\n== 回查 EgoOps ==")
    tok = ea.token_of()
    tasks = ed._api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % res["task_set_id"],
                    token=tok).get("records") or []
    for t in tasks:
        print("  %-24s 照片 %d | 视频 %d | SOP %d | 时长 %s" % (
            t.get("task_name"), len(t.get("task_photos") or []), len(t.get("task_videos") or []),
            len((t.get("sop") or {}).get("steps") or []), t.get("required_duration")))
    st = fetch_one(res["task_set_id"], tok)
    print("  状态:", st)


if __name__ == "__main__":
    main()
