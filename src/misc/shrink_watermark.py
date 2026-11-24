"""把水印缩小一档：F 50 → 42（所有元素等比缩），并生成单张效果图。"""

import io
import sys

sys.path.insert(0, "viewer")

from PIL import Image

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()
assert 'float F = 50 * u;' in s
s = s.replace('float F = 50 * u;', 'float F = 42 * u;')
io.open(p, 'w', encoding='utf-8').write(s)
print('Java: F=42')

# 预览同步
pv = 'tools/watermark_preview7.py'
t = io.open(pv, encoding='utf-8').read()
t = t.replace('    F = 50 * u', '    F = 42 * u')
io.open(pv, 'w', encoding='utf-8').write(t)

# 生成单张效果
import types
code = io.open(pv, encoding='utf-8').read()
mod = types.ModuleType("wm42")
exec(compile(code, "wm42", "exec"), mod.__dict__)

src = Image.open("docs/_sample_photo.jpg").convert("RGB")
w = 1080
h = int(src.height * w / src.width)
photo = src.resize((w, h), Image.LANCZOS)
mod.draw_stamp(photo).save("docs/watermark-real.png")
print("saved docs/watermark-real.png")

# 版本 63
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="62"', 'android:versionCode="63"')
m = m.replace('android:versionName="62.0"', 'android:versionName="63.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v62.apk', 'egoops-collect-v63.apk')
b = b.replace('--version-code 62 --version-name 62.0', '--version-code 63 --version-name 63.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 63')
