"""模拟查看器：拉列表 → 厂商解析 → 质检 → 导出 → 建草稿。"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))

import extras
from api import Api
import egoops_draft

BASE = "https://<FILL_ME>/relay"
VERBOSE = True


def log(*a):
    if VERBOSE:
        print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    site_id = open("sim/site_id.txt").read().strip()
    a = Api(BASE)
    a.login("查看器模拟")
    items = a.sites()
    site = next((x for x in items if x["id"] == site_id), None)
    if not site:
        print("找不到模拟采集点"); return

    print("\n== 1. 列表 ==")
    print("  名称:", site["name"], "| 邀请码:", site.get("invite"), "| 厂商映射:", end=" ")
    cfg_path = os.path.join(os.environ["APPDATA"], "egoops-viewer", "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    invites = {k.upper(): v for k, v in (cfg.get("invites") or {}).items()}
    print(invites.get((site.get("invite") or "").upper(), "（未配置）"))

    detail = a.site(site_id)
    files = []
    for t in detail.get("tasks") or []:
        files += (t.get("photos") or []) + (t.get("videos") or [])

    print("\n== 2. 质检 ==")
    issues = extras.check_site(detail, files,
                               lambda f: extras.fetch_to_temp(BASE, a.token, f, "sim"))
    for it in issues:
        print("  [%s] %-28s %s" % (it["level"], it["file"].get("filename"), it["kind"] + " · " + it["reason"]))
    print("  共 %d 条问题（严重 %d）" % (len(issues), sum(1 for i in issues if i["level"] == "error")))

    print("\n== 3. 导出表格 ==")
    rows = []
    for it in items:
        d = a.site(it["id"])
        photos = sum(len(t.get("photos") or []) for t in d.get("tasks") or [])
        videos = sum(len(t.get("videos") or []) for t in d.get("tasks") or [])
        rows.append({"name": it["name"], "vendor": invites.get((it.get("invite") or "").upper(), "—"),
                     "invite": it.get("invite", ""), "address": it.get("address", ""),
                     "area": it.get("area"), "scene": it.get("scene_label", ""),
                     "by": it.get("created_by", ""), "created": (it.get("created_at") or "")[:16],
                     "tasks": it.get("task_count", 0), "photos": photos, "videos": videos,
                     "bytes": it.get("bytes", 0), "draft": "未建"})
    extras.export_sites_csv(rows, "sim/export.csv")
    print("  已导出 sim/export.csv")
    print(open("sim/export.csv", encoding="utf-8-sig").read().strip())

    print("\n== 4. 一键建草稿（只建草稿，不提交） ==")
    payload = dict(detail)
    for t in payload.get("tasks") or []:
        for f in (t.get("photos") or []) + (t.get("videos") or []):
            f["url"] = BASE + "/files/" + f["id"]

    def prog(pct, text):
        print("  [%3d%%] %s" % (pct, text))

    res = egoops_draft.create_draft(payload, log=log, progress=prog)
    extras.remember(site_id, res["task_set_id"], res.get("name", ""))
    print("\n  草稿:", res["task_set_id"], "| 照片", res["photos"], "| 视频", res["videos"],
          "| SOP", len(res["sop"]), "步")
    json.dump(res, open("sim/draft_result.json", "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
