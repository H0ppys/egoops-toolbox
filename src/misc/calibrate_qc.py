"""下载真实照片，看看清晰度/亮度分布，用来校准阈值。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
import extras  # noqa: E402

import json
import urllib.request

BASE = "http://<FILL_ME>/relay"


def main():
    login = json.loads(urllib.request.urlopen(urllib.request.Request(
        BASE + "/api/auth/login",
        data=json.dumps({"name": "校准"}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")).read())
    token = login["token"]
    h = {"Authorization": "Bearer " + token}
    sites = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/api/sites", headers=h)).read())["items"]
    vals = []
    for s in sites:
        detail = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/api/sites/" + s["id"], headers=h)).read())
        for t in detail.get("tasks") or []:
            for f in t.get("photos") or []:
                p = extras.fetch_to_temp(BASE, token, f, "calib")
                m = extras.photo_metrics(p)
                if m:
                    vals.append((f.get("filename"), m["blur"], m["bright"]))
    vals.sort(key=lambda x: x[1])
    print("照片数:", len(vals))
    for name, blur, bright in vals:
        print("  %-28s blur=%7.1f bright=%5.1f" % (name, blur, bright))

    vids = []
    for s in sites:
        detail = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/api/sites/" + s["id"], headers=h)).read())
        for t in detail.get("tasks") or []:
            for f in t.get("videos") or []:
                p = extras.fetch_to_temp(BASE, token, f, "calib")
                m = extras.video_metrics(p)
                if m:
                    vids.append((f.get("filename"), m))
    print("\n视频:")
    for name, m in vids:
        print("  %-28s %.1fs %dx%d" % (name, m["duration"], m["width"], m["height"]))


if __name__ == "__main__":
    main()
