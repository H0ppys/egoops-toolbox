"""任务1 合成 9 项：门头照/全景照片/全景视频 + 该区域对角2/任务照2/任务视频2。

实现要点：
  · 新增任务类型 task1，shots 共 9 项
  · 拍到第 3 项（三项全景）拍完时，自动弹「填区域和动作」，写回同一个任务
  · 第 4~9 项照常拍；换区域时新建的是普通 area 任务（6 项）
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 新增 9 项定义
if 'SHOTS_TASK1' not in s:
    anchor = '''    /** 后续区域：2 张对角照 + 2 张任务照 + 2 个任务视频（门头/全景只在任务1 拍） */'''
    block = '''    /** 任务1：门头 3 项 + 第一个区域 6 项，合起来 9 项 */
    private static final String[][] SHOTS_TASK1 = {
            {"door", "门头照", "正对门头，把招牌和门都拍进去（用广角）", "photo"},
            {"panophoto", "全景照片", "站在店中央，用广角把整个空间拍全", "photo"},
            {"panovideo", "全景视频", "原地慢慢转一圈，用广角（15 秒左右）", "video"},
            {"corner1", "对角照片 1", "站在区域一个角，用广角斜着拍对角", "photo"},
            {"corner2", "对角照片 2", "走到对角，反方向再拍一张", "photo"},
            {"work1", "任务照片 1", "拍这个区域要采集的内容", "photo"},
            {"work2", "任务照片 2", "换个角度再拍一张", "photo"},
            {"clip1", "任务视频 1", "对准要采集的动作，用广角录 10 秒", "video"},
            {"clip2", "任务视频 2", "换个角度再录 10 秒", "video"},
    };

'''
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)

# 2) shotsOf 支持 task1（老数据 site 仍按 3 项）
s = s.replace('''    private static String[][] shotsOf(Model.Task t) {
        return (t != null && "site".equals(t.type)) ? SHOTS_SITE : SHOTS_AREA;
    }''',
'''    private static String[][] shotsOf(Model.Task t) {
        if (t == null) return SHOTS_AREA;
        if ("task1".equals(t.type)) return SHOTS_TASK1;
        if ("site".equals(t.type)) return SHOTS_SITE;
        return SHOTS_AREA;
    }''')

# 3) beginShooting：新采集点用 task1
s = s.replace('''            Model.Task t = new Model.Task();
            t.type = "site";
            t.name = "任务1·门头与全景";
            site.tasks.add(t);''',
'''            Model.Task t = new Model.Task();
            t.type = "task1";
            t.name = "任务1";
            site.tasks.add(t);''')

# 4) renderShot：任务1 的第 4 项起，如果还没填区域，先要求填
s = s.replace('''        int idx = currentShot;
        String key = shots[idx][0];''',
'''        if ("task1".equals(task.type) && currentShot >= 3
                && (task.area == null || task.area.isEmpty())) {
            showAreaForTask1();
            return;
        }

        int idx = currentShot;
        String key = shots[idx][0];''')

# 5) acceptCapture：三项全景拍完 -> 立刻问区域
s = s.replace('''            if ("site".equals(task.type)) {''', '''            if ("task1".equals(task.type) && (task.area == null || task.area.isEmpty())
                    && doneCount(currentTask) >= 3) {
                toast("门头/全景拍完了，接着填区域和动作");
                showAreaForTask1();
            } else if ("site".equals(task.type)) {''')

# 6) 区域对话框：任务1 复用同一个任务
if 'showAreaForTask1' not in s:
    s = s.replace('''    private void askTask(String presetArea) {''',
'''    /** 任务1 的区域填写：写回当前任务，不新建 */
    private void showAreaForTask1() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(20), dp(8), dp(20), 0);

        TextView tip = new TextView(this);
        tip.setText("门头照 + 全景照片 + 全景视频 已拍好。\\n现在填这次要拍的第一个区域：");
        tip.setTextSize(14);
        tip.setTextColor(MUTED);
        tip.setPadding(0, 0, 0, dp(8));
        box.addView(tip);

        TextView l1 = new TextView(this);
        l1.setText("1. 这是哪个区域？（比如：饮料区 / 后厨）");
        l1.setTextSize(13);
        l1.setTextColor(MUTED);
        box.addView(l1);

        final EditText etAreaName = new EditText(this);
        etAreaName.setHint("饮料区");
        etAreaName.setTextSize(20);
        box.addView(etAreaName);

        TextView l2 = new TextView(this);
        l2.setText("2. 在这个区域要做什么动作？（比如：捡垃圾 / 擦拭桌面）");
        l2.setTextSize(13);
        l2.setTextColor(MUTED);
        l2.setPadding(0, dp(12), 0, 4);
        box.addView(l2);

        final EditText etTaskName = new EditText(this);
        etTaskName.setHint("捡垃圾");
        etTaskName.setTextSize(20);
        box.addView(etTaskName);

        final AlertDialog dlg = new AlertDialog.Builder(this)
                .setTitle("填写区域和动作")
                .setView(box)
                .setCancelable(false)
                .setPositiveButton("开始拍摄这个区域", null)
                .create();
        dlg.show();
        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String a = etAreaName.getText().toString().trim();
            String n = etTaskName.getText().toString().trim();
            if (a.isEmpty()) { toast("请填写区域名称"); etAreaName.requestFocus(); return; }
            if (n.isEmpty()) { toast("请填写动作名称"); etTaskName.requestFocus(); return; }
            Model.Task t = site.tasks.get(0);
            t.area = a;
            t.name = n + " · 门头与全景";
            store.saveQueue(site);
            currentTask = 0;
            currentShot = firstUndone(0);
            if (currentShot < 0) currentShot = 3;
            dlg.dismiss();
            renderShot();
        });
    }

    private void askTask(String presetArea) {''')

# 7) 进度条文案：任务1 显示 9 项
s = s.replace('''        String prefix = (currentTask == 0 && "area".equals(task.type)) ? "任务1（含门头/全景）· " : "";''',
'''        String prefix = "area".equals(task.type) ? "" : "";''')

io.open(P, 'w', encoding='utf-8').write(s)
print('任务1 合成 9 项')
