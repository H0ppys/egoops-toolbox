"""按你选的 F=38，并把单行宽度限制在 0.74W，长地址仍然断成两行（和参考图一致）。"""

import io
import types

import sys
sys.path.insert(0, "viewer")
from PIL import Image

# ---- Java ----
p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()
assert 'float F = 42 * u;' in s
s = s.replace('float F = 42 * u;', 'float F = 38 * u;')
s = s.replace('        float maxW = w - margin - 0.40f * F;',
              '        float maxW = Math.min(w - margin - 0.40f * F, 0.74f * w);')
io.open(p, 'w', encoding='utf-8').write(s)
print('Java: F=38，行宽限制 0.74W')

# ---- 预览 ----
pv = 'tools/watermark_preview7.py'
t = io.open(pv, encoding='utf-8').read()
t = t.replace('    F = 42 * u', '    F = 38 * u')
t = t.replace('    max_w = w - margin - 0.4 * F', '    max_w = min(w - margin - 0.4 * F, 0.74 * w)')
io.open(pv, 'w', encoding='utf-8').write(t)

code = io.open(pv, encoding='utf-8').read()
mod = types.ModuleType("wm38")
exec(compile(code, "wm38", "exec"), mod.__dict__)
src = Image.open("docs/_sample_photo.jpg").convert("RGB")
w = 1080
h = int(src.height * w / src.width)
photo = src.resize((w, h), Image.LANCZOS)
mod.draw_stamp(photo).save("docs/watermark-real.png")
print("saved docs/watermark-real.png")

# ---- 版本 64 ----
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="63"', 'android:versionCode="64"')
m = m.replace('android:versionName="63.0"', 'android:versionName="64.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v63.apk', 'egoops-collect-v64.apk')
b = b.replace('--version-code 63 --version-name 63.0', '--version-code 64 --version-name 64.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 64')
