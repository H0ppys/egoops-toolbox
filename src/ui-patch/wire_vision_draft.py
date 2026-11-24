import io

p = 'viewer/egoops_draft.py'
s = io.open(p, encoding='utf-8').read()

# 1) 导入视觉生成
s = s.replace('from agent_fill import generate_description, generate_task_content  # noqa: E402',
              'from agent_fill import (generate_description, generate_task_content,  # noqa: E402\n                        generate_task_content_from_media)')

# 2) 把「生成内容」挪到素材下载之后，并优先用素材
old = '''    step(38, "生成任务描述与 SOP…")
    content, src2 = generate_task_content(site, task)
    log("  内容来源：%s，时长 %s 小时，SOP %d 步" % (
        "大模型" if src2 == "llm" else "模板", content["hours"], len(content["sop"])))

    photos = task.get("photos") or []
    videos = task.get("videos") or []
    total = len(photos) + len(videos)'''
new = '''    photos = task.get("photos") or []
    videos = task.get("videos") or []

    # 先把素材落到本地：既要上传，也要给模型看
    step(36, "下载素材（给模型看，也用于上传）…")
    local_photos, local_videos = [], []
    for f in photos[:9]:
        try:
            local_photos.append((f, relay_files(f) if relay_files else _download(f)))
        except Exception as e:
            log("  素材下载失败 %s：%s" % (f.get("filename"), e))
    for f in videos[:3]:
        try:
            local_videos.append((f, relay_files(f) if relay_files else _download(f)))
        except Exception as e:
            log("  素材下载失败 %s：%s" % (f.get("filename"), e))

    step(40, "看图写任务描述与 SOP…")
    content, src2 = generate_task_content_from_media(
        site, task, [p for _, p in local_photos], [p for _, p in local_videos])
    log("  内容来源：%s，时长 %s 小时，SOP %d 步" % (
        {"vision": "看过素材", "llm": "大模型(纯文本)", "template": "模板"}.get(src2, src2),
        content["hours"], len(content["sop"])))
    if content.get("seen"):
        log("  画面内容：%s" % content["seen"])

    total = len(local_photos) + len(local_videos)'''
assert old in s
s = s.replace(old, new)

# 3) 上传循环改用已下载的本地文件
old2 = '''    photo_ids, video_ids = [], []
    for f in photos[:9]:
        done += 1
        step(38 + int(52 * done / max(total, 1)), "上传照片 %s（%d/%d）" % (f.get("filename"), done, total))
        path = relay_files(f) if relay_files else _download(f)
        photo_ids.append(_upload(tid, path, "photo", token))
    for f in videos[:3]:
        done += 1
        step(38 + int(52 * done / max(total, 1)), "上传视频 %s（%d/%d）" % (f.get("filename"), done, total))
        path = relay_files(f) if relay_files else _download(f)
        if codec_of(path) == "hevc":'''
new2 = '''    photo_ids, video_ids = [], []
    for f, path in local_photos:
        done += 1
        step(46 + int(46 * done / max(total, 1)), "上传照片 %s（%d/%d）" % (f.get("filename"), done, total))
        photo_ids.append(_upload(tid, path, "photo", token))
    for f, path in local_videos:
        done += 1
        step(46 + int(46 * done / max(total, 1)), "上传视频 %s（%d/%d）" % (f.get("filename"), done, total))
        if codec_of(path) == "hevc":'''
assert old2 in s
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(s)
print('create_draft 接入看图')
