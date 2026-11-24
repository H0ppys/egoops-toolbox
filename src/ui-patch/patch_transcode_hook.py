import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

# 1) 顶部加转码工具引入
if 'const { transcodeIfNeeded }' not in s:
    s = s.replace("import { createRequire } from 'node:module';",
                  "import { createRequire } from 'node:module';\nimport { transcodeIfNeeded } from './transcode.mjs';")

# 2) complete 后异步触发转码
old = '''      return send(res, 200, {
        file: { id: fileId, kind: up.kind, filename: up.filename, size: realSize, url: `/files/${fileId}` },
      });'''
new = '''      // 视频若是 H.265(HEVC) 自动转成 H.264，浏览器/EgoOps 才播得了；异步做，不阻塞上传
      if (up.kind === 'video') {
        transcodeIfNeeded({ db, fileId, abs, filename: up.filename, contentName: up.filename }).then((r) => {
          if (r && r.done) log(`转码完成 ${fileId} ${up.filename} -> ${(r.size / 1048576).toFixed(1)}MB`);
        }).catch((e) => log(`转码失败 ${fileId}: ${e.message}`));
      }

      return send(res, 200, {
        file: { id: fileId, kind: up.kind, filename: up.filename, size: realSize, url: `/files/${fileId}` },
      });'''
assert old in s
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
print('server patched')
