"""服务器：每个厂商可以有自己的分类表 /opt/egoops/relay/vendor_scenes/<CODE>.json。"""

import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

old = """    if (req.method === 'GET' && p === '/api/scenes') {
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

new = """    if (req.method === 'GET' && p === '/api/scenes') {
      const code = (u.searchParams.get('vendor') || '').trim().toUpperCase();

      // 1) 这个厂商有自己的一套分类表 → 整份返回
      if (code) {
        const own = path.join(HERE, 'vendor_scenes', code + '.json');
        if (fs.existsSync(own)) {
          try {
            const data = JSON.parse(fs.readFileSync(own, 'utf8'));
            const domains = [];
            for (const it of data.items || []) if (!domains.includes(it.category)) domains.push(it.category);
            return send(res, 200, { ...data, vendor: code, domains, own: true });
          } catch (e) {
            log('厂商分类表读取失败 ' + code + ': ' + e.message);
          }
        }
      }

      // 2) 否则用全局默认表，再按 vendor_scenes.json 里的允许大类过滤
      const allow = (vendorScenes()[code] || []).map((x) => String(x));
      if (!code || allow.length === 0) {
        return send(res, 200, { ...SCENES, vendor: code, domains: null, own: false });
      }
      const items = SCENES.items.filter((it) => allow.includes(it.category));
      const domains = [];
      for (const it of items) if (!domains.includes(it.category)) domains.push(it.category);
      return send(res, 200, { ...SCENES, count: items.length, items, vendor: code, domains, own: false });
    }"""

assert old in s, '找不到 scenes 路由'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('server: 支持每厂商独立分类表')
