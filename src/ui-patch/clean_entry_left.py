"""清掉重做后残留的旧控件引用。"""

import io

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 1) do_connect 里 focus 到姓名
s = s.replace('''            self.ent_name.focus_set()''', '''            pass''')

# 2) apply_invite_visibility 里藏/显示邀请码输入框——现在没这个控件了，整段简化
s = s.replace('''        self.ent_invite.pack(side="left", padx=(6, 14), before=self.btn_connect)''',
              '''        pass''')
s = s.replace('''        self.ent_invite.pack_forget()''', '''        pass''')

# 3) 自检输出
s = s.replace('''app.ent_server.get()''', '''app.var_server.get()''')

io.open(p, 'w', encoding='utf-8').write(s)
print('残留引用已清理')

import re
left = [l.strip() for l in s.splitlines() if re.search(r'ent_(server|name|invite)\.', l)]
print('剩余:', left[:5])
