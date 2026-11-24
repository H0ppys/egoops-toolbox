"""视频水印接线：
   1) WatermarkVideo 增加静态方法 makeOverlay()（生成透明水印图层）
   2) Uploader 上传视频前先烧水印，失败就用原文件
   3) App 的「从相册选」按钮文案改成明确的水印相机提示
"""

import io

# ---------- 1) 叠加层生成 ----------
p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

if 'makeOverlay' not in s:
    anchor = '    public WatermarkVideo(Bitmap overlay, int width, int height) {'
    block = '''    /** 生成一张和视频同尺寸的透明水印图层（左下角打卡块） */
    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h) {
        try {
            Bitmap bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
            Canvas c = new Canvas(bmp);
            float u = w / 1080f;

            Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
            p.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);

            java.util.Calendar cal = java.util.Calendar.getInstance();
            String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                    cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));
            char[] wk = "日一二三四五六".toCharArray();
            String week = "星期" + wk[cal.get(java.util.Calendar.DAY_OF_WEEK) - 1];
            String hhmm = String.format("%02d:%02d", cal.get(java.util.Calendar.HOUR_OF_DAY),
                    cal.get(java.util.Calendar.MINUTE));

            float pad = 34 * u;
            p.setTextSize(38 * u);
            float maxW = w - pad * 2 - 120 * u;
            java.util.List<String> lines = new java.util.ArrayList<>();
            StringBuilder cur = new StringBuilder();
            String text = (addr == null || addr.trim().isEmpty()) ? "（未填地址）" : addr.trim();
            for (char ch : text.toCharArray()) {
                cur.append(ch);
                if (p.measureText(cur.toString()) > maxW) {
                    cur.deleteCharAt(cur.length() - 1);
                    if (cur.length() > 0) lines.add(cur.toString());
                    cur = new StringBuilder().append(ch);
                    if (lines.size() >= 2) break;
                }
            }
            if (lines.size() < 2 && cur.length() > 0) lines.add(cur.toString());

            float lineH = 46 * u;
            float blockH = pad * 2 + 70 * u + lines.size() * lineH + 44 * u;
            float top = h - pad - blockH;

            Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG);
            bg.setColor(Color.parseColor("#99000000"));
            android.graphics.RectF rf = new android.graphics.RectF(pad * 0.4f, top, w - pad * 0.4f, h - pad * 0.4f);
            c.drawRoundRect(rf, 18 * u, 18 * u, bg);

            Paint bar = new Paint(Paint.ANTI_ALIAS_FLAG);
            bar.setColor(Color.parseColor("#FFC400"));
            c.drawRect(pad * 0.4f, top + 18 * u, pad * 0.4f + 8 * u, h - pad * 0.4f - 18 * u, bar);

            float x = pad * 0.4f + 26 * u;
            float y = top + pad + 30 * u;
            p.setColor(Color.parseColor("#FFC400"));
            p.setTextSize(46 * u);
            c.drawText("打卡", x, y, p);
            float tw = p.measureText("打卡");
            p.setColor(Color.WHITE);
            c.drawText(" " + hhmm, x + tw, y, p);

            p.setColor(Color.WHITE);
            p.setTextSize(38 * u);
            y += 62 * u;
            for (String ln : lines) {
                c.drawText(ln, x, y, p);
                y += lineH;
            }
            p.setTextSize(34 * u);
            String bottom = date + " " + week
                    + (store == null || store.isEmpty() ? "" : "  " + store)
                    + (who == null || who.isEmpty() ? "" : "  " + who);
            c.drawText(bottom, x, y + 8 * u, p);
            return bmp;
        } catch (Throwable t) {
            return null;
        }
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('makeOverlay 已加')

# ---------- 2) Uploader 上传前烧水印 ----------
p2 = 'android/src/com/egoops/collect/Uploader.java'
t = io.open(p2, encoding='utf-8').read()

if 'WatermarkVideo' not in t:
    old = '''                stage("上传：" + task.name + " · " + new File(m.path).getName());
                sentAll += uploadOneWithRetry(task, m);'''
    new = '''                stage("上传：" + task.name + " · " + new File(m.path).getName());
                if ("video".equals(m.kind)) watermarked(m);
                sentAll += uploadOneWithRetry(task, m);'''
    assert old in t
    t = t.replace(old, new)

    helper = '''    /** 视频上传前烧水印；失败就用原文件，不阻断上传 */
    private void watermarked(Model.Media m) {
        File src = new File(m.path);
        if (!src.exists() || src.length() > 200L * 1024 * 1024) return;
        File out = new File(src.getParentFile(), "wm_" + src.getName());
        try {
            android.graphics.Bitmap probe = android.graphics.BitmapFactory.decodeFile(m.thumbPath);
            int w = 0, h = 0;
            try {
                android.media.MediaMetadataRetriever r = new android.media.MediaMetadataRetriever();
                r.setDataSource(src.getAbsolutePath());
                w = Integer.parseInt(r.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH));
                h = Integer.parseInt(r.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT));
                r.release();
            } catch (Throwable ignored) {}
            if (w <= 0 || h <= 0) return;

            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    site.address, site.name, site.collector, w & ~1, h & ~1);
            if (overlay == null) return;
            stage("给视频加水印：" + src.getName());
            WatermarkVideo wv = new WatermarkVideo(overlay, w, h);
            boolean ok = wv.burn(src, out);
            overlay.recycle();
            if (ok && out.exists() && out.length() > 0) {
                String old = m.path;
                m.path = out.getAbsolutePath();
                m.watermarkSrc = old;
            }
        } catch (Throwable ignored) {
        }
    }

'''
    anchor2 = '    /** 把后加的区域任务登记到服务器，拿回 task_id */'
    t = t.replace(anchor2, helper + anchor2, 1)
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('Uploader 烧水印已接线')
