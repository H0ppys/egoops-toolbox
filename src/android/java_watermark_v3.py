"""按最终实测参数重写 Java drawStamp（渐变时间块、数字描边、轻字重）。"""

import io

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

start = s.index('    /** 水印：按参考样式复刻（打卡徽章 + 钢蓝时间块 + 地址两行 + 日期 + 验证行） */')
end = s.index('    /** 地址断行：第一行尽量排满，在 区/街道/路/号 等处断开 */')

new_block = r'''    /** 水印：按参考样式复刻（打卡徽章 + 渐变时间块 + 地址两行 + 日期 + 验证行） */
    public static void drawStamp(Canvas c, int w, int h, String addr) {
        float u = w / 1080f;
        float F = 50 * u;

        java.util.Calendar cal = java.util.Calendar.getInstance();
        String date = String.format("%04d.%02d.%02d", cal.get(java.util.Calendar.YEAR),
                cal.get(java.util.Calendar.MONTH) + 1, cal.get(java.util.Calendar.DAY_OF_MONTH));
        char[] wk = "日一二三四五六".toCharArray();
        String week = "星期" + wk[cal.get(java.util.Calendar.DAY_OF_WEEK) - 1];
        String hhmm = String.format("%02d:%02d", cal.get(java.util.Calendar.HOUR_OF_DAY),
                cal.get(java.util.Calendar.MINUTE));

        float chipH = 2.15f * F;
        float gapChip = 0.93f * F;
        float lineH = 1.30f * F;
        float offDate = 1.62f * F;
        float offSmall = 1.72f * F;
        float margin = 0.55f * F;
        float barW = 0.40f * F;
        float maxW = w - margin - 0.40f * F;

        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setTypeface(android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT,
                android.graphics.Typeface.BOLD));
        p.setTextSize(F);
        java.util.List<String> lines = splitAddress(p, addr, maxW);

        float blockH = chipH + gapChip + lines.size() * lineH + offDate + offSmall;
        float top = h - margin - blockH;

        // ---------- 打卡徽章 ----------
        p.setTextSize(1.12f * F);
        float tagPad = 0.16f * F;
        float tagW = p.measureText("打卡") + tagPad * 2;
        android.graphics.RectF r1 = new android.graphics.RectF(margin, top, margin + tagW, top + chipH);
        Paint yellow = new Paint(Paint.ANTI_ALIAS_FLAG);
        yellow.setColor(Color.parseColor("#F6C23C"));
        c.drawRoundRect(r1, 0.12f * F, 0.12f * F, yellow);
        Paint edge = new Paint(Paint.ANTI_ALIAS_FLAG);
        edge.setStyle(Paint.Style.STROKE);
        edge.setStrokeWidth(Math.max(1, 0.04f * F));
        edge.setColor(0x78FFFFFF);
        c.drawRoundRect(r1, 0.12f * F, 0.12f * F, edge);

        p.setColor(Color.parseColor("#0F0F0F"));
        drawV(c, p, "打卡", margin + tagPad, top, chipH);

        // ---------- 时间块（上浅下深渐变 + 浅描边） ----------
        p.setTextSize(1.55f * F);
        float timePad = 0.08f * F;
        float timeW = p.measureText(hhmm) + timePad * 2;
        float bx = margin + tagW + 0.08f * F;
        android.graphics.RectF r2 = new android.graphics.RectF(bx, top, bx + timeW, top + chipH);
        Paint chip = new Paint(Paint.ANTI_ALIAS_FLAG);
        chip.setShader(new android.graphics.LinearGradient(bx, top, bx, top + chipH,
                Color.parseColor("#B0BCCB"), Color.parseColor("#828EA3"),
                android.graphics.Shader.TileMode.CLAMP));
        c.drawRoundRect(r2, 0.14f * F, 0.14f * F, chip);
        Paint chipEdge = new Paint(Paint.ANTI_ALIAS_FLAG);
        chipEdge.setStyle(Paint.Style.STROKE);
        chipEdge.setStrokeWidth(Math.max(1, 0.05f * F));
        chipEdge.setColor(0xE6F0F5FA);
        c.drawRoundRect(r2, 0.14f * F, 0.14f * F, chipEdge);

        Paint num = new Paint(Paint.ANTI_ALIAS_FLAG);
        num.setTypeface(p.getTypeface());
        num.setTextSize(1.55f * F);
        num.setStyle(Paint.Style.STROKE);
        num.setStrokeWidth(Math.max(2, 0.03f * F));
        num.setColor(0xC81E2C3C);
        drawV(c, num, hhmm, bx + timePad, top, chipH);
        num.setStyle(Paint.Style.FILL);
        num.setColor(Color.WHITE);
        drawV(c, num, hhmm, bx + timePad, top, chipH);

        // ---------- 黄竖条 ----------
        float barTop = top + chipH + gapChip * 0.55f;
        float barBot = barTop + lines.size() * lineH + offDate * 0.62f;
        Paint bar = new Paint(Paint.ANTI_ALIAS_FLAG);
        bar.setColor(Color.parseColor("#F6C23C"));
        c.drawRect(margin + 0.06f * F, barTop, margin + 0.06f * F + barW, barBot, bar);

        // ---------- 地址 ----------
        float x = margin + 0.06f * F + barW + 0.36f * F;
        float y = barTop + 0.10f * F;
        Paint txt = new Paint(Paint.ANTI_ALIAS_FLAG);
        txt.setTypeface(p.getTypeface());
        txt.setTextSize(F);
        txt.setShadowLayer(Math.max(1, 0.04f * F), 1, 1, 0xA5000000);
        txt.setColor(Color.WHITE);
        for (String ln : lines) {
            c.drawText(ln, x, y + F * 0.86f, txt);
            y += lineH;
        }

        // ---------- 日期 ----------
        y += offDate - lineH + 0.10f * F;
        c.drawText(date + " " + week, x, y + F * 0.86f, txt);

        // ---------- 验证行 ----------
        y += offSmall - 0.15f * F;
        float ic = 0.72f * F;
        shield(c, x, y, ic);
        Paint small = new Paint(Paint.ANTI_ALIAS_FLAG);
        small.setTypeface(p.getTypeface());
        small.setTextSize(0.78f * F);
        small.setColor(Color.parseColor("#F2F2F2"));
        small.setShadowLayer(Math.max(1, 0.03f * F), 1, 1, 0x99000000);
        c.drawText("采集水印已验证 | 时间地点真实", x + ic + 0.30f * F,
                y + 0.78f * F * 0.9f, small);
    }

    /** 在给定高度内垂直居中绘制 */
    private static void drawV(Canvas c, Paint p, String text, float x, float top, float h) {
        Paint.FontMetrics fm = p.getFontMetrics();
        float baseline = top + (h - (fm.descent - fm.ascent)) / 2f - fm.ascent;
        c.drawText(text, x, baseline, p);
    }

'''
s = s[:start] + new_block + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)

# 版本 59
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="58"', 'android:versionCode="59"').replace('android:versionName="58.0"', 'android:versionName="59.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v58.apk', 'egoops-collect-v59.apk').replace('--version-code 58 --version-name 58.0', '--version-code 59 --version-name 59.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('Java 水印最终版 + 版本 59')
