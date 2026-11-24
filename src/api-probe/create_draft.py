"""用采集数据创建/更新一条 EgoOps 草稿（地址取自采集字段，不编造）。"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viewer"))
from agent_fill import generate_description, generate_task_content  # noqa: E402
from address_parse import parse as parse_addr  # noqa: E402
from transcode_pc import ensure_h264, codec_of  # noqa: E402

API = "https://mrobo.uav.meituan.com/egoops"
RELAY = "http://<FILL_ME>/relay"
AUTH = os.path.join(os.environ["APPDATA"], "egoops-viewer", "egoops_auth.json")
TMP = os.path.join(os.environ["TEMP"], "egoops-media")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def _tok():
    data = json.load(open(AUTH, encoding="utf-8"))
    for scope in ("session", "local"):
        for k, v in (data["storage"].get(scope) or {}).items():
            if v and k.startswith("oidc.user") and "access_token" in v:
                return json.loads(v)["access_token"]
    raise SystemExit("no token")


TOK = _tok()


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + TOK)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            txt = r.read().decode()
    except urllib.error.HTTPError as e:
        raise RuntimeError("%s %s -> %s %s" % (method, path, e.code, e.read().decode()[:300])) from None
    return json.loads(txt) if txt else {}


def download(f):
    os.makedirs(TMP, exist_ok=True)
    name = f.get("filename") or (f["id"] + ".bin")
    path = os.path.join(TMP, name)
    if os.path.exists(path) and os.path.getsize(path) == f.get("size"):
        return path
    with urllib.request.urlopen(RELAY + "/files/" + f["id"], timeout=300) as r, open(path, "wb") as out:
        out.write(r.read())
    return path


def upload_media(task_id, path, kind):
    business = "TASK_PHOTO" if kind == "photo" else "TASK_VIDEO"
    ct = "image/jpeg" if kind == "photo" else "video/mp4"
    r = api("POST", "/api/v1/media-assets/upload-url", {
        "owner_type": "TASK", "owner_id": task_id, "business_type": business,
        "filename": os.path.basename(path), "content_type": ct,
        "file_size": os.path.getsize(path),
    })
    mid, url = r["media_id"], r["upload_url"]
    with open(path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Content-Type", ct)
    with urllib.request.urlopen(req, timeout=600) as resp:
        if resp.status >= 300:
            raise RuntimeError("PUT " + str(resp.status))
    api("POST", "/api/v1/media-assets/%s/complete" % mid, {})
    return mid


def main():
    path = sys.argv[1]
    tsid = sys.argv[2] if len(sys.argv) > 2 else None
    site = json.load(open(path, encoding="utf-8"))

    addr_text = (site.get("address") or "").strip()
    parts = parse_addr(addr_text)
    full_addr = (parts["province"] + parts["city"] + parts["district"] + parts["street"]) if parts["ok"] else addr_text
    log("采集数据里的地址:", repr(addr_text), "| 拆解:", parts["province"], parts["city"], parts["district"], parts["street"], "| ok", parts["ok"])

    desc, _ = generate_description(site)
    real_tasks = [t for t in (site.get("tasks") or []) if (t.get("name") or "") != "采集点-门头与全景"]
    tk = real_tasks[0] if real_tasks else (site.get("tasks") or [{}])[-1]
    label = ((tk.get("area") + " ") if (tk.get("area") or "").strip() else "") + (tk.get("name") or "")
    content, _ = generate_task_content(site, tk)
    log("任务:", label, "| 照片", len(tk.get("photos") or []), "视频", len(tk.get("videos") or []))

    if not tsid:
        tsid = api("POST", "/api/v1/task-sets/allocate-draft", {}).get("task_set_id")
        log("新建草稿:", tsid)
    else:
        log("更新草稿:", tsid)

    api("PATCH", "/api/v1/task-sets/%s" % tsid, {
        "name": site.get("name") or "",
        "address": full_addr,
        "tet_node_path": site.get("scene") or "",
        "description": desc,
    })
    log("✓ 采集点字段（含地址）")

    recs = api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid).get("records") or []
    if recs:
        tid = recs[0].get("task_id")
    else:
        nt = api("POST", "/api/v1/task-sets/%s/tasks/allocate-draft" % tsid, {})
        tid = nt.get("task_id") or (nt.get("task") or {}).get("task_id")
    log("任务 id:", tid)

    photos, videos = [], []
    for f in (tk.get("photos") or [])[:9]:
        photos.append(upload_media(tid, download(f), "photo"))
    for f in (tk.get("videos") or [])[:3]:
        path = download(f)
        codec = codec_of(path)
        if codec == "hevc":
            log("   转码 H.265 → H.264:", os.path.basename(path))
            path = ensure_h264(path)
            log("   转码完成", round(os.path.getsize(path) / 1048576, 2), "MB")
        videos.append(upload_media(tid, path, "video"))
    log("✓ 媒体 照片", len(photos), "视频", len(videos))

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

    ts = api("GET", "/api/v1/task-sets/%s" % tsid)
    t2 = (api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid).get("records") or [{}])[0]
    print()
    log("== 回查 ==")
    log("  草稿", tsid, "|", ts.get("name"), "| 状态", ts.get("review_status"))
    log("  地址:", repr(ts.get("address")))
    log("  场景:", ts.get("tet_node_path"))
    log("  任务:", t2.get("task_name"), "| 时长", t2.get("required_duration"), "| 照片", len(t2.get("task_photos") or []), "| 视频", len(t2.get("task_videos") or []))


if __name__ == "__main__":
    main()
