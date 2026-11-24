import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 采集点列表加「地址」列，并重排列宽
old = '''        cols = ("sel", "name", "by", "time", "scene", "area", "tasks", "count", "size")
        self.tv_sites = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, t, w in zip(cols, ("选", "门店", "采集员", "时间", "场景分类", "面积", "任务", "文件", "大小"),
                           (36, 170, 70, 120, 140, 50, 40, 40, 70)):
            self.tv_sites.heading(c, text=t)
            self.tv_sites.column(c, width=w, anchor="w" if c in ("name", "scene") else "center")'''
new = '''        cols = ("sel", "name", "address", "by", "time", "scene", "area", "tasks", "count", "size")
        self.tv_sites = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, t, w in zip(cols, ("选", "门店", "现场地址", "采集员", "时间", "场景分类", "面积", "任务", "文件", "大小"),
                           (34, 145, 210, 60, 105, 110, 48, 40, 40, 65)):
            self.tv_sites.heading(c, text=t)
            self.tv_sites.column(c, width=w, anchor="w" if c in ("name", "address", "scene") else "center")'''
assert old in s
s = s.replace(old, new)

# 2) 填充时给地址赋值
old2 = '''            self.tv_sites.insert("", "end", iid=it["id"], values=(
                "☐",
                it.get("name", ""),'''
new2 = '''            self.tv_sites.insert("", "end", iid=it["id"], values=(
                "☐",
                it.get("name", ""),
                it.get("address") or "",'''
assert old2 in s
s = s.replace(old2, new2)

# 3) 文件列表列宽收一点，别把「上传时间」挤掉
old3 = '''        for c, t, w in zip(cols2, ("选", "区域", "任务", "类型", "文件名", "大小", "上传时间"), (36, 85, 95, 45, 195, 70, 125)):'''
new3 = '''        for c, t, w in zip(cols2, ("选", "区域", "任务", "类型", "文件名", "大小", "上传时间"), (34, 70, 90, 44, 165, 62, 105)):'''
assert old3 in s
s = s.replace(old3, new3)

# 4) 窗口宽一点
s = s.replace('root.geometry("1180x720")', 'root.geometry("1320x760")')

io.open(p, 'w', encoding='utf-8').write(s)
print('address column patched')
