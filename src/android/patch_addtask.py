import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) addTask 改成先填「区域 + 任务」
old_add = s[s.index('    private void addTask() {'):s.index('    private void finishAll()')]
new_add = '''    private void addTask() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(20), dp(8), dp(20), 0);

        TextView l1 = new TextView(this);
        l1.setText("区域名称（比如：客厅 / 后厨 / 3号包间）");
        l1.setTextSize(13);
        l1.setTextColor(MUTED);
        l1.setPadding(0, dp(8), 0, dp(4));
        box.addView(l1);

        final EditText etAreaName = new EditText(this);
        etAreaName.setHint("客厅");
        etAreaName.setTextSize(20);
        box.addView(etAreaName);

        TextView l2 = new TextView(this);
        l2.setText("任务名称（比如：擦拭桌面 / 整理货架）");
        l2.setTextSize(13);
        l2.setTextColor(MUTED);
        l2.setPadding(0, dp(14), 0, dp(4));
        box.addView(l2);

        final EditText etTaskName = new EditText(this);
        etTaskName.setHint("擦拭桌面");
        etTaskName.setTextSize(20);
        box.addView(etTaskName);

        final AlertDialog dlg = new AlertDialog.Builder(this)
                .setTitle("这个区域要拍什么？")
                .setView(box)
                .setCancelable(false)
                .setPositiveButton("开始拍摄", null)
                .setNegativeButton("取消", null)
                .create();
        dlg.show();
        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String a = etAreaName.getText().toString().trim();
            String n = etTaskName.getText().toString().trim();
            if (a.isEmpty()) { toast("请填写区域名称"); etAreaName.requestFocus(); return; }
            if (n.isEmpty()) { toast("请填写任务名称"); etTaskName.requestFocus(); return; }
            Model.Task t = new Model.Task();
            t.type = "area";
            t.area = a;
            t.name = n;
            site.tasks.add(t);
            currentTask = site.tasks.size() - 1;
            currentShot = 0;
            store.saveQueue(site);
            showPage(2);
            renderShot();
            dlg.dismiss();
        });
    }

'''
s = s.replace(old_add, new_add)

# 2) 拍摄标题与完成文案用「区域：任务」
s = s.replace('tvStep.setText(task.name + " · 第 " + (idx + 1) + "/" + shots.length + " 项");',
              'tvStep.setText(labelOf(task) + " · 第 " + (idx + 1) + "/" + shots.length + " 项");')
s = s.replace('tvTaskDoneTitle.setText(task.name + " 拍完了");',
              'tvTaskDoneTitle.setText(labelOf(task) + " 拍完了");')

# 3) 增加 labelOf 辅助方法
s = s.replace('''    private Model.Task task(int i) {
        return site.tasks.get(i);
    }''', '''    private Model.Task task(int i) {
        return site.tasks.get(i);
    }

    private String labelOf(Model.Task t) {
        if (t.area != null && !t.area.isEmpty()) return t.area + "：" + t.name;
        return t.name;
    }''')

io.open(p, 'w', encoding='utf-8').write(s)
print('main patched')
