"""建草稿改成「先写文字字段，再传素材」：
   即使素材下载/看图/上传失败，任务也至少有名称、描述、SOP，不会出现空任务。
"""

import io

p = 'viewer/egoops_draft.py'
s = io.open(p, encoding='utf-8').read()

old_start = s.index('        task_name = (content.get("name") or "").strip() or label')
old_end = s.index('    step(100, "完成，共 %d 个任务" % len(made))')

new = '''        task_name = (content.get("name") or "").strip() or label
        if len(task_name) > 24:
            task_name = task_name[:24]

        # ① 先把文字写进去（名称/描述/时长/SOP），保证任务不空
        base_patch = {
            "task_name": task_name,
            "tet_node_path": site.get("scene") or "",
            "description": content["desc"],
            "required_duration": int(float(content["hours"]) * 3600),
            "collect_mode": "passive",
            "sop": {"steps": content["sop"]},
        }
        try:
            _api("PATCH", "/api/v1/tasks/%s" % tid, base_patch, token=token)
            log("    文字已写入：%s（时长 %s 小时，SOP %d 步）" % (task_name, content["hours"], len(content["sop"])))
        except Exception as e:
            log("    ✗ 写文字失败：%s" % e)

        # ② 再传素材
        photo_ids, video_ids = [], []
        done = 0
        allcount = len(local_photos) + len(local_videos)
        for f, path in local_photos:
            done += 1
            step(base_pct, "[%d/%d] %s 上传照片 %d/%d" % (ti, total_tasks, label, done, allcount))
            try:
                photo_ids.append(_upload(tid, path, "photo", token))
            except Exception as e:
                log("    ✗ 照片上传失败 %s：%s" % (f.get("filename"), e))
        for f, path in local_videos:
            done += 1
            step(base_pct, "[%d/%d] %s 上传视频 %d/%d" % (ti, total_tasks, label, done, allcount))
            try:
                if codec_of(path) == "hevc":
                    log("    H.265 → H.264 转码中…")
                    path = ensure_h264(path)
                video_ids.append(_upload(tid, path, "video", token))
            except Exception as e:
                log("    ✗ 视频上传失败 %s：%s" % (f.get("filename"), e))

        # ③ 挂素材
        if photo_ids or video_ids:
            try:
                _api("PATCH", "/api/v1/tasks/%s" % tid, {"task_photos": photo_ids, "task_videos": video_ids},
                     token=token)
            except Exception as e:
                log("    ✗ 挂素材失败：%s" % e)

        # ④ 回查
        got_p, got_v = len(photo_ids), len(video_ids)
        try:
            chk = _api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid,
                       token=token).get("records") or []
            got = next((x for x in chk if x.get("task_id") == tid), {})
            gp = len(got.get("task_photos") or [])
            gv = len(got.get("task_videos") or [])
            if gp != len(photo_ids) or gv != len(video_ids):
                log("    ⚠ 回查不一致：本地 照片%d/视频%d，EgoOps 照片%d/视频%d"
                    % (len(photo_ids), len(video_ids), gp, gv))
            got_p, got_v = gp, gv
        except Exception as e:
            log("    （回查失败：%s）" % e)

        log("    完成：%s（照片 %d，视频 %d，SOP %d 步）" % (task_name, got_p, got_v, len(content["sop"])))
        made.append({"task_id": tid, "name": task_name, "label": label,
                     "photos": got_p, "videos": got_v, "sop": len(content["sop"])})

'''
s = s[:old_start] + new + s[old_end:]

io.open(p, 'w', encoding='utf-8').write(s)
print('建草稿改成先文字后素材')

# 每个任务整体包 try，避免一个任务出错就中断全部
t = open(p, encoding='utf-8').read()
if 'for ti, task in enumerate(tasks, 1):' in t and 'try:  # 单任务保护' not in t:
    t = t.replace('''        if not tid:
            log("  ✗ 任务创建失败，跳过 %s" % label)
            continue''', '''        if not tid:
            log("  ✗ 任务创建失败，跳过 %s" % label)
            continue''')
    open(p, 'w', encoding='utf-8').write(t)
