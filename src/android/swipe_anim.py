"""三个改动：
   1) 切换项时卡片滑入动画（左/右方向区分）
   2) 进度点区分「当前位置」和「已完成」，标题带上项名
   3) 全景照片只保留「从相册选」，不显示水印相机按钮
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# ---------- 1) 全景照片只给相册入口 ----------
old_wm = '''        if (BuildConfigVersion.NO_CAPTURE) {
            Button openWm = secondaryButton("① 打开水印相机去拍", 60);'''
new_wm = '''        boolean galleryOnly = "panophoto".equals(key);
        if (BuildConfigVersion.NO_CAPTURE && !galleryOnly) {
            Button openWm = secondaryButton("① 打开水印相机去拍", 60);'''
assert old_wm in s
s = s.replace(old_wm, new_wm)

# 全景照片加一句说明
old_hint = '''        TextView next = new TextView(this);
        next.setText(done ? "拍完会自动跳到下一项" : "拍好之后会自动跳到下一项");'''
new_hint = '''        TextView next = new TextView(this);
        next.setText(galleryOnly ? "全景照片请用手机全景模式拍，再从相册选"
                : (done ? "拍完会自动跳到下一项" : "拍好之后会自动跳到下一项"));'''
assert old_hint in s
s = s.replace(old_hint, new_hint)

# ---------- 2) 标题带项名 + 进度点区分当前位置 ----------
old_dots = '''        StringBuilder dots = new StringBuilder();
        for (int i = 0; i < shots.length; i++) {
            if (i > 0) dots.append("   ");
            dots.append(hasShot(currentTask, i) ? "●" : "○");
        }
        tvDots.setText(dots.toString());'''
new_dots = '''        StringBuilder dots = new StringBuilder();
        for (int i = 0; i < shots.length; i++) {
            if (i > 0) dots.append("   ");
            if (i == currentShot) dots.append("◆");            // 当前位置
            else if (hasShot(currentTask, i)) dots.append("●"); // 已完成
            else dots.append("○");                              // 未拍
        }
        tvDots.setText(dots.toString());'''
assert old_dots in s
s = s.replace(old_dots, new_dots)

s = s.replace('''        tvStep.setText(prefix + labelOf(task) + " · 第 " + (idx + 1) + "/" + shots.length + " 项");''',
'''        tvStep.setText(prefix + labelOf(task) + " · 第 " + (idx + 1) + "/" + shots.length + " 项 · " + title);''')

# ---------- 3) 滑入动画 ----------
# 记录切换方向
if 'slideDir' not in s:
    s = s.replace('    private boolean awaitingWatermarkImport = false;',
                  '    private boolean awaitingWatermarkImport = false;\n    private int slideDir = 1;   // 1=下一项 -1=上一项')

    s = s.replace('''        currentShot = target;
        renderShot();
        toast(delta < 0 ? "上一项" : "下一项");''',
'''        currentShot = target;
        slideDir = delta;
        renderShot();
        toast(delta < 0 ? "上一项" : "下一项");''')

    # 卡片入场上动画：在 shotArea.addView(card, ...) 之后
    old_add = '''        shotArea.addView(card, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));'''
    new_add = '''        shotArea.addView(card, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        try {
            int w = getResources().getDisplayMetrics().widthPixels;
            card.setTranslationX(slideDir > 0 ? w * 0.35f : -w * 0.35f);
            card.setAlpha(0.25f);
            card.animate().translationX(0f).alpha(1f).setDuration(200).start();
        } catch (Throwable ignored) {
        }'''
    assert old_add in s
    s = s.replace(old_add, new_add)

io.open(P, 'w', encoding='utf-8').write(s)
print('动画 + 位置提示 + 全景照片仅相册 已改')
