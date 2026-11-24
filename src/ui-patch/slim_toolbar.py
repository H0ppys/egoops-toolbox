import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 顶部「设置」按钮去掉（菜单里已有），减少重复
s = s.replace('''        self.btn_settings = ttk.Button(top, text="设置", command=self.open_settings)
        self.btn_settings.pack(side="left")
''', '')

io.open(p, 'w', encoding='utf-8').write(s)
print('去掉顶部设置按钮')
