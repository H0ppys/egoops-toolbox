import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 导入 extras ----------
s = s.replace('from address_parse import parse as parse_address',
              'from address_parse import parse as parse_address\nimport extras')

# ---------- 2) 表格加 EgoOps 状态列 ----------
s = s.replace('''        cols = ("sel", "name", "vendor", "detail", "who", "time", "size")''',
              '''        cols = ("sel", "name", "vendor", "detail", "who", "time", "size", "draft")''')
s = s.replace('''        widths = {"sel": 30, "name": 150, "vendor": 110, "detail": 190, "who": 88, "time": 100, "size": 60}
        titles = {"sel": "选", "name": "名称 / 文件", "vendor": "厂商", "detail": "地址 / 区域·任务 / 类型",
                  "who": "采集员 / 数量", "time": "时间", "size": "大小"}''',
'''        widths = {"sel": 28, "name": 140, "vendor": 100, "detail": 165, "who": 78, "time": 92, "size": 54, "draft": 92}
        titles = {"sel": "选", "name": "名称 / 文件", "vendor": "厂商", "detail": "地址 / 区域·任务 / 类型",
                  "who": "采集员 / 数量", "time": "时间", "size": "大小", "draft": "EgoOps"}''')

# ---------- 3) 站点行填草稿状态 ----------
s = s.replace('''                human_size(it.get("bytes", 0)),
            ))''', '''                human_size(it.get("bytes", 0)),
                self.draft_text(it),
            ))''')

# 任务/文件行补一列
s = s.replace('''                "☐", label, "", "区域任务", "照片 %d · 视频 %d" % (len(photos), len(videos)), "", ""))''',
'''                "☐", label, "", "区域任务", "照片 %d · 视频 %d" % (len(photos), len(videos)), "", "", ""))''')
s = s.replace('''                    "照片" if f.get("kind") == "photo" else "视频",
                    (f.get("created_at") or "").replace("T", " ")[:16],
                    human_size(f.get("size", 0)),
                ))''', '''                    "照片" if f.get("kind") == "photo" else "视频",
                    (f.get("created_at") or "").replace("T", " ")[:16],
                    human_size(f.get("size", 0)),
                    "",
                ))''')

# ---------- 4) 辅助方法 ----------
s = s.replace('''    def invites_map(self):''', '''    def draft_text(self, site):
        d = extras.draft_of(site.get("id"))
        if not d:
            return "未建"
        return "草稿 " + str(d.get("task_set_id"))[-6:]

    def invites_map(self):''')

# ---------- 5) 单条建草稿：已建过要确认 ----------
s = s.replace('''    def _start_draft(self, site, fields):
        self.btn_fill.config(state="disabled")''', '''    def _start_draft(self, site, fields):
        exist = extras.draft_of(site.get("id"))
        if exist and not messagebox.askyesno(
                APP_NAME,
                "这个采集点已经建过草稿 %s。\\n再建一份会在 EgoOps 里多出一条。\\n\\n仍然新建吗？" % exist.get("task_set_id")):
            return
        self.btn_fill.config(state="disabled")''')

# 建完后记住
s = s.replace('''                res = mod.create_draft(payload, log=log, progress=progress)
                self.ui(self._draft_done, res)''', '''                res = mod.create_draft(payload, log=log, progress=progress)
                extras.remember(site["id"], res["task_set_id"], res.get("name", ""))
                self.ui(self._draft_done, res)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('draft tracking wired')
