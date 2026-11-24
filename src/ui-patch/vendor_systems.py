"""服务器：厂商 → 提交系统（美团 EgoOps / 其它系统）。"""

import io
import json
import os

# 1) 默认配置：美团有 EgoOps，其它厂商先标成 other（未接入）
path = 'relay/vendor_systems.json'
if not os.path.exists(path):
    data = {"KWQZB": "meituan"}
    io.open(path, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))
    print('已建', path)

# 2) 接口
p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

if '/api/vendor-systems' not in s:
    anchor = "    // 邀请码 → 厂家名（公开，查看器用来显示厂商）"
    block = '''    // 邀请码 → 提交系统（meituan = 美团 EgoOps；other = 别的系统，还没接）
    if (req.method === 'GET' && p === '/api/vendor-systems') {
      try {
        const cfgSys = JSON.parse(fs.readFileSync(path.join(HERE, 'vendor_systems.json'), 'utf8'));
        return send(res, 200, { items: cfgSys });
      } catch (_) {
        return send(res, 200, { items: { KWQZB: 'meituan' } });
      }
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('server: /api/vendor-systems 已加')
