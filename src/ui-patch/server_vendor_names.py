"""服务器：/api/vendor-names 返回邀请码 → 厂家名（查看器显示用，公开）。"""

import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

if '/api/vendor-names' not in s:
    anchor = "    // App 版本信息（公开）：有新版就提示下载"
    block = '''    // 邀请码 → 厂家名（公开，查看器用来显示厂商）
    if (req.method === 'GET' && p === '/api/vendor-names') {
      try {
        const names = JSON.parse(fs.readFileSync(path.join(HERE, 'vendor_names.json'), 'utf8'));
        return send(res, 200, { items: names });
      } catch (_) {
        return send(res, 200, { items: {} });
      }
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('server: /api/vendor-names 已加')
else:
    print('server: 已有 vendor-names')
