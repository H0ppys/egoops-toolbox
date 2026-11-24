"""把草稿修正成正确内容：真实任务名、真实素材上传、地址不编造。"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_task_content  # noqa: E402

API = "https://mrobo.uav.meituan.com/egoops"
RELAY = "http://<FILL_ME>/relay"
AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")
TMP = os.path.join(os.environ["TEMP"], "egoops-media")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def token():
    data = json.load(open(AUTH, encoding="utf-8"))
    for scope in ("session", "local"):
        for k, v in (data["storage"].get(scope) or {}).items():
            if v and k.startswith("oidc.user") and "access_token" in v:
                return json.loads(v)["access_token"]
    raise SystemExit("no token")


TOK = token()


def api(method, path, body=None, base=API, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if base == API:
        req.add_header("Authorization", "Bearer " + TOK)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
    except urllib.error.HTTPError as e:
        raise RuntimeError("%s %s -> %s %s" % (method, path, e.code, e.read().decode()[:300])) from None
    return json.loads(txt) if txt else {}


def upload_media(task_id, path, kind):
    business = "TASK_PHOTO" if kind == "photo" else "TASK_VIDEO"
    ct = "image/jpeg" if kind == "photo" else "video/mp4"
    size = os.path.getsize(path)
    r = api("POST", "/api/v1/media-assets/upload-url", {
        "owner_type": "TASK", "owner_id": task_id, "business_type": business,
        "filename": os.path.basename(path), "content_type": ct, "file_size": size,
    })
    media_id, url = r.get("media_id"), r.get("upload_url")
    with open(path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Content-Type", ct)
    with urllib.request.urlopen(req, timeout=600) as resp:
        if resp.status >= 300:
            raise RuntimeError("PUT %s" % resp.status)
    api("POST", "/api/v1/media-assets/%s/complete" % media_id, {})
    return media_id


def main():
    tsid = sys.argv[1]
    site = json.load(open(sys.argv[2], encoding="utf-8"))

    # 只取真实的「区域任务」，跳过采集点级那个占位任务
    real_tasks = [t for t in (site.get("tasks") or []) if (t.get("name") or "") != "采集点-门头与全景"]
    tk = real_tasks[0] if real_tasks else (site.get("tasks") or [{}])[-1]
    log("用这个任务填：", (tk.get("area") or "-"), tk.get("name"),
        "| 照片", len(tk.get("photos") or []), "视频", len(tk.get("videos") or []))

    content, _ = generate_task_content(site, tk)
    label = ((tk.get("area") + " ") if (tk.get("area") or "").strip() else "") + (tk.get("name") or "")

    log("1) 改采集点：地址不编造，留空待人工补")
    api("PATCH", "/api/v1/task-sets/%s" % tsid, {
        "name": site.get("name") or "",
        "address": "",
        "tet_node_path": site.get("scene") or "",
        "description": site.get("note") or "",
    })

    tasks = api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid).get("records") or []
    if not tasks:
        nt = api("POST", "/api/v1/task-sets/%s/tasks/allocate-draft" % tsid, {})
        tid = nt.get("task_id") or (nt.get("task") or {}).get("task_id")
    else:
        tid = tasks[0].get("task_id")
    log("2) 任务 id =", tid)

    log("3) 上传素材（走平台 upload-url → PUT → complete）")
    photos, videos = [], []
    for f in (tk.get("photos") or [])[:9]:
        p = download(f)
        photos.append(upload_media(tid, p, "photo"))
        log("   照片", os.path.basename(p), "->", photos[-1])
    for f in (tk.get("videos") or [])[:3]:
        p = download(f)
        videos.append(upload_media(tid, p, "video"))
        log("   视频", os.path.basename(p), "->", videos[-1])

    log("4) 写任务内容 + 挂素材")
    api("PATCH", "/api/v1/tasks/%s" % tid, {
        "task_name": label,
        "tet_node_path": site.get("scene") or "",
        "description": content["desc"],
        "required_duration": int(float(content["hours"]) * 3600),
        "collect_mode": "passive",
        "sop": {"steps": content["sop"]},
        "task_photos": photos,
        "task_videos": videos,
    })

    log("5) 回查")
    ts = api("GET", "/api/v1/task-sets/%s" % tsid)
    t2 = (api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid).get("records") or [{}])[0]
    log("   采集点:", ts.get("name"), "| 地址:", repr(ts.get("address")), "| 场景:", ts.get("tet_node_path"))
    log("   任务:", t2.get("task_name"), "| 照片", len(t2.get("task_photos") or []), "| 视频", len(t2.get("task_videos") or []))
    log("   状态:", ts.get("review_status"))


def download(f):
    os.makedirs(TMP, exist_ok=True)
    name = f.get("filename") or (f["id"] + ".bin")
    path = os.path.join(TMP, name)
    if os.path.exists(path) and os.path.getsize(path) == f.get("size"):
        return path
    with urllib.request.urlopen(RELAY + "/files/" + f["id"], timeout=300) as r, open(path, "wb") as out:
        out.write(r.read())
    return path


if __name__ == "__main__":
    main()
