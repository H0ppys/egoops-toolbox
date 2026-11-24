"""下载流程的几个体验修正：
1) 目录名取勾选采集点的名字，而不是固定的"采集点"
2) 开始下载前把状态写清楚，失败时把原因带到提示里
3) 目录选择框强制置前，避免"点了没反应""
"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

old = '''        target = self.ask_dir()
        if not target:
            return
        site_name = (self.current_site or {}).get("name", "采集点")'''
new = '''        target = self.ask_dir()
        if not target:
            return
        site_name = ""
        for iid in self.checked:
            if iid in self.site_rows:
                site_name = self.site_rows[iid].get("name", "")
                break
        if not site_name:
            site_name = (self.current_site or {}).get("name", "") or "采集点"'''
assert old in s
s = s.replace(old, new)

# 目录选择框置前
s = s.replace('''    def ask_dir(self):
        base = self.cfg.get("download_dir") or os.path.join(os.path.expanduser("~"), "Desktop", "采集数据")''',
'''    def ask_dir(self):
        try:
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass
        base = self.cfg.get("download_dir") or os.path.join(os.path.expanduser("~"), "Desktop", "采集数据")''')

# 失败原因收集，最后一起提示
s = s.replace('''        def work():
            ok, fail = 0, 0
            total = len(files)''', '''        def work():
            ok, fail = 0, 0
            errors = []
            total = len(files)''')

s = s.replace('''                except Exception as e:
                    fail += 1
                    self.ui(self.lbl_task.config, text="失败：%s（%s）" % (name, e))''',
'''                except Exception as e:
                    fail += 1
                    errors.append("%s：%s" % (name, e))
                    self.ui(self.lbl_task.config, text="失败：%s（%s）" % (name, e))''')

s = s.replace('''            self.ui(self.download_done, ok, fail, folder, open_after, files)''',
'''            self.ui(self.download_done, ok, fail, folder, open_after, files, errors)''')

s = s.replace('''    def download_done(self, ok, fail, folder, open_after, files):''',
'''    def download_done(self, ok, fail, folder, open_after, files, errors=None):''')

s = s.replace('''        if fail:
            messagebox.showwarning(APP_NAME, "有 %d 个文件下载失败，可重试" % fail)''',
'''        if fail:
            detail = "\\n".join((errors or [])[:5])
            messagebox.showwarning(APP_NAME, "有 %d 个文件下载失败：\\n\\n%s" % (fail, detail or "（无详细信息）"))''')

# 开始下载时立刻给反馈
s = s.replace('''        self.busy = True
        self.progress["value"] = 0''', '''        self.busy = True
        self.lbl_task.config(text="准备下载 %d 个文件…" % len(files))
        self.progress["value"] = 0''')

io.open(p, 'w', encoding='utf-8').write(s)
print('下载体验修正完成')
