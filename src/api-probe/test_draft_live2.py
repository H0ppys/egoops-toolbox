"""对最新的「盛宴公寓」跑一遍完整建草稿，看真实失败点。"""
import sys

sys.path.insert(0, "viewer")

import egoops_auth as ea            # noqa: E402
import egoops_draft as ed          # noqa: E402
from api import Api                # noqa: E402

RELAY = "https://<FILL_ME>/relay"


def main():
    r = Api(RELAY)
    r.login("实测2")
    site = next(s for s in r.sites() if s["name"] == "盛宴公寓")
    detail = r.site(site["id"])
    print("采集点:", detail["name"], "| 场景:", detail.get("scene_label"))
    for t in detail["tasks"]:
        print("  %r / %r 照片%d 视频%d" % (t.get("area"), t.get("name"),
                                          len(t.get("photos") or []), len(t.get("videos") or [])))
    payload = dict(detail)
    for t in payload["tasks"]:
        for f in (t.get("photos") or []) + (t.get("videos") or []):
            f["url"] = RELAY + "/files/" + f["id"]

    res = ed.create_draft(payload, log=lambda m: print(m, flush=True), progress=lambda p, t: None)
    print("\n结果:", res["task_set_id"], res["tasks"])

    tok = ea.token_of()
    rows = ed._api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % res["task_set_id"],
                   token=tok).get("records") or []
    print("\n回查:")
    for t in rows:
        print("  %-26s 照片%d 视频%d SOP%d" % (t.get("task_name"),
              len(t.get("task_photos") or []), len(t.get("task_videos") or []),
              len((t.get("sop") or {}).get("steps") or [])))


if __name__ == "__main__":
    main()
