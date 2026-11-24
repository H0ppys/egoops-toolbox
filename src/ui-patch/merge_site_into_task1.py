"""EgoOps 任务映射改为：
   任务1 = 门头照/全景照片/全景视频 + 第一个区域的全套素材
   任务2..N = 各区域自己的素材（不再带门头/全景）

平台上限：单个任务照片 ≤8、视频 ≤3，合并后超了会截断并打日志。
"""

import io

P = 'viewer/egoops_draft.py'
s = io.open(P, encoding='utf-8').read()

# 1) 进入循环前：先把「采集点级」和「区域级」分开，并把采集点级并进第一个区域
old = '''    existing = _api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid,
                    token=token).get("records") or []
    made = []
    total_tasks = len(tasks)'''
new = '''    existing = _api("GET", "/api/v1/task-sets/%s/tasks?include_stats=false&include_assignments=false" % tsid,
                    token=token).get("records") or []

    # ---- 分组：采集点级（门头/全景）要并进第一个区域 ----
    def is_site_task(t):
        name = (t.get("name") or "")
        return ("门头" in name or "全景" in name) and not (t.get("area") or "").strip()

    site_tasks = [t for t in tasks if is_site_task(t)]
    area_tasks = [t for t in tasks if not is_site_task(t)]
    if not area_tasks:
        # 只有门头/全景：当成一个任务处理
        area_tasks = site_tasks
        site_tasks = []

    site_photos, site_videos = [], []
    for t in site_tasks:
        site_photos += t.get("photos") or []
        site_videos += t.get("videos") or []
    if site_photos or site_videos:
        log("  门头/全景素材：照片 %d 张、视频 %d 个，会并进任务1" % (len(site_photos), len(site_videos)))

    merged = []
    for i, t in enumerate(area_tasks):
        if i == 0:
            merged.append({
                "area": t.get("area") or "",
                "name": t.get("name") or "",
                "photos": (site_photos + (t.get("photos") or []))[:8],
                "videos": (site_videos + (t.get("videos") or []))[:3],
                "_merged": bool(site_photos or site_videos),
            })
        else:
            merged.append({
                "area": t.get("area") or "",
                "name": t.get("name") or "",
                "photos": (t.get("photos") or [])[:8],
                "videos": (t.get("videos") or [])[:3],
                "_merged": False,
            })
    tasks = merged

    made = []
    total_tasks = len(tasks)'''
assert old in s
s = s.replace(old, new)

# 2) 限流日志保持（现在在 merged 里已截断）
s = s.replace('''        # EgoOps 限制：单个任务照片最多 8 张、视频最多 3 个
        if len(photos) > 8:
            log("  照片 %d 张，超过平台上限 8 张，只传前 8 张" % len(photos))
            photos = photos[:8]
        if len(videos) > 3:
            log("  视频 %d 个，超过平台上限 3 个，只传前 3 个" % len(videos))
            videos = videos[:3]''',
'''        if task.get("_merged"):
            log("  任务1 = 门头/全景 + 第一区域，共 照片 %d、视频 %d" % (len(photos), len(videos)))''')

io.open(P, 'w', encoding='utf-8').write(s)
print('任务合并逻辑已加')
