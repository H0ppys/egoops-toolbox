"""把预览图里的几何参数原样搬进 Java（WatermarkVideo.drawStamp）。"""

import io

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

start = s.index('    /** 统一的水印画法：打卡标签 + 时间 + 地址（两行）+ 日期 + 小字 */')
end = s.index('    /** 生成和视频同尺寸的透明水印图层 */')

new_block = r'''    /** 水印：按参考样式复刻（打卡徽章 + 钢蓝时间块 + 地址两行 + 日期 + 验证行） */
    public static void drawStamp(Canvas c, int w, int h, String addr) {
        float u = w / 1080f;
        float F = 40 * u;

        java.util.Calendar cal = java.util.Calendar.getInstance();
        String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));
        char[] wk = "日一二三四五六".toCharArray();
        String week = "星期" + wk[cal.get(java.util.Calendar.DAY_OF_WEEK) - 1];
        String hhmm = String.format("%02d:%02d", cal.get(java.util.Calendar.HOUR_OF_DAY),
                cal.get(java.util.Calendar.MINUTE));

        float lineH = 1.42f * F;
        float chipH = 2.30f * F;
        float gap = 0.90f * F;
        float margin = 0.60f * F;
        float barW = 0.42f * F;
        float maxW = w - margin - 0.45f * F;

        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setTypeface(android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT,
                android.graphics.Typeface.BOLD));

        p.setTextSize(F);
        java.util.List<String> lines = splitAddress(p, addr, maxW);

        float blockH = chipH + gap * 0.55f + lines.size() * lineH + gap * 0.35f
                + F + gap * 0.5f + 0.8f * F;
        float top = h - margin - blockH;

        // ---------- 打卡徽章 ----------
        Paint fill = new Paint(Paint.ANTI_ALIAS_FLAG);
        fill.setColor(Color.parseColor("#F5C243"));
        p.setTextSize(1.30f * F);
        float tagPad = 0.30f * F;
        float tagW = p.measureText("打卡") + tagPad * 2;
        android.graphics.RectF r1 = new android.graphics.RectF(margin, top, margin + tagW, top + chipH);
        c.drawRoundRect(r1, 0.15f * F, 0.15f * F, fill);

        Paint stroke = new Paint(Paint.ANTI_ALIAS_FLAG);
        stroke.setStyle(Paint.Style.STROKE);
        stroke.setStrokeWidth(Math.max(1, 0.05f * F));
        stroke.setColor(0x96FFFFFF);
        c.drawRoundRect(r1, 0.15f * F, 0.15f * F, stroke);

        p.setColor(Color.parseColor("#0F0F0F"));
        drawCenteredV(c, p, "打卡", margin + tagPad, top, chipH);

        // ---------- 时间块 ----------
        p.setTextSize(1.55f * F);
        float timeW = p.measureText(hhmm) + 0.44f * F;
        float bx = margin + tagW + 0.12f * F;
        android.graphics.RectF r2 = new android.graphics.RectF(bx, top, bx + timeW, top + chipH);
        Paint chip = new Paint(Paint.ANTI_ALIAS_FLAG);
        chip.setColor(Color.parseColor("#7C92AA"));
        c.drawRoundRect(r2, 0.18f * F, 0.18f * F, chip);
        Paint chipStroke = new Paint(Paint.ANTI_ALIAS_FLAG);
        chipStroke.setStyle(Paint.Style.STROKE);
        chipStroke.setStrokeWidth(Math.max(2, 0.07f * F));
        chipStroke.setColor(0xE6F0F4F8);
        c.drawRoundRect(r2, 0.18f * F, 0.18f * F, chipStroke);

        Paint tp = new Paint(Paint.ANTI_ALIAS_FLAG);
        tp.setTypeface(android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT,
                android.graphics.Typeface.BOLD));
        tp.setTextSize(1.55f * F);
        tp.setColor(Color.WHITE);
        float tyText = top + chipH / 2 + 1.55f * F * 0.36f;
        c.drawText(hhmm, bx + 0.22f * F, tyText, tp);
        c.drawText(hhmm, bx + 0.22f * F + 1f, tyText, tp);

        // ---------- 黄竖条 ----------
        float barTop = top + chipH + gap * 0.55f;
        float barBot = barTop + lines.size() * lineH + gap * 0.3f + F;
        Paint bar = new Paint(Paint.ANTI_ALIAS_FLAG);
        bar.setColor(Color.parseColor("#F5C243"));
        c.drawRect(margin + 0.08f * F, barTop, margin + 0.08f * F + barW, barBot, bar);

        // ---------- 地址 ----------
        float x = margin + 0.08f * F + barW + 0.42f * F;
        float y = barTop + F * 0.86f;
        p.setTextSize(F);
        p.setColor(Color.WHITE);
        p.setShadowLayer(3 * u, 1 * u, 1 * u, 0xB3000000);
        for (String ln : lines) {
            c.drawText(ln, x, y, p);
            y += lineH;
        }

        // ---------- 日期 ----------
        y += gap * 0.3f - lineH + F * 0.86f;
        p.setTextSize(F);
        c.drawText(date + " " + week, x, y, p);

        // ---------- 验证行 ----------
        y += F + gap * 0.45f - F * 0.86f;
        float ic = 0.82f * F;
        shield(c, x, y, ic);
        p.setTextSize(0.80f * F);
        p.setColor(Color.parseColor("#F2F2F2"));
        p.setShadowLayer(2 * u, 1 * u, 1 * u, 0x99000000);
        c.drawText("采集水印已验证 | 时间地点真实", x + ic + 0.35f * F, y + 0.86f * F * 0.9f, p);
    }

    private static void drawCenteredV(Canvas c, Paint p, String text, float x, float top, float h) {
        Paint.FontMetrics fm = p.getFontMetrics();
        float baseline = top + (h - (fm.descent - fm.ascent)) / 2 - fm.ascent;
        c.drawText(text, x, baseline, p);
    }

    /** 盾形勾（矢量画，不依赖字体） */
    private static void shield(Canvas c, float x, float y, float size) {
        float w = size;
        android.graphics.Path path = new android.graphics.Path();
        path.moveTo(x + w * 0.5f, y);
        path.lineTo(x + w * 0.95f, y + w * 0.18f);
        path.lineTo(x + w * 0.95f, y + w * 0.55f);
        path.lineTo(x + w * 0.5f, y + w);
        path.lineTo(x + w * 0.05f, y + w * 0.55f);
        path.lineTo(x + w * 0.05f, y + w * 0.18f);
        path.close();

        Paint s = new Paint(Paint.ANTI_ALIAS_FLAG);
        s.setStyle(Paint.Style.STROKE);
        s.setStrokeWidth(Math.max(2, w * 0.13f));
        s.setStrokeJoin(Paint.Join.ROUND);
        s.setColor(Color.parseColor("#F0F0F0"));
        c.drawPath(path, s);

        android.graphics.Path tick = new android.graphics.Path();
        tick.moveTo(x + w * 0.30f, y + w * 0.50f);
        tick.lineTo(x + w * 0.45f, y + w * 0.66f);
        tick.lineTo(x + w * 0.72f, y + w * 0.33f);
        s.setStrokeWidth(Math.max(2, w * 0.14f));
        c.drawPath(tick, s);
    }

'''
s = s[:start] + new_block + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('Java 水印按实测参数重写')
