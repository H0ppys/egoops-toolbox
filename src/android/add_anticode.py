"""加一个「我们自己的防伪码」：素材文件的 SHA1 前 12 位，烧在水印角落。
   这个码可以拿原文件重算校验，是真的防伪，不是抄别人的。
"""

import io

# ---------- Model ----------
p = 'android/src/com/egoops/collect/Model.java'
s = io.open(p, encoding='utf-8').read()
if 'antiCode' not in s:
    s = s.replace('        public long capturedAt = 0;          // 拍摄时刻（毫秒）',
                  '        public long capturedAt = 0;          // 拍摄时刻（毫秒）\n        public String antiCode = "";         // 防伪码（SHA1 前 12 位）')
    s = s.replace('        o.put("captured_at", capturedAt);',
                  '        o.put("captured_at", capturedAt);\n        o.put("anti_code", antiCode);')
    s = s.replace('        m.capturedAt = o.optLong("captured_at");',
                  '        m.capturedAt = o.optLong("captured_at");\n        m.antiCode = o.optString("anti_code");')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Model: antiCode')

# ---------- WatermarkVideo：右下角画防伪码 ----------
p2 = 'android/src/com/egoops/collect/WatermarkVideo.java'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('    public static void drawStamp(Canvas c, int w, int h, String addr, long whenMs) {',
              '    public static void drawStamp(Canvas c, int w, int h, String addr, long whenMs, String antiCode) {')
t = t.replace('    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h, long whenMs) {',
              '    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h, long whenMs, String antiCode) {')
t = t.replace('            drawStamp(c, w, h, addr, whenMs);', '            drawStamp(c, w, h, addr, whenMs, antiCode);')

# 在验证行之后追加防伪码
t = t.replace('''        c.drawText("采集水印相机已验证 | 时间地点真实", x + ic + 0.30f * F,
                y + 0.78f * F * 0.9f, small);
    }''',
'''        c.drawText("采集水印相机已验证 | 时间地点真实", x + ic + 0.30f * F,
                y + 0.78f * F * 0.9f, small);

        if (antiCode != null && !antiCode.isEmpty()) {
            Paint code = new Paint(Paint.ANTI_ALIAS_FLAG);
            code.setTypeface(p.getTypeface());
            code.setTextSize(0.62f * F);
            code.setColor(0xCCFFFFFF);
            code.setShadowLayer(Math.max(1, 0.03f * F), 1, 1, 0x99000000);
            String line = "防伪 " + antiCode;
            float cw = code.measureText(line);
            c.drawText(line, w - margin - cw, h - margin * 0.55f, code);
        }
    }''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('WatermarkVideo: 防伪码')

# ---------- MainActivity：算 SHA1 并传 ----------
p3 = 'android/src/com/egoops/collect/MainActivity.java'
a = io.open(p3, encoding='utf-8').read()

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
    anchor = '    /** 照片烧水印（样式与视频一致） */'
    assert anchor in a
    a = a.replace(anchor, helper + anchor, 1)

a = a.replace('            if (!video) stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis());',
              '            if (!video) stampWatermark(dest, dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis(), antiCodeOf(dest));')

a = a.replace('''        m.capturedAt = dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis();''',
'''        m.capturedAt = dest.lastModified() > 0 ? dest.lastModified() : System.currentTimeMillis();
        if (m.antiCode == null || m.antiCode.isEmpty()) m.antiCode = antiCodeOf(dest);''')

io.open(p3, 'w', encoding='utf-8').write(a)
print('MainActivity: 算防伪码')

# ---------- Uploader：视频水印带防伪码 ----------
p4 = 'android/src/com/egoops/collect/Uploader.java'
u = io.open(p4, encoding='utf-8').read()
u = u.replace('''            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1, when);''',
'''            String code = m.antiCode == null ? "" : m.antiCode;
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
                    wmAddr, "", "", w & ~1, h & ~1, when, code);''')
io.open(p4, 'w', encoding='utf-8').write(u)
print('Uploader: 视频带防伪码')

# 版本 66
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="65"', 'android:versionCode="66"')
m = m.replace('android:versionName="65.0"', 'android:versionName="66.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v65.apk', 'egoops-collect-v66.apk')
b = b.replace('--version-code 65 --version-name 65.0', '--version-code 66 --version-name 66.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 66')
