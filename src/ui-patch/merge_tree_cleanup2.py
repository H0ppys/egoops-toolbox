import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) 删掉旧的「勾选框」整段（含重复的 on_site_click / delete_* / download_checked_sites / on_file_click 等）
start_marker = '    # ---------- 勾选框 ----------'
end_marker = '    def download_files(self, files, open_after=False):'
i = s.index(start_marker)
j = s.index(end_marker)
new_block = '''    def download_checked(self):
        files = self.checked_files()
        if not files:
            messagebox.showinfo(APP_NAME, "先勾选文件或采集点（点最左边的方框）")
            return
        self.download_files(files)

'''
s = s[:i] + new_block + s[j:]

# 2) selftest 用 tree
s = s.replace('app.tv_sites["columns"]', 'app.tree["columns"]')

io.open(p, 'w', encoding='utf-8').write(s)
print('cleaned')
