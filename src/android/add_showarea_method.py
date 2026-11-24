"""补上 showAreaForTask1 方法体（上一步因为字符串已存在被跳过）。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

if 'private void showAreaForTask1()' in s:
    print('方法已存在')
    raise SystemExit(0)

anchor = '    private void askTask(String presetArea) {'
assert anchor in s

block = '''    /** 任务1 的区域填写：写回当前任务，不新建 */
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

'''

s = s.replace(anchor, block + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('showAreaForTask1 已补')
