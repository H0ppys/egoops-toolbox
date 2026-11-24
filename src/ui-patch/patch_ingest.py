import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

# 1) API 增加「最近入库」扫描
s = s.replace('''    def by_actor_in_task(self, task_id):''',
'''    def ingest_map(self, log=None):
        """全量扫描，统计每个 (task_id, 执行者) 的最新入库时间 created_at。"""
        import concurrent.futures
        first = self.get("/api/v1/recordings", {"page": 1, "size": 20})
        total = int(first.get("total") or 0)
        pages = (total + 19) // 20
        items = list(first.get("items") or [])

        def fetch(p):
            for _ in range(3):
                try:
                    return self.get("/api/v1/recordings", {"page": p, "size": 20}).get("items") or []
                except Exception:
                    time.sleep(0.5)
            return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for chunk in pool.map(fetch, range(2, pages + 1)):
                if chunk:
                    items.extend(chunk)
        m = {}
        for it in items:
            k = (str(it.get("task_id") or ""), it.get("actor_name") or "")
            ca = it.get("created_at") or ""
            if ca > m.get(k, ""):
                m[k] = ca
        if log:
            log(f"扫描 {len(items)} 条用于入库时间（{pages} 页）")
        return m

    def by_actor_in_task(self, task_id):''')

# 2) build_rows 增加 ingest 参数并写入「最近入库」、合格率取整
s = s.replace("def build_rows(stats, tasks, names, fetch_actors, updated_at, log):",
              "def build_rows(stats, tasks, names, fetch_actors, ingest, updated_at, log):")
s = s.replace('''                "最近录制": (a.get("latest_record_time") or "")[:10],
                "更新时间": updated_at,''',
'''                "最近录制": (a.get("latest_record_time") or "")[:10],
                "最近入库": (ingest.get((tid, a.get("group_name") or "")) or "")[:10],
                "更新时间": updated_at,''')
s = s.replace('"合格率（%）": round(pss / d * 100, 1) if d else 0,',
              '"合格率（%）": round(pss / d * 100) if d else 0,')
s = s.replace('"合格率（%）": round(total_pass / total_dur * 100, 1) if total_dur else 0,',
              '"合格率（%）": round(total_pass / total_dur * 100) if total_dur else 0,')

# 3) sync 中先扫描入库时间
s = s.replace('''    step(55, "按任务拉取执行者数据…")''',
'''    step(50, "扫描入库时间（全量）…")
    try:
        ingest = api.ingest_map(log)
    except Exception as e:
        ingest = {}
        log(f"入库时间扫描失败：{e}")

    step(62, "按任务拉取执行者数据…")''')
s = s.replace('''    rows = build_rows(stats, tasks, names,
                      lambda tid: (api.by_actor_in_task(tid).get("items") or []),
                      updated, log)''',
'''    rows = build_rows(stats, tasks, names,
                      lambda tid: (api.by_actor_in_task(tid).get("items") or []),
                      ingest, updated, log)''')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
