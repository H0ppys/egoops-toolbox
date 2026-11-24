import io

p = 'viewer/agent_fill.py'
s = io.open(p, encoding='utf-8').read()

# 配置里加视觉模型
s = s.replace('''def load_llm_config():''', '''VISION_MODEL_DEFAULT = "doubao-seed-2-1-pro-260915"


def vision_model():
    cfg = load_llm_config()
    return (cfg.get("vision_model") or "").strip() or VISION_MODEL_DEFAULT


def load_llm_config():''')

# 基于素材生成
s = s.replace('''def generate_description(site):''', '''def _shrink(path, max_px=768, quality=78):
    """压成小图再送模型，省 token"""
    import base64
    import os as _os
    import tempfile
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB")
        img.thumbnail((max_px, max_px))
        out = _os.path.join(tempfile.gettempdir(), "egoops_llm_" + _os.path.basename(path) + ".jpg")
        img.save(out, quality=quality)
        with open(out, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        try:
            import base64 as b
            with open(path, "rb") as f:
                return b.b64encode(f.read()).decode()
        except Exception:
            return ""


def _video_frames(path, count=2):
    """从视频里抽几帧，返回临时图片路径"""
    import os as _os
    import subprocess
    import tempfile
    exe = _os.path.join(_os.environ.get("APPDATA") or "", "egoops-viewer", "ffmpeg.exe")
    if not _os.path.exists(exe):
        return []
    out_dir = _os.path.join(tempfile.gettempdir(), "egoops_frames")
    _os.makedirs(out_dir, exist_ok=True)
    base = _os.path.splitext(_os.path.basename(path))[0]
    frames = []
    for i in range(count):
        t = 0.5 + i * 1.0
        out = _os.path.join(out_dir, "%s_%d.jpg" % (base, i))
        try:
            subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t),
                            "-i", path, "-frames:v", "1", "-vf", "scale=768:-2", out],
                           check=False, timeout=60)
            if _os.path.exists(out) and _os.path.getsize(out) > 1024:
                frames.append(out)
        except Exception:
            pass
    return frames


def build_media_prompt(site, task):
    scene = (site.get("scene_label") or site.get("scene") or "").replace("/", "·")
    return (
        "下面是这家店拍的照片/视频截帧。请先看清楚画面里到底有什么（设备、物品、空间、人在做什么），"
        "再为这个采集任务写三样东西。\\n\\n"
        "要求：\\n"
        "1. desc：60~110 字，要写**画面里真实看到的东西**（具体物件、位置），不要套话；\\n"
        "2. hours：按实际耗时估算，0.5~3 的数字；\\n"
        "3. sop：5~7 条，按真实执行顺序，每条 8~18 字，动词开头，"
        "必须和画面里出现的东西对应（比如画面里是货架就写走到货架前，是机器就写操作机器）；\\n"
        "4. seen：一句话描述你从画面里看到了什么。\\n\\n"
        "只输出 JSON，不要代码块：\\n"
        '{"seen": "...", "desc": "...", "hours": 1, "sop": ["...", "..."]}\\n\\n'
        "门店：%s\\n场景分类：%s\\n任务名称：%s\\n所属区域：%s\\n"
        % (site.get("name") or "", scene or "未填", task.get("name") or "", task.get("area") or "未填")
    )


def _chat_vision(prompt, images, timeout=120):
    cfg = load_llm_config()
    key = (cfg.get("key") or "").strip()
    if not key or not images:
        return None
    base = (cfg.get("base") or "").rstrip("/")
    model = vision_model()
    content = [{"type": "text", "text": prompt}]
    for b64 in images:
        content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}})
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一名具身智能数据采集项目的执行导演，看清画面再下笔，只输出要求的 JSON。"},
            {"role": "user", "content": content},
        ],
        "temperature": 0.5,
    }
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode())
    return data["choices"][0]["message"]["content"].strip()


def generate_task_content_from_media(site, task, photo_paths, video_paths):
    """看素材写 SOP。素材读不到就退回纯文本。返回 (content, 来源)"""
    images = []
    for p in photo_paths[:4]:
        b = _shrink(p)
        if b:
            images.append(b)
    for v in video_paths[:2]:
        for fp in _video_frames(v, 2)[:2]:
            b = _shrink(fp)
            if b:
                images.append(b)
    if not images:
        return generate_task_content(site, task)

    try:
        raw = _chat_vision(build_media_prompt(site, task), images[:6])
        if raw:
            obj = _extract_json(raw)
            sop = [str(x).strip() for x in (obj.get("sop") or []) if str(x).strip()]
            if sop:
                return {
                    "desc": str(obj.get("desc") or "").strip(),
                    "hours": float(obj.get("hours") or 1),
                    "sop": sop,
                    "seen": str(obj.get("seen") or "").strip(),
                }, "vision"
    except Exception:
        pass
    return generate_task_content(site, task)


def generate_description(site):''')

io.open(p, 'w', encoding='utf-8').write(s)
print('agent_fill 支持看图')
