"""修底部状态栏看不见：footer 必须在可伸展的 body 之前 pack(side=bottom)。"""

import io

p = 'viewer/app2.py'
s = io.open(p, encoding='utf-8').read()

# 找到 foot 段与 body 段
i_body = s.index('        # 主体：左右分栏')
i_foot = s.index('        # 底部操作条')
i_menu = s.index('        # 菜单')

body_block = s[i_body:i_foot]
foot_block = s[i_foot:i_menu]

# 重排：foot 先，body 后
s = s[:i_body] + foot_block + body_block + s[i_menu:]

# foot 改为 side="bottom" 先占位
s = s.replace('''        foot = ttk.Frame(self.root, padding=(18, 6, 18, 12))
        foot.pack(fill="x")''',
'''        foot = ttk.Frame(self.root, padding=(18, 6, 18, 12))
        foot.pack(side="bottom", fill="x")''')

io.open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('footer 位置已调整，语法 OK')
