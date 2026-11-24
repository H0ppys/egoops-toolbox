"""把预览好的水印样式落到 Java：WatermarkVideo.drawStamp() 统一画，
   照片和视频都用它，保证两种素材一模一样。
"""

import io

# ---------------- 1) WatermarkVideo：统一的水印画法 ----------------
p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

# 删掉旧的 makeOverlay 与 旧的画法，换成 drawStamp + 新的 makeOverlay
start = s.index('    /** 生成一张和视频同尺寸的透明水印图层（左下角打卡块） */') if '/** 生成一张和视频同尺寸的透明水印图层（左下角打卡块） */' in s else s.index('    /** 把地址/日期/时间/门店/采集员烧进照片（和打卡水印相机一个意思） */')
end = s.index('    public WatermarkVideo(Bitmap overlay, int width, int height) {')

new_block = r'''    /** 统一的水印画法：打卡标签 + 时间 + 地址（两行）+ 日期 + 小字 */
    public static void drawStamp(Canvas c, int w, int h, String addr) {
        float u = w / 1080f;

        java.util.Calendar cal = java.util.Calendar.getInstance();
        String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));
        char[] wk = "日一二三四五六".toCharArray();
        String week = "星期" + wk[cal.get(java.util.Calendar.DAY_OF_WEEK) - 1];
        String hhmm = String.format("%02d:%02d", cal.get(java.util.Calendar.HOUR_OF_DAY),
                cal.get(java.util.Calendar.MINUTE));

        float margin = 46 * u;
        float lineH = 52 * u;
        float dateH = 48 * u;
        float smallH = 34 * u;
        float tagH = 50 * u;

        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setTypeface(android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT,
                android.graphics.Typeface.BOLD));
        p.setShadowLayer(4 * u, 0, 2 * u, 0xCC000000);

        float maxW = w - margin * 2 - 26 * u;
        p.setTextSize(38 * u);
        java.util.List<String> lines = splitAddress(p, addr, maxW);

        float blockH = tagH + 16 * u + lines.size() * lineH + dateH + smallH + 10 * u;
        float top = h - margin - blockH;

        // 打卡标签
        Paint tag = new Paint(Paint.ANTI_ALIAS_FLAG);
        tag.setColor(Color.parseColor("#FFC400"));
        p.setTextSize(36 * u);
        float tagW = p.measureText("打卡") + 26 * u;
        android.graphics.RectF rf1 = new android.graphics.RectF(margin, top, margin + tagW, top + tagH);
        c.drawRoundRect(rf1, 6 * u, 6 * u, tag);
        p.setColor(Color.parseColor("#141414"));
        c.drawText("打卡", margin + 13 * u, top + 7 * u + 36 * u * 0.86f, p);

        // 时间块
        Paint timeBg = new Paint(Paint.ANTI_ALIAS_FLAG);
        timeBg.setColor(Color.parseColor("#1A1A1A"));
        p.setTextSize(46 * u);
        float tw = p.measureText(hhmm) + 22 * u;
        float tx0 = margin + tagW + 8 * u;
        android.graphics.RectF rf2 = new android.graphics.RectF(tx0, top, tx0 + tw, top + tagH);
        c.drawRoundRect(rf2, 6 * u, 6 * u, timeBg);
        p.setColor(Color.WHITE);
        c.drawText(hhmm, tx0 + 11 * u, top + 3 * u + 46 * u * 0.86f, p);

        // 左侧黄条
        Paint bar = new Paint(Paint.ANTI_ALIAS_FLAG);
        bar.setColor(Color.parseColor("#FFC400"));
        float barTop = top + tagH + 14 * u;
        float barBot = barTop + lines.size() * lineH + dateH - 8 * u;
        c.drawRect(margin, barTop, margin + 6 * u, barBot, bar);

        // 地址
        float x = margin + 18 * u;
        float y = barTop + 38 * u * 0.86f;
        p.setTextSize(38 * u);
        p.setColor(Color.WHITE);
        for (String ln : lines) {
            c.drawText(ln, x, y, p);
            y += lineH;
        }

        // 日期
        y += 2 * u;
        p.setTextSize(36 * u);
        c.drawText(date + " " + week, x, y, p);
        y += dateH;

        // 底部小字
        p.setTextSize(25 * u);
        p.setColor(Color.parseColor("#CFCFCF"));
        p.setShadowLayer(3 * u, 0, 1 * u, 0xAA000000);
        c.drawText("采集水印已验证  |  时间地点真实", x, y, p);
    }

    /** 地址断行：优先在 区/街道/路/号 处断开，并让两行长度接近 */
    private static java.util.List<String> splitAddress(Paint p, String text, float maxW) {
        java.util.List<String> out = new java.util.ArrayList<>();
        if (text == null) text = "";
        text = text.trim();
        if (text.isEmpty()) {
            out.add("（未获取到定位）");
            return out;
        }
        if (p.measureText(text) <= maxW) {
            out.add(text);
            return out;
        }
        String boundaryChars = "区街道路号镇乡村巷弄段";
        int best = -1;
        int bestScore = Integer.MAX_VALUE;
        for (int i = 1; i < text.length(); i++) {
            if (boundaryChars.indexOf(text.charAt(i - 1)) < 0) continue;
            String a = text.substring(0, i);
            String b = text.substring(i);
            if (p.measureText(a) > maxW || p.measureText(b) > maxW) continue;
            int score = Math.abs(a.length() - b.length());
            if (score < bestScore) {
                bestScore = score;
                best = i;
            }
        }
        if (best > 0) {
            out.add(text.substring(0, best));
            out.add(text.substring(best));
            return out;
        }
        // 硬断
        StringBuilder cur = new StringBuilder();
        for (char ch : text.toCharArray()) {
            if (p.measureText(cur.toString() + ch) > maxW && cur.length() > 0) {
                out.add(cur.toString());
                cur = new StringBuilder();
                if (out.size() == 1) break;
            }
            cur.append(ch);
        }
        String rest = text.substring(out.isEmpty() ? 0 : out.get(0).length());
        if (!rest.isEmpty()) out.add(rest);
        return out;
    }

    /** 生成和视频同尺寸的透明水印图层 */
    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h) {
        try {
            Bitmap bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
            Canvas c = new Canvas(bmp);
            drawStamp(c, w, h, addr);
            return bmp;
        } catch (Throwable t) {
            return null;
        }
    }

'''
s = s[:start] + new_block + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('WatermarkVideo: 统一 drawStamp')

# ---------------- 2) MainActivity：照片用同一个画法 ----------------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

a = t.index('    /** 把地址/日期/时间/门店/采集员烧进照片（和打卡水印相机一个意思） */')
b = t.index('    /** 任务1 的区域填写：写回当前任务，不新建 */')

new_photo = r'''    /** 照片烧水印（样式与视频一致） */
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

            String gps = gpsAddress == null ? "" : gpsAddress.trim();
            String addr = gps.isEmpty()
                    ? ((site.address == null || site.address.trim().isEmpty()) ? "" : site.address.trim() + "（自填）")
                    : gps;

            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr);

            java.io.FileOutputStream out = new java.io.FileOutputStream(f);
            bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 92, out);
            out.close();
            bmp.recycle();
        } catch (Exception e) {
            // 水印失败不影响拍摄
        }
    }

'''
t = t[:a] + new_photo + t[b:]
io.open(p2, 'w', encoding='utf-8').write(t)
print('MainActivity: 照片水印改用 drawStamp')
