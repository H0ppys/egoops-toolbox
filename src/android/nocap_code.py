"""让「不拍摄收集」版在代码里生效：
   · 隐藏拍照/录像按钮，只保留「从相册选」
   · 不烧水印（素材自带水印）
   · 不检查更新
"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 拍照按钮：不拍摄版隐藏
old = '''        b.setOnClickListener(v -> captureShot(key, kind));'''
new = '''        if (BuildConfigVersion.NO_CAPTURE) {
            b.setVisibility(View.GONE);
        } else {
            b.setOnClickListener(v -> captureShot(key, kind));
        }'''
assert old in s
s = s.replace(old, new)

# 2) 从相册选按钮更醒目 + 文案
s = s.replace('''        Button pick = secondaryButton(kind.equals("video") ? "从相册选视频" : "从相册选照片", 54);''',
'''        String pickText = BuildConfigVersion.NO_CAPTURE
                ? (kind.equals("video") ? "从相册选水印视频" : "从相册选水印照片")
                : (kind.equals("video") ? "从相册选视频" : "从相册选照片");
        Button pick = secondaryButton(pickText, BuildConfigVersion.NO_CAPTURE ? 64 : 54);''')

# 3) 不拍版：不烧水印
s = s.replace('            if (!video) stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis(), antiCodeOf(dest));',
'''            if (!video && !BuildConfigVersion.NO_CAPTURE) {
                stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis(), antiCodeOf(dest));
            }''')

# 4) 不拍版：不检查更新
s = s.replace('        tvUpload.postDelayed(this::checkUpdate, 3000);',
'''        if (!BuildConfigVersion.NO_CAPTURE) {
            tvUpload.postDelayed(this::checkUpdate, 3000);
        }''')

# 5) 首页标题区分
s = s.replace('        title.setText("采集点拍照");',
'''        title.setText(BuildConfigVersion.NO_CAPTURE ? "不拍摄收集" : "采集点拍照");''')

io.open(p, 'w', encoding='utf-8').write(s)
print('MainActivity: 不拍摄模式生效')

# 6) Uploader：不拍版不给视频烧水印
p2 = 'android/src/com/egoops/collect/Uploader.java'
u = io.open(p2, encoding='utf-8').read()
u = u.replace('                        if ("video".equals(m.kind)) watermarked(m);',
'''                        if ("video".equals(m.kind) && !BuildConfigVersion.NO_CAPTURE) watermarked(m);''')
io.open(p2, 'w', encoding='utf-8').write(u)
print('Uploader: 不拍版跳过视频水印')
