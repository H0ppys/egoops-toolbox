"""按「每张照片精确对应到项」改：
   1) 去掉批量导入按钮（按顺序塞容易错位）
   2) 拍好的项显示缩略图 + 文件名，肉眼可核对是哪张
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# ---------- 1) 去掉批量选按钮 ----------
old_btn = '''        if (BuildConfigVersion.NO_CAPTURE) {
            Button multi = secondaryButton("批量选剩下的项（一次选多张）", 56);
            multi.setOnClickListener(v -> pickMultiple());
            LinearLayout.LayoutParams mlp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
            mlp.topMargin = dp(8);
            card.addView(multi, mlp);
        }

'''
if old_btn in s:
    s = s.replace(old_btn, '')
    print('批量按钮已移除')

# ---------- 2) 拍好的项显示缩略图 + 文件名 ----------
old_done = '''        TextView num = new TextView(this);
        num.setText(done ? "这一项已经拍好了" : "现在拍这一项");'''
new_done = '''        if (done) {
            Model.Media mine = null;
            for (Model.Media mm : task.media) {
                if (key.equals(mm.shot)) mine = mm;
            }
            if (mine != null) {
                try {
                    java.io.File f = new java.io.File(mine.path);
                    if (f.exists() && "photo".equals(mine.kind)) {
                        android.graphics.BitmapFactory.Options o = new android.graphics.BitmapFactory.Options();
                        o.inJustDecodeBounds = true;
                        android.graphics.BitmapFactory.decodeFile(f.getAbsolutePath(), o);
                        int sample = 1;
                        while (Math.max(o.outWidth, o.outHeight) / sample > 900) sample *= 2;
                        o.inJustDecodeBounds = false;
                        o.inSampleSize = sample;
                        android.graphics.Bitmap bm = android.graphics.BitmapFactory.decodeFile(f.getAbsolutePath(), o);
                        if (bm != null) {
                            android.widget.ImageView iv = new android.widget.ImageView(this);
                            iv.setImageBitmap(bm);
                            iv.setScaleType(android.widget.ImageView.ScaleType.CENTER_CROP);
                            LinearLayout.LayoutParams ilp = new LinearLayout.LayoutParams(
                                    ViewGroup.LayoutParams.MATCH_PARENT, dp(220));
                            ilp.topMargin = dp(10);
                            card.addView(iv, ilp);
                        }
                    }
                } catch (Throwable ignored) {
                }

                TextView fn = new TextView(this);
                fn.setText("已用：" + new java.io.File(mine.path).getName());
                fn.setTextSize(13);
                fn.setTextColor(MUTED);
                fn.setGravity(Gravity.CENTER);
                fn.setPadding(0, dp(6), 0, 0);
                card.addView(fn);
            }
        }

        TextView num = new TextView(this);
        num.setText(done ? "这一项已经拍好了" : "现在拍这一项");'''
assert old_done in s
s = s.replace(old_done, new_done)

io.open(P, 'w', encoding='utf-8').write(s)
print('已加：拍好项显示缩略图与文件名')
