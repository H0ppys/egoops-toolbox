"""修下载校验：按服务器给的大小比对，而不是写死 100KB（APK 才 95KB，被误判成不完整）。"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 传大小进来
s = s.replace('.setPositiveButton("立即更新", (d, w) -> downloadAndInstall(url))',
              '.setPositiveButton("立即更新", (d, w) -> downloadAndInstall(url, size))')

s = s.replace('private void downloadAndInstall(final String url) {',
              'private void downloadAndInstall(final String url, final long expectSize) {')

# 2) 校验改成：有声明大小就比对大小，并检查 ZIP 头
old = '''                if (out.length() < 100000) throw new Exception("下载的文件不完整");
                installApk(out);'''
new = '''                long got = out.length();
                if (expectSize > 0 && got != expectSize) {
                    throw new Exception("大小不一致（收到 " + got + "，应为 " + expectSize + "）");
                }
                if (got < 20000) throw new Exception("文件太小（" + got + " 字节），可能没下全");
                byte[] head = new byte[4];
                java.io.FileInputStream fis = new java.io.FileInputStream(out);
                int hn = fis.read(head);
                fis.close();
                if (hn < 2 || head[0] != 'P' || head[1] != 'K') {
                    throw new Exception("下载到的不是 APK（可能被网关拦截）");
                }
                installApk(out);'''
assert old in s
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(s)
print('下载校验已修正')
