"""服务器：/api/app/version 版本信息 + /apk/latest.apk 下载（支持断点）。"""

import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

if '/api/app/version' not in s:
    anchor = "    // 采集场景分类（EgoOps「申请采集点」同款）——公开接口，未登录也能拉"
    block = '''    // App 版本信息（公开）：有新版就提示下载
    if (req.method === 'GET' && p === '/api/app/version') {
      try {
        const info = JSON.parse(fs.readFileSync(path.join(HERE, 'app_version.json'), 'utf8'));
        return send(res, 200, info);
      } catch (_) {
        return send(res, 200, { versionCode: 0, versionName: '', url: '' });
      }
    }

    // 下载最新 APK（支持 Range，断点续传）
    if (req.method === 'GET' && p === '/apk/latest.apk') {
      const file = path.join(HERE, 'apk', 'egoops-collect-latest.apk');
      if (!fs.existsSync(file)) throw notFound('还没有发布过 APK');
      const stat = fs.statSync(file);
      const range = req.headers.range;
      res.writeHead(200, {
        'Content-Type': 'application/vnd.android.package-archive',
        'Content-Length': stat.size,
        'Accept-Ranges': 'bytes',
        'Content-Disposition': 'attachment; filename="egoops-collect.apk"',
        ...CORS,
      });
      if (range) {
        const m = /bytes=(\\d+)-(\\d*)/.exec(range);
        if (m) {
          const start = Number(m[1]);
          const end = m[2] ? Number(m[2]) : stat.size - 1;
          res.writeHead(206, {
            'Content-Type': 'application/vnd.android.package-archive',
            'Content-Range': `bytes ${start}-${end}/${stat.size}`,
            'Content-Length': end - start + 1,
            'Accept-Ranges': 'bytes',
            ...CORS,
          });
          fs.createReadStream(file, { start, end }).pipe(res);
          return;
        }
      }
      fs.createReadStream(file).pipe(res);
      return;
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('server: 版本 + APK 下载接口已加')
else:
    print('server: 已有版本接口')
