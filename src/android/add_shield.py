import io

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

if 'private static void shield(' not in s:
    method = r'''    /** 盾形勾（矢量画，不依赖字体） */
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

        Paint s1 = new Paint(Paint.ANTI_ALIAS_FLAG);
        s1.setStyle(Paint.Style.STROKE);
        s1.setStrokeWidth(Math.max(2, w * 0.12f));
        s1.setStrokeJoin(Paint.Join.ROUND);
        s1.setColor(Color.parseColor("#F2F2F2"));
        c.drawPath(path, s1);

        android.graphics.Path tick = new android.graphics.Path();
        tick.moveTo(x + w * 0.30f, y + w * 0.50f);
        tick.lineTo(x + w * 0.45f, y + w * 0.66f);
        tick.lineTo(x + w * 0.72f, y + w * 0.33f);
        s1.setStrokeWidth(Math.max(2, w * 0.13f));
        c.drawPath(tick, s1);
    }

'''
    anchor = '    /** 在给定高度内垂直居中绘制 */'
    assert anchor in s
    s = s.replace(anchor, method + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('shield 已补')
else:
    print('shield 已存在')
