import io

p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

# 去掉转码钩子（服务器只存不转），避免小机器被 CPU 打满
s = s.replace("import { transcodeIfNeeded } from './transcode.mjs';\n", "")

old = '''      // 视频若是 H.265(HEVC) 自动转成 H.264，浏览器/EgoOps 才播得了；异步做，不阻塞上传
      if (up.kind === 'video') {
        transcodeIfNeeded({ db, fileId, abs, filename: up.filename, contentName: up.filename }).then((r) => {
          if (r && r.done) log(`转码完成 ${fileId} ${up.filename} -> ${(r.size / 1048576).toFixed(1)}MB`);
        }).catch((e) => log(`转码失败 ${fileId}: ${e.message}`));
      }

'''
assert old in s
s = s.replace(old, "")
io.open(p, 'w', encoding='utf-8').write(s)
print('server hook removed')
