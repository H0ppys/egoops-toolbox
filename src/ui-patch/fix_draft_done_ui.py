"""查看器的建草稿成功弹窗改成多任务版（原来读 res["hours"]/res["sop"]）。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old_start = s.index('    def _draft_done(self, res):')
old_end = s.index('    def _draft_failed(self, err):')
new = '''    def _draft_done(self, res):
        self.progress["value"] = 100
        self.lbl_task.config(text="草稿已建：%s（%d 个任务）" % (res["task_set_id"], len(res.get("tasks") or [])))
        tasks = res.get("tasks") or []
        lines = [
            "草稿已建好（未提交审核）",
            "",
            "采集点：%s" % res["name"],
            "草稿 ID：%s" % res["task_set_id"],
            "现场地址：%s" % (res["address"] or "（空，需在页面上选省市区）"),
            "",
            "任务 %d 个：" % len(tasks),
        ]
        for t in tasks[:8]:
            lines.append("  · %s —— 照片 %d，视频 %d，SOP %d 步" % (t["name"], t["photos"], t["videos"], t["sop"]))
        if len(tasks) > 8:
            lines.append("  …")
        lines.append("")
        lines.append("去 EgoOps「申报 → 草稿」核对，没问题再点提交审核。")

        if messagebox.askyesno(APP_NAME, "\\n".join(lines) + "\\n\\n现在打开 EgoOps 看吗？"):
            import webbrowser
            webbrowser.open("https://egoops.meituan.com/assignment")

'''
s = s[:old_start] + new + s[old_end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('成功弹窗改成多任务')
