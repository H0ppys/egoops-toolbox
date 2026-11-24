import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) addTask -> askTask(预设区域)
old = s[s.index('    private void addTask() {'):s.index('    private void finishAll()')]
new = '''    private void addTask() {
        String preset = "";
        if (currentTask >= 0 && currentTask < site.tasks.size()) {
            preset = site.tasks.get(currentTask).area;
        }
        askTask(preset);
    }

    /** 填「区域 + 任务」再开拍；presetArea 非空时预填区域，只让填任务 */
    private void askTask(String presetArea) {
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
        etAreaName.setText(presetArea == null ? "" : presetArea);
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
        if (!presetArea.isEmpty()) etTaskName.requestFocus();
    }

'''
s = s.replace(old, new)

# 2) 任务完成页：三个按钮（同区域再拍 / 换区域 / 全部拍完）
s = s.replace('''        Button more = primaryButton("再拍一个区域", 68, PRIMARY);
        more.setOnClickListener(v -> addTask());
        bottom.addView(more);''', '''        Button sameArea = secondaryButton("同一区域，再拍一个任务", 56);
        sameArea.setOnClickListener(v -> {
            String area = currentTask < site.tasks.size() ? site.tasks.get(currentTask).area : "";
            askTask(area);
        });
        bottom.addView(sameArea, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        Button more = primaryButton("换一个区域拍", 68, PRIMARY);
        more.setOnClickListener(v -> askTask(""));
        LinearLayout.LayoutParams mlp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(68));
        mlp.topMargin = dp(10);
        bottom.addView(more, mlp);''')

# 3) 文案
s = s.replace('tvTaskDoneSub.setText("site".equals(task.type) ? "这个采集点还有区域要拍吗？" : "还有别的区域要拍吗？");',
              'tvTaskDoneSub.setText("site".equals(task.type) ? "这个采集点还有区域要拍吗？" : "还有区域或任务要拍吗？");')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
