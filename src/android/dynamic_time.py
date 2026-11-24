"""水印的时间改成「素材拍摄那一刻」：
   · 照片/视频在拍完落盘时记录 capturedAt
   · 水印按 capturedAt 画时间（不再用「加水印那一刻」）
   · 视频是整段恒定时间（同真实水印相机：显示开拍时间）
"""

import io

# ---------- Model：capturedAt ----------
p = 'android/src/com/egoops/collect/Model.java'
s = io.open(p, encoding='utf-8').read()
if 'capturedAt' not in s:
    s = s.replace('        public String watermarkSrc = "";     // 加水印前的原文件路径',
                  '        public String watermarkSrc = "";     // 加水印前的原文件路径\n        public long capturedAt = 0;          // 拍摄时刻（毫秒）')
    # 序列化
    s = s.replace('        o.put("shot", shot);', '        o.put("shot", shot);\n        o.put("captured_at", capturedAt);')
    s = s.replace('        shot = o.optString("shot");', '        shot = o.optString("shot");\n        m.capturedAt = o.optLong("captured_at");')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Model: capturedAt')

# ---------- WatermarkVideo：按给定时刻画 ----------
p2 = 'android/src/com/egoops/collect/WatermarkVideo.java'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('    public static void drawStamp(Canvas c, int w, int h, String addr) {',
              '    public static void drawStamp(Canvas c, int w, int h, String addr, long whenMs) {')

t = t.replace('''        java.util.Calendar cal = java.util.Calendar.getInstance();
        String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));''',
'''        java.util.Calendar cal = java.util.Calendar.getInstance();
        if (whenMs > 0) cal.setTimeInMillis(whenMs);
        String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));''')

t = t.replace('    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h) {',
              '    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h, long whenMs) {')
t = t.replace('            drawStamp(c, w, h, addr);', '            drawStamp(c, w, h, addr, whenMs);')

io.open(p2, 'w', encoding='utf-8').write(t)
print('WatermarkVideo: 按 whenMs 画')

# ---------- Uploader：传 capturedAt ----------
p3 = 'android/src/com/egoops/collect/Uploader.java'
u = io.open(p3, encoding='utf-8').read()
u = u.replace('''            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1);''',
'''            long when = m.capturedAt > 0 ? m.capturedAt : src.lastModified();
            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1, when);''')
io.open(p3, 'w', encoding='utf-8').write(u)
print('Uploader: 用拍摄时刻')

# ---------- MainActivity：照片按拍摄时刻；落盘时记录 ----------
p4 = 'android/src/com/egoops/collect/MainActivity.java'
a = io.open(p4, encoding='utf-8').read()

a = a.replace('    private void stampWatermark(File f) {',
              '    private void stampWatermark(File f, long whenMs) {')
a = a.replace('            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr);',
              '            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr, whenMs);')
a = a.replace('            if (!video) stampWatermark(dest);',
              '            if (!video) stampWatermark(dest, System.currentTimeMillis());')

io.open(p4, 'w', encoding='utf-8').write(a)
print('MainActivity: 照片用当前拍摄时刻')

# ---------- 记录 capturedAt：新建 Media 的地方 ----------
# 找到创建 Media 并加入 task.media 的位置
import re
idx = a.find('task.media.add')
print('task.media.add 位置:', idx)

io.open('tools/_note.txt', 'w', encoding='utf-8').write('ok')
