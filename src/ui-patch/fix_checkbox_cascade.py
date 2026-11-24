import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    def on_tree_click(self, event):')
end = s.index('    def on_tree_double(self, event):')

new = '''    def on_tree_click(self, event):
        if self.tree.identify("region", event.x, event.y) != "cell":
            return None
        if self.tree.identify_column(event.x) != "#1":
            return None
        iid = self.tree.identify_row(event.y)
        if not iid:
            return None

        want = self.tree.set(iid, "sel") != "☑"     # 点一下要变成的状态
        self._set_checked(iid, want, cascade=True)   # 勾采集点 = 连带下面全部
        self._sync_ancestors(iid)
        self.update_check_label()
        return "break"

    def _set_checked(self, iid, checked, cascade=False):
        mark = "☑" if checked else "☐"
        try:
            self.tree.set(iid, "sel", mark)
        except Exception:
            return
        if checked:
            self.checked.add(iid)
        else:
            self.checked.discard(iid)
        if cascade:
            for child in self.tree.get_children(iid):
                self._set_checked(child, checked, cascade=True)

    def _sync_ancestors(self, iid):
        """下级全勾 → 上级自动勾；有一个没勾 → 上级取消"""
        parent = self.tree.parent(iid)
        while parent:
            kids = self.tree.get_children(parent)
            if kids:
                all_on = all(self.tree.set(k, "sel") == "☑" for k in kids)
                self._set_checked(parent, all_on, cascade=False)
            parent = self.tree.parent(parent)

    def _is_checked(self, iid):
        try:
            return self.tree.set(iid, "sel") == "☑"
        except Exception:
            return False

'''
s = s[:start] + new + s[end:]

# 全选/反选也要级联
s = s.replace('''    def toggle_all_checks(self):
        all_rows = []
        for iid in self.tree.get_children():
            all_rows.append(iid)
        all_checked = all(self.tree.set(i, "sel") == "☑" for i in all_rows) if all_rows else False
        for i in all_rows:
            self.tree.set(i, "sel", "☐" if all_checked else "☑")
        for i in all_rows:
            if all_checked:
                self.checked.discard(i)
            else:
                self.checked.add(i)
        self.update_check_label()''',
'''    def toggle_all_checks(self):
        rows = self.tree.get_children()
        if not rows:
            return
        all_checked = all(self._is_checked(i) for i in rows)
        for i in rows:
            self._set_checked(i, not all_checked, cascade=True)
        self.update_check_label()''')

io.open(p, 'w', encoding='utf-8').write(s)
print('勾选级联完成')
