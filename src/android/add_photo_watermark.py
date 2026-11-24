"""照片加水印（地址 + 日期 + 时间 + 门店 + 采集员），样式接近「打卡水印相机」。

视频目前无法烧录（系统相机录的，App 拿不到画面），先做照片；视频另议。
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 复制完文件后，照片就加水印
old = '''            try { getContentResolver().delete(src, null, null); } catch (Exception ignored) {}

            String problem = checkQuality(dest.getAbsolutePath(), video);'''
new = '''            try { getContentResolver().delete(src, null, null); } catch (Exception ignored) {}

            if (!video) stampWatermark(dest);

            String problem = checkQuality(dest.getAbsolutePath(), video);'''
assert old in s
s = s.replace(old, new)

# 2) 水印实现
if 'private void stampWatermark' not in s:
    anchor = '    private void askTask(String presetArea) {'
    block = r'''    /** 把地址/日期/时间/门店/采集员烧进照片（和打卡水印相机一个意思） */
    private void stampWatermark(File f) {
        try {
            android.graphics.BitmapFactory.Options o = new android.graphics.BitmapFactory.Options();
            o.inJustDecodeBounds = true;
            android.graphics.BitmapFactory.decodeFile(f.getAbsolutePath(), o);
            int sample = 1;
            int maxSide = Math.max(o.outWidth, o.outHeight);
            while (maxSide / sample > 2048) sample *= 2;
            o.inJustDecodeBounds = false;
            o.inSampleSize = sample;
            android.graphics.Bitmap src = android.graphics.BitmapFactory.decodeFile(f.getAbsolutePath(), o);
            if (src == null) return;

            android.graphics.Bitmap bmp = src.copy(android.graphics.Bitmap.Config.ARGB_8888, true);
            src.recycle();
            android.graphics.Canvas c = new android.graphics.Canvas(bmp);
            int W = bmp.getWidth();
            int H = bmp.getHeight();
            float u = W / 1080f;                    // 以 1080 宽为基准

            String addr = (site.address == null || site.address.trim().isEmpty()) ? "（未填地址）" : site.address.trim();
            String store = site.name == null ? "" : site.name.trim();
            String who = (site.collector == null || site.collector.trim().isEmpty()) ? "" : site.collector.trim();

            java.util.Calendar cal = java.util.Calendar.getInstance();
            String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                    cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));
            char[] wk = "日一二三四五六".toCharArray();
            String week = "星期" + wk[cal.get(java.util.Calendar.DAY_OF_WEEK) - 1];
            String hhmm = String.format("%02d:%02d", cal.get(java.util.Calendar.HOUR_OF_DAY),
                    cal.get(java.util.Calendar.MINUTE));

            android.graphics.Paint p = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
            p.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);

            // 文字最大宽度，地址按宽度折行
            float pad = 34 * u;
            float maxW = W - pad * 2 - 120 * u;
            p.setTextSize(38 * u);
            java.util.List<String> lines = new java.util.ArrayList<>();
            StringBuilder cur = new StringBuilder();
            for (char ch : addr.toCharArray()) {
                cur.append(ch);
                if (p.measureText(cur.toString()) > maxW) {
                    cur.deleteCharAt(cur.length() - 1);
                    if (cur.length() > 0) lines.add(cur.toString());
                    cur = new StringBuilder().append(ch);
                    if (lines.size() >= 2) break;
                }
            }
            if (lines.size() < 2 && cur.length() > 0) lines.add(cur.toString());

            // 背景块高度
            float lineH = 46 * u;
            float blockH = pad * 2 + 70 * u + lines.size() * lineH + 44 * u;
            float top = H - pad - blockH;

            android.graphics.Paint bg = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
            bg.setColor(android.graphics.Color.parseColor("#99000000"));
            android.graphics.RectF rf = new android.graphics.RectF(pad * 0.4f, top, W - pad * 0.4f, H - pad * 0.4f);
            c.drawRoundRect(rf, 18 * u, 18 * u, bg);

            // 左侧黄条
            android.graphics.Paint bar = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
            bar.setColor(android.graphics.Color.parseColor("#FFC400"));
            c.drawRect(pad * 0.4f, top + 18 * u, pad * 0.4f + 8 * u, H - pad * 0.4f - 18 * u, bar);

            float x = pad * 0.4f + 26 * u;
            float y = top + pad + 30 * u;

            // 打卡 + 时间
            p.setColor(android.graphics.Color.parseColor("#FFC400"));
            p.setTextSize(46 * u);
            c.drawText("打卡", x, y, p);
            float tw = p.measureText("打卡");
            p.setColor(android.graphics.Color.WHITE);
            c.drawText(" " + hhmm, x + tw, y, p);

            // 地址
            p.setColor(android.graphics.Color.WHITE);
            p.setTextSize(38 * u);
            y += 62 * u;
            for (String ln : lines) {
                c.drawText(ln, x, y, p);
                y += lineH;
            }

            // 日期 + 星期（+ 门店）
            p.setTextSize(34 * u);
            String bottom = date + " " + week + (store.isEmpty() ? "" : "  " + store)
                    + (who.isEmpty() ? "" : "  " + who);
            c.drawText(bottom, x, y + 8 * u, p);

            java.io.FileOutputStream out = new java.io.FileOutputStream(f);
            bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 92, out);
            out.close();
            bmp.recycle();
        } catch (Exception e) {
            // 水印失败不影响拍摄
        }
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('照片水印已加')
