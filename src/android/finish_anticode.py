"""补完防伪码接线（MainActivity + Uploader），锚点用真实文本。"""

import io

# ---------- MainActivity ----------
p = 'android/src/com/egoops/collect/MainActivity.java'
a = io.open(p, encoding='utf-8').read()

a = a.replace('    private void stampWatermark(File f, long whenMs) {',
              '    private void stampWatermark(File f, long whenMs, String antiCode) {')
a = a.replace('            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr, whenMs);',
              '            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr, whenMs, antiCode);')

if 'antiCodeOf' not in a:
    helper = '''    /** 素材防伪码：文件 SHA1 的前 12 位（大写） */
    private static String antiCodeOf(File f) {
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-1");
            java.io.FileInputStream in = new java.io.FileInputStream(f);
            byte[] buf = new byte[64 * 1024];
            int n;
            while ((n = in.read(buf)) > 0) md.update(buf, 0, n);
            in.close();
            byte[] d = md.digest();
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 6; i++) sb.append(String.format("%02X", d[i]));
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }

'''
    anchor = '    /** 把地址/日期/时间/门店/采集员烧进照片（和打卡水印相机一个意思） */'
    assert anchor in a
    a = a.replace(anchor, helper + anchor, 1)

a = a.replace('            if (!video) stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis());',
              '            if (!video) stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis(), antiCodeOf(dest));')

a = a.replace('        m.capturedAt = dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis();',
              '        m.capturedAt = dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis();\n        if (m.antiCode == null || m.antiCode.isEmpty()) m.antiCode = antiCodeOf(dest);')

io.open(p, 'w', encoding='utf-8').write(a)
print('MainActivity 完成')

# ---------- Uploader ----------
p2 = 'android/src/com/egoops/collect/Uploader.java'
u = io.open(p2, encoding='utf-8').read()

old = '''            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1, when);'''
new = '''            String code = m.antiCode == null ? "" : m.antiCode;
            if (code.isEmpty()) {
                try {
                    java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-1");
                    java.io.FileInputStream in = new java.io.FileInputStream(src);
                    byte[] buf = new byte[64 * 1024];
                    int n;
                    while ((n = in.read(buf)) > 0) md.update(buf, 0, n);
                    in.close();
                    byte[] d = md.digest();
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < 6; i++) sb.append(String.format("%02X", d[i]));
                    code = sb.toString();
                    m.antiCode = code;
                } catch (Exception ignored) {
                }
            }
            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1, when, code);'''
assert old in u
u = u.replace(old, new)
io.open(p2, 'w', encoding='utf-8').write(u)
print('Uploader 完成')

# 版本号提升到 66（若之前未改）
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="65"', 'android:versionCode="66"').replace('android:versionName="65.0"', 'android:versionName="66.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v65.apk', 'egoops-collect-v66.apk').replace('--version-code 65 --version-name 65.0', '--version-code 66 --version-name 66.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 66')
