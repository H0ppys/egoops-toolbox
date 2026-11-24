import io

p = 'viewer/app2.py'
s = io.open(p, encoding='utf-8').read()

old = '        self.lbl_count.config(text="%d 个" % shown)'
new = '''        self.lbl_count.config(text="%d 个" % shown)

        # 自动选中第一个采集点，省一次点击
        kids = self.tv_sites.get_children()
        if kids and not self.tv_sites.selection():
            self.tv_sites.selection_set(kids[0])
            self.tv_sites.focus(kids[0])
            self.on_site_select()'''
if '自动选中第一个采集点' not in s:
    assert old in s
    s = s.replace(old, new, 1)

if 'def open_egoops' not in s:
    s = s.replace('    def check_login(self):', '''    def open_egoops(self):
        import webbrowser
        webbrowser.open("https://egoops.meituan.com/assignment")

    def check_login(self):''', 1)
    s = s.replace('        m3.add_command(label="检查登录态", command=self.check_login)',
                  '        m3.add_command(label="打开 EgoOps 网页", command=self.open_egoops)\n'
                  '        m3.add_command(label="检查登录态", command=self.check_login)')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('自动选中 + 打开EgoOps 已加')
