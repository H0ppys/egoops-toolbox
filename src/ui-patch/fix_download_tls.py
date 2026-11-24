"""下载走 tls.urlopen（服务器是自签证书，必须带固定证书的 context）。"""

import io

p = 'viewer/api.py'
s = io.open(p, encoding='utf-8').read()

old = '''        with urllib.request.urlopen(req, timeout=600) as resp:'''
new = '''        with tls.urlopen(req, timeout=600) as resp:'''
if old in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('api.download: 改用 tls.urlopen')
else:
    print('没找到目标行，检查是否已改过')

# 顺带确认 tls 已导入
if 'import tls' not in s:
    s = s.replace('import urllib.request', 'import urllib.request\nimport tls', 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('补上 import tls')
