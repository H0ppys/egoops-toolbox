import io

# ---------------- App：输入框不限大小写，提示写清楚 ----------------
p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

s = s.replace('        etInvite.setHint("ZJMEIYI");',
              '        etInvite.setHint("例如 ZJMEIYI（大小写都可以）");')

s = s.replace('''        lInv.setText("邀请码（必填，管理员事先约定，例如 ZJMEIYI）");''',
              '''        lInv.setText("邀请码（必填，管理员事先约定，大小写都可以）");''')

# 输入时允许字母数字和 - _（不限制大小写）
if 'InputFilter' not in s:
    s = s.replace('''        etInvite.setSingleLine(true);''',
'''        etInvite.setSingleLine(true);
        etInvite.setInputType(android.text.InputType.TYPE_CLASS_TEXT
                | android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        etInvite.setFilters(new android.text.InputFilter[]{ new android.text.InputFilter.LengthFilter(32) });''')

io.open(p, 'w', encoding='utf-8').write(s)
print('App：邀请码大小写都接受')

# ---------------- 查看器：本地映射大小写不敏感 ----------------
p2 = 'viewer/app.py'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('''    def vendor_of(self, site):
        code = (site.get("invite") or "").strip().upper()
        if not code:
            return "—"
        return self.invites_map().get(code) or (code + "（未配置）")''',
'''    def vendor_of(self, site):
        code = (site.get("invite") or "").strip()
        if not code:
            return "—"
        # 大小写不敏感匹配：采集员填 zjmeiyi、你配 ZJMEIYI，都能对上
        for k, v in self.invites_map().items():
            if k.strip().upper() == code.upper():
                return v
        return code.upper() + "（未配置）"''')

# 添加时不强制大写存储（显示时再说）
t = t.replace('''        def add_code():
            code = e_code.get().strip().upper()''',
'''        def add_code():
            code = e_code.get().strip().upper()   # 统一按大写存，避免一个码两条记录''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('查看器：大小写不敏感匹配')
