"""服务器：/api/scenes?vendor=CODE 按厂商返回可见大类。"""

import io
import json

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

# 1) 读厂商配置
if 'vendorScenes' not in s:
    s = s.replace("const SCENES = JSON.parse(fs.readFileSync(path.join(HERE, 'scenes.json'), 'utf8'));",
"""const SCENES = JSON.parse(fs.readFileSync(path.join(HERE, 'scenes.json'), 'utf8'));

// 厂商 → 可见大类（没有配置就是全部）
const VENDOR_FILE = path.join(HERE, 'vendor_scenes.json');
function vendorScenes() {
  try { return JSON.parse(fs.readFileSync(VENDOR_FILE, 'utf8')); } catch (_) { return {}; }
}""")

# 2) 接口支持 vendor 过滤
old = """    if (req.method === 'GET' && p === '/api/scenes') {
      return send(res, 200, SCENES);
    }"""
new = """    if (req.method === 'GET' && p === '/api/scenes') {
      const code = (u.searchParams.get('vendor') || '').trim().toUpperCase();
      const allow = (vendorScenes()[code] || []).map((x) => String(x));
      if (!code || allow.length === 0) {
        return send(res, 200, { ...SCENES, vendor: code, domains: null });
      }
      const items = SCENES.items.filter((it) => allow.includes(it.category));
      const domains = [];
      for (const it of items) if (!domains.includes(it.category)) domains.push(it.category);
      return send(res, 200, { ...SCENES, count: items.length, items, vendor: code, domains });
    }"""
assert old in s
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
print('server: /api/scenes?vendor= 已支持')

# 3) 空配置文件，方便查看器/命令行维护
try:
    io.open('relay/vendor_scenes.json', encoding='utf-8').read()
except Exception:
    io.open('relay/vendor_scenes.json', 'w', encoding='utf-8').write('{}')
    print('已创建 relay/vendor_scenes.json')
