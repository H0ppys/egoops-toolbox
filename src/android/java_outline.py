"""Java 端也加四向描边（浅色背景上更清楚），与预览一致。"""

import io

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

old = '''        for (String ln : lines) {
            c.drawText(ln, x, y + F * 0.86f, txt);
            y += lineH;
        }

        // ---------- 日期 ----------
        y += offDate - lineH + 0.10f * F;
        c.drawText(date + " " + week, x, y + F * 0.86f, txt);'''

new = '''        float off = Math.max(1.5f, 0.045f * F);
        Paint dark = new Paint(txt);
        dark.setColor(0xAA000000);
        dark.clearShadowLayer();
        for (String ln : lines) {
            for (int dx = -1; dx <= 1; dx += 2) {
                for (int dy = -1; dy <= 1; dy += 2) {
                    c.drawText(ln, x + dx * off, y + F * 0.86f + dy * off, dark);
                }
            }
            c.drawText(ln, x, y + F * 0.86f, txt);
            y += lineH;
        }

        // ---------- 日期 ----------
        y += offDate - lineH + 0.10f * F;
        for (int dx = -1; dx <= 1; dx += 2) {
            for (int dy = -1; dy <= 1; dy += 2) {
                c.drawText(date + " " + week, x + dx * off, y + F * 0.86f + dy * off, dark);
            }
        }
        c.drawText(date + " " + week, x, y + F * 0.86f, txt);'''

assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('Java 四向描边已加')

# 版本 62
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="61"', 'android:versionCode="62"')
m = m.replace('android:versionName="61.0"', 'android:versionName="62.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v61.apk', 'egoops-collect-v62.apk')
b = b.replace('--version-code 61 --version-name 61.0', '--version-code 62 --version-name 62.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 62')
