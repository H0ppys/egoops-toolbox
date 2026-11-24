import io

# ---------------- 1) viewer/tls.py：统一带证书校验的 opener ----------------
io.open('viewer/tls.py', 'w', encoding='utf-8').write('''"""服务器用的是自签证书，客户端固定校验这张证书（不信任其它任何 CA）。"""
import os
import ssl
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    os.path.join(getattr(sys, "_MEIPASS", HERE), "egoops.crt"),
    os.path.join(HERE, "egoops.crt"),
]

_CTX = None


def context():
    global _CTX
    if _CTX is not None:
        return _CTX
    for p in CANDIDATES:
        if os.path.exists(p):
            _CTX = ssl.create_default_context(cafile=p)
            return _CTX
    _CTX = ssl.create_default_context()
    return _CTX


def urlopen(req, timeout=30):
    return urllib.request.urlopen(req, timeout=timeout, context=context())
''')
print('tls.py 写好')

# ---------------- 2) api.py 用 tls.urlopen ----------------
p = 'viewer/api.py'
s = io.open(p, encoding='utf-8').read()
if 'import tls' not in s:
    s = s.replace('import urllib.request', 'import urllib.request\nimport tls', 1)
    s = s.replace('            with urllib.request.urlopen(req, timeout=timeout) as resp:',
                  '            with tls.urlopen(req, timeout=timeout) as resp:')
    s = s.replace('DEFAULT_SERVER = "http://<FILL_ME>/relay"', 'DEFAULT_SERVER = "https://<FILL_ME>/relay"')
    s = s.replace('"http://<FILL_ME>/relay"', '"https://<FILL_ME>/relay"')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('api.py: https + 证书校验')

# ---------------- 3) extras / egoops_draft 下载也用 tls ----------------
p2 = 'viewer/extras.py'
t = io.open(p2, encoding='utf-8').read()
if 'import tls' not in t:
    t = t.replace('import urllib.request', 'import urllib.request\nimport tls', 1)
    t = t.replace('    with urllib.request.urlopen(req, timeout=300) as r, open(path, "wb") as out:',
                  '    with tls.urlopen(req, timeout=300) as r, open(path, "wb") as out:')
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('extras.py: 用 tls')

p3 = 'viewer/egoops_draft.py'
u = io.open(p3, encoding='utf-8').read()
if 'import tls' not in u:
    u = u.replace('from transcode_pc import ensure_h264, codec_of',
                  'from transcode_pc import ensure_h264, codec_of\nimport tls')
    u = u.replace('    with urllib.request.urlopen(url, timeout=300) as r, open(tmp, "wb") as out:',
                  '    with tls.urlopen(url, timeout=300) as r, open(tmp, "wb") as out:')
    io.open(p3, 'w', encoding='utf-8').write(u)
    print('egoops_draft.py: 用 tls')
