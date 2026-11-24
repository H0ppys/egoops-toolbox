"""拍摄页支持左右滑动切换项：
   · 右滑 → 上一项，左滑 → 下一项
   · 同时在标题右侧加「← 上一项」文字按钮（中年人不一定会滑，给个可见入口）
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 头部加「上一项」按钮
old_head = '''        TextView back = new TextView(this);
        back.setText("重新开始");'''
new_head = '''        TextView prev = new TextView(this);
        prev.setText("← 上一项");
        prev.setTextSize(14);
        prev.setTextColor(Color.parseColor("#1B63D6"));
        prev.setPadding(dp(8), dp(8), dp(10), dp(8));
        prev.setOnClickListener(v -> stepShot(-1));
        head.addView(prev);

        TextView back = new TextView(this);
        back.setText("重新开始");'''
assert old_head in s
s = s.replace(old_head, new_head)

# 2) 手势：挂在滚动容器上
old_wrap = '''        p.addView(scrollWrap(area), new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));'''
new_wrap = '''        android.widget.ScrollView sv = scrollWrap(area);
        final android.view.GestureDetector gd = new android.view.GestureDetector(this,
                new android.view.GestureDetector.SimpleOnGestureListener() {
                    @Override
                    public boolean onFling(android.view.MotionEvent e1, android.view.MotionEvent e2,
                                           float vx, float vy) {
                        if (e1 == null || e2 == null) return false;
                        float dx = e2.getX() - e1.getX();
                        float dy = e2.getY() - e1.getY();
                        if (Math.abs(dx) < dp(60) || Math.abs(dx) < Math.abs(dy) * 1.5f) return false;
                        stepShot(dx > 0 ? -1 : 1);
                        return true;
                    }
                });
        sv.setOnTouchListener((v, ev) -> {
            gd.onTouchEvent(ev);
            return false;
        });
        p.addView(sv, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));'''
assert old_wrap in s
s = s.replace(old_wrap, new_wrap)

# 3) stepShot 实现
if 'private void stepShot' not in s:
    anchor = '    private void renderShot() {'
    block = '''    /** 左右滑动切换拍摄项：delta = -1 上一项，+1 下一项 */
    private void stepShot(int delta) {
        if (site == null || site.tasks.isEmpty()) return;
        Model.Task task = task(currentTask);
        String[][] shots = shotsOf(task);
        int target = currentShot + delta;

        // 越界就跨任务
        if (target < 0) {
            if (currentTask > 0) {
                currentTask--;
                currentShot = shotsOf(task(currentTask)).length - 1;
                currentShot = firstUndoneOrLast(currentTask);
                renderShot();
                toast("回到上一项");
            } else {
                toast("已经是第一项了");
            }
            return;
        }
        if (target >= shots.length) {
            if (currentTask + 1 < site.tasks.size()) {
                currentTask++;
                currentShot = 0;
                renderShot();
                toast("下一项");
            } else {
                toast("已经是最后一项了");
            }
            return;
        }

        currentShot = target;
        renderShot();
        toast(delta < 0 ? "上一项" : "下一项");
    }

    /** 取该任务最后一拍的项（用于往回切） */
    private int firstUndoneOrLast(int taskIndex) {
        int last = shotsOf(task(taskIndex)).length - 1;
        for (int i = 0; i <= last; i++) if (hasShot(taskIndex, i)) last = Math.max(last, last);
        return Math.max(0, last);
    }

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('左右滑动 + 上一项按钮 已加')
