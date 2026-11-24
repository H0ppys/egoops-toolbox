"""美团「申请采集点」：按区域逐个建 EgoOps 任务（每个任务带自己的素材和看图 SOP）。

之前的做法只建一个任务，把第一个区域的内容塞进去，其它区域直接丢掉了。
现在：
  采集点字段（名称/地址/场景/描述）→ 写一次
  每个任务（含采集点级的门头与全景）→ 各建一条 EgoOps 任务，各自上传素材、各自看图写 SOP
"""

import io

p = 'viewer/egoops_draft.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('def create_draft(')
end = s.index('def _download(f):')

new = '''def create_draft(site, relay_files=None, log=print, progress=None, token=None):
    """site: 采集点详情（含 tasks[].photos/videos）
    每个 task 都会在 EgoOps 里建一条作业任务，素材和 SOP 各归各的。
    """
    token = token or _token()
    site_name = site.get("name") or ""
    tasks = site.get("tasks") or []
    if not tasks:
        raise DraftError("这个采集点还没有任何任务")

    def step(pct, text):
        if progress:
            progress(pct, text)
        log(text)

    # ---------- 采集点级字段 ----------
    step(2, "读取采集点数据…")
    addr_text = (site.get("address") or "").strip()
    parts = parse_addr(addr_text)
    if parts["ok"]:
        full_addr = "%s %s %s %s" % (parts["province"], "" if parts["city"] == "市辖区" else parts["city"],
                                     parts["district"], parts["street"])
        full_addr = full_addr.replace("  ", " ").strip()
    else:
        full_addr = addr_text
        if addr_text:
            log("  地址拆不开（%s），原样写入" % parts.get("note"))
    if not addr_text:
        log("  ⚠ 没有现场地址，草稿里会留空")

    step(6, "生成采集点描述…")
    desc, src = generate_description(site)
    log("  描述来源：%s" % ("大模型" if src == "llm" else "模板"))

    step(10, "建草稿…")
    tsid = _api("POST", "/api/v1/task-sets/allocate-draft", {}, token=token).get("task_set_id")
    log("  草稿 id = %s" % tsid)

    step(14, "写采集点字段…")
    cur = _api("GET", "/api/v1/task-sets/%s" % tsid, token=token)
    _api("PATCH", "/api/v1/task-sets/%s" % tsid, {
        "name": site_name,
        "address": full_addr,
        "tet_node_path": site.get("scene") or cur.get("tet_node_path") or "",
        "description": desc,
    }, token=token)
    log("  名称 / 地址 / 场景 / 描述 已写入")

    # ---------- 逐个任务 ----------
    existing = _api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid,
                    token=token).get("records") or []
    made = []
    total_tasks = len(tasks)
    for ti, task in enumerate(tasks, 1):
        base_pct = 14 + int(80 * (ti - 1) / total_tasks)
        area = (task.get("area") or "").strip()
        name = (task.get("name") or "").strip() or ("任务%d" % ti)
        label = (area + "：" + name) if area else name

        # 复用草稿自带的第一个空任务，其余新建
        if ti == 1 and existing:
            tid = existing[0].get("task_id")
            step(base_pct, "[%d/%d] %s（复用默认任务）" % (ti, total_tasks, label))
        else:
            nt = _api("POST", "/api/v1/task-sets/%s/tasks/allocate-draft" % tsid, {}, token=token)
            tid = nt.get("task_id") or (nt.get("task") or {}).get("task_id")
            step(base_pct, "[%d/%d] %s（新建任务）" % (ti, total_tasks, label))
        if not tid:
            log("  ✗ 任务创建失败，跳过 %s" % label)
            continue

        photos = task.get("photos") or []
        videos = task.get("videos") or []
        log("  照片 %d 张，视频 %d 个" % (len(photos), len(videos)))

        local_photos, local_videos = [], []
        for f in photos:
            try:
                local_photos.append((f, relay_files(f) if relay_files else _download(f)))
            except Exception as e:
                log("    素材下载失败 %s：%s" % (f.get("filename"), e))
        for f in videos:
            try:
                local_videos.append((f, relay_files(f) if relay_files else _download(f)))
            except Exception as e:
                log("    素材下载失败 %s：%s" % (f.get("filename"), e))

        # 看图写这个任务的内容
        content, src2 = generate_task_content_from_media(
            site, task, [p for _, p in local_photos], [p for _, p in local_videos])
        log("    内容来源：%s，时长 %s 小时，SOP %d 步" % (
            {"vision": "看过素材", "llm": "大模型", "template": "模板"}.get(src2, src2),
            content["hours"], len(content["sop"])))
        if content.get("seen"):
            log("    画面：%s" % content["seen"][:60])

        # 上传素材
        photo_ids, video_ids = [], []
        done = 0
        allcount = len(local_photos) + len(local_videos)
        for f, path in local_photos:
            done += 1
            step(base_pct, "[%d/%d] %s 上传照片 %d/%d" % (ti, total_tasks, label, done, allcount))
            photo_ids.append(_upload(tid, path, "photo", token))
        for f, path in local_videos:
            done += 1
            step(base_pct, "[%d/%d] %s 上传视频 %d/%d" % (ti, total_tasks, label, done, allcount))
            if codec_of(path) == "hevc":
                log("    H.265 → H.264 转码中…")
                path = ensure_h264(path)
            video_ids.append(_upload(tid, path, "video", token))

        task_name = (content.get("name") or "").strip() or label
        if len(task_name) > 24:
            task_name = task_name[:24]
        _api("PATCH", "/api/v1/tasks/%s" % tid, {
            "task_name": task_name,
            "tet_node_path": site.get("scene") or "",
            "description": content["desc"],
            "required_duration": int(float(content["hours"]) * 3600),
            "collect_mode": "passive",
            "sop": {"steps": content["sop"]},
            "task_photos": photo_ids,
            "task_videos": video_ids,
        }, token=token)
        log("    已写入：%s（照片 %d，视频 %d，SOP %d 步）" % (task_name, len(photo_ids), len(video_ids), len(content["sop"])))
        made.append({"task_id": tid, "name": task_name, "label": label,
                     "photos": len(photo_ids), "videos": len(video_ids), "sop": len(content["sop"])})

    step(100, "完成，共 %d 个任务" % len(made))
    return {
        "task_set_id": tsid,
        "name": site_name,
        "address": full_addr,
        "tasks": made,
        "photos": sum(t["photos"] for t in made),
        "videos": sum(t["videos"] for t in made),
    }


'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('create_draft 改成多任务')
