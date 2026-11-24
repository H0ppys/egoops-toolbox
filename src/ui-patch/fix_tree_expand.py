import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''    def on_tree_open(self, event):
        iid = self.tree.focus()
        if iid not in self.site_rows or iid in self.loaded_sites:
            return
        self.loaded_sites.add(iid)
        site = self.site_rows.get(iid)
        if not site:
            return'''
new = '''    def on_tree_open(self, event):
        iid = self.tree.focus()
        # 点三角展开时焦点不一定落在这一行，兜底找「已展开但没加载过」的采集点
        if iid not in self.site_rows:
            for sid in self.tree.get_children():
                if sid in self.site_rows and self.tree.item(sid, "open") and sid not in self.loaded_sites:
                    iid = sid
                    break
        if iid not in self.site_rows or iid in self.loaded_sites:
            return
        self.loaded_sites.add(iid)
        site = self.site_rows.get(iid)
        if not site:
            return'''
assert old in s
s = s.replace(old, new)

# 加载失败时把「加载中…」换成可点击重试，而不是永远转圈
s = s.replace('''            except Exception as e:
                self.ui(self.set_status, "读取文件失败：%s" % e, "#b3261e")''',
'''            except Exception as e:
                self.ui(self._load_failed, iid, str(e))''')

s = s.replace('''    def fill_detail(self, iid, detail):''', '''    def _load_failed(self, iid, err):
        self.loaded_sites.discard(iid)
        try:
            for ch in self.tree.get_children(iid):
                self.tree.delete(ch)
            self.tree.insert(iid, "end", text="", values=("", "加载失败，点三角收起再展开重试：%s" % err, "", "", "", "", ""))
        except Exception:
            pass
        self.set_status("读取文件失败：%s" % err, "#b3261e")

    def fill_detail(self, iid, detail):''')

io.open(p, 'w', encoding='utf-8').write(s)
print('展开加载修好')
