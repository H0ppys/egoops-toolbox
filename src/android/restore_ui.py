"""重建被误删的 UI 构建方法（buildUi / 四个页面 / 工具方法），并保留新功能：
邀请码输入、厂商提示行、省市区两行布局、拍摄要点、继续上次采集点。
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 插到 loadScenes 之前
anchor = '    private void loadScenes() {'
assert anchor in s, '找不到插入点'

BLOCK = r'''    // ---------------------------------------------------------------- 界面

    private View buildUi() {
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(BG);

        pageStart = buildStartPage();
        pageShoot = buildShootPage();
        pageTaskDone = buildTaskDonePage();
        pageDone = buildDonePage();

        root.addView(pageStart, full());
        root.addView(pageShoot, full());
        root.addView(pageTaskDone, full());
        root.addView(pageDone, full());
        return root;
    }

    private FrameLayout.LayoutParams full() {
        return new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
    }

    private int curPage = 1;

    private void showPage(int n) {
        curPage = n;
        pageStart.setVisibility(n == 1 ? View.VISIBLE : View.GONE);
        pageShoot.setVisibility(n == 2 ? View.VISIBLE : View.GONE);
        pageTaskDone.setVisibility(n == 3 ? View.VISIBLE : View.GONE);
        pageDone.setVisibility(n == 4 ? View.VISIBLE : View.GONE);
    }

    private LinearLayout pageShell() {
        LinearLayout p = new LinearLayout(this);
        p.setOrientation(LinearLayout.VERTICAL);
        p.setBackgroundColor(BG);
        return p;
    }

    private ScrollView scrollWrap(LinearLayout content) {
        ScrollView sc = new ScrollView(this);
        sc.setFillViewport(true);
        sc.addView(content, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return sc;
    }

    private LinearLayout bottomBar() {
        LinearLayout b = new LinearLayout(this);
        b.setOrientation(LinearLayout.VERTICAL);
        b.setBackgroundColor(BG);
        b.setPadding(dp(20), dp(10), dp(20), dp(20));
        return b;
    }

    private Button primaryButton(String text, int heightDp, int color) {
        Button btn = new Button(this);
        btn.setText(text);
        btn.setAllCaps(false);
        btn.setTextSize(23);
        btn.setTypeface(Typeface.DEFAULT_BOLD);
        btn.setTextColor(Color.WHITE);
        btn.setBackground(roundRect(color, 16));
        btn.setMinHeight(0);
        btn.setMinimumHeight(0);
        btn.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(heightDp)));
        return btn;
    }

    private Button secondaryButton(String text, int heightDp) {
        Button btn = new Button(this);
        btn.setText(text);
        btn.setAllCaps(false);
        btn.setTextSize(19);
        btn.setTextColor(PRIMARY);
        btn.setBackground(roundRect(Color.parseColor("#E8EFFC"), 14));
        btn.setMinHeight(0);
        btn.setMinimumHeight(0);
        btn.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(heightDp)));
        return btn;
    }

    // ---------------------------------------------------------------- 第 1 屏

    private LinearLayout buildStartPage() {
        LinearLayout p = pageShell();

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(24), dp(20), dp(24), dp(16));

        TextView title = new TextView(this);
        title.setText("采集点拍照");
        title.setTextSize(30);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setTextColor(TEXT);
        title.setGravity(Gravity.CENTER);
        content.addView(title);

        TextView sub = new TextView(this);
        sub.setText("先拍门头照 + 全景视频\n再逐个区域拍（每个区域 6 项）");
        sub.setTextSize(16);
        sub.setTextColor(MUTED);
        sub.setGravity(Gravity.CENTER);
        sub.setLineSpacing(dp(6), 1f);
        sub.setPadding(0, dp(8), 0, 0);
        content.addView(sub);

        // 邀请码状态行（点一下可改）
        tvVendor = new TextView(this);
        tvVendor.setTextSize(14);
        tvVendor.setTextColor(MUTED);
        tvVendor.setPadding(dp(6), dp(14), dp(6), dp(2));
        tvVendor.setOnClickListener(v -> askInvite());
        content.addView(tvVendor);
        refreshVendorLabel();

        TextView lInv = new TextView(this);
        lInv.setText("邀请码（必填，管理员事先约定，大小写都可以）");
        lInv.setTextSize(15);
        lInv.setTextColor(MUTED);
        lInv.setPadding(dp(4), dp(2), 0, dp(6));
        content.addView(lInv);

        etInvite = new EditText(this);
        etInvite.setText(store.invite());
        etInvite.setHint("例如 ZJMEIYI");
        etInvite.setTextSize(20);
        etInvite.setSingleLine(true);
        etInvite.setInputType(InputType.TYPE_CLASS_TEXT);
        etInvite.setBackground(roundRect(CARD, 12));
        etInvite.setPadding(dp(16), dp(10), dp(16), dp(10));
        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        TextView l1 = new TextView(this);
        l1.setText("采集员姓名（必填）");
        l1.setTextSize(16);
        l1.setTextColor(MUTED);
        l1.setPadding(dp(4), dp(18), 0, dp(8));
        content.addView(l1);

        etCollector = new EditText(this);
        etCollector.setHint("你的名字");
        etCollector.setText(store.name());
        etCollector.setTextSize(21);
        etCollector.setTextColor(TEXT);
        etCollector.setHintTextColor(Color.parseColor("#A8B4C6"));
        etCollector.setBackground(roundRect(CARD, 12));
        etCollector.setPadding(dp(16), dp(12), dp(16), dp(12));
        content.addView(etCollector, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(60)));

        TextView l2 = new TextView(this);
        l2.setText("门店名称（必填）");
        l2.setTextSize(16);
        l2.setTextColor(MUTED);
        l2.setPadding(dp(4), dp(18), 0, dp(8));
        content.addView(l2);

        etStoreName = new EditText(this);
        etStoreName.setHint("例如：XX 超市");
        etStoreName.setTextSize(21);
        etStoreName.setTextColor(TEXT);
        etStoreName.setHintTextColor(Color.parseColor("#A8B4C6"));
        etStoreName.setBackground(roundRect(CARD, 12));
        etStoreName.setPadding(dp(16), dp(12), dp(16), dp(12));
        etStoreName.setText(site.name);
        content.addView(etStoreName, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(60)));

        // 现场地址：省 + 市 一行，区 + 街道 一行
        TextView lAddr = new TextView(this);
        lAddr.setText("现场地址（必填：先选省市区，再填街道门牌号）");
        lAddr.setTextSize(16);
        lAddr.setTextColor(MUTED);
        lAddr.setPadding(dp(4), dp(18), 0, dp(8));
        content.addView(lAddr);

        LinearLayout addrRow1 = new LinearLayout(this);
        addrRow1.setOrientation(LinearLayout.HORIZONTAL);
        content.addView(addrRow1, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        spProv = new android.widget.Spinner(this);
        spProv.setBackground(roundRect(CARD, 12));
        spProv.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"省份"}));
        addrRow1.addView(spProv, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f));

        spCity = new android.widget.Spinner(this);
        spCity.setBackground(roundRect(CARD, 12));
        spCity.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"城市"}));
        LinearLayout.LayoutParams clp2 = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f);
        clp2.leftMargin = dp(8);
        addrRow1.addView(spCity, clp2);

        LinearLayout addrRow2 = new LinearLayout(this);
        addrRow2.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams r2lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
        r2lp.topMargin = dp(8);
        content.addView(addrRow2, r2lp);

        spDist = new android.widget.Spinner(this);
        spDist.setBackground(roundRect(CARD, 12));
        spDist.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"区 / 县"}));
        addrRow2.addView(spDist, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 0.62f));

        etStreet = new EditText(this);
        etStreet.setHint("街道、门牌号");
        etStreet.setTextSize(18);
        etStreet.setTextColor(TEXT);
        etStreet.setHintTextColor(Color.parseColor("#A8B4C6"));
        etStreet.setBackground(roundRect(CARD, 12));
        etStreet.setPadding(dp(14), dp(10), dp(14), dp(10));
        LinearLayout.LayoutParams slp2 = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1.38f);
        slp2.leftMargin = dp(8);
        addrRow2.addView(etStreet, slp2);

        spProv.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                updateCities(pos);
            }
            @Override public void onNothingSelected(android.widget.AdapterView<?> p) { }
        });
        spCity.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                updateDistricts(pos);
            }
            @Override public void onNothingSelected(android.widget.AdapterView<?> p) { }
        });

        TextView l3 = new TextView(this);
        l3.setText("采集场景分类（必选）");
        l3.setTextSize(16);
        l3.setTextColor(MUTED);
        l3.setPadding(dp(4), dp(18), 0, dp(8));
        content.addView(l3);

        spCat = new android.widget.Spinner(this);
        spCat.setBackground(roundRect(CARD, 12));
        List<String> catLabels = new ArrayList<String>();
        catLabels.add("全部分类");
        spCat.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, catLabels));
        content.addView(spCat, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        spScene2 = new android.widget.Spinner(this);
        spScene2.setBackground(roundRect(CARD, 12));
        List<String> sceneHint = new ArrayList<String>();
        sceneHint.add("请选择具体场景");
        spScene2.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, sceneHint));
        LinearLayout.LayoutParams s2lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
        s2lp.topMargin = dp(8);
        content.addView(spScene2, s2lp);

        TextView l4 = new TextView(this);
        l4.setText("场地面积 ㎡（必填）");
        l4.setTextSize(16);
        l4.setTextColor(MUTED);
        l4.setPadding(dp(4), dp(18), 0, dp(8));
        content.addView(l4);

        etArea = new EditText(this);
        etArea.setHint("例如：85");
        etArea.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        etArea.setTextSize(21);
        etArea.setTextColor(TEXT);
        etArea.setHintTextColor(Color.parseColor("#A8B4C6"));
        etArea.setBackground(roundRect(CARD, 12));
        etArea.setPadding(dp(16), dp(12), dp(16), dp(12));
        if (site.area > 0) etArea.setText(String.valueOf((int) site.area));
        content.addView(etArea, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(60)));

        p.addView(scrollWrap(content), new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout bottom = bottomBar();

        Button resume = secondaryButton("继续上次的采集点（补拍/续传）", 52);
        resume.setOnClickListener(v -> resumeLastSite());
        bottom.addView(resume);

        Button start = primaryButton("开始拍摄", 72, PRIMARY);
        start.setOnClickListener(v -> beginShooting());
        LinearLayout.LayoutParams slp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(72));
        slp.topMargin = dp(10);
        bottom.addView(start, slp);

        TextView settings = new TextView(this);
        settings.setText("设置服务器");
        settings.setTextSize(13);
        settings.setTextColor(MUTED);
        settings.setGravity(Gravity.CENTER);
        settings.setPadding(0, dp(10), 0, 0);
        settings.setOnClickListener(v -> showSettings());
        bottom.addView(settings);

        p.addView(bottom);
        return p;
    }

    // ---------------------------------------------------------------- 第 2 屏

    private LinearLayout buildShootPage() {
        LinearLayout p = pageShell();

        LinearLayout head = new LinearLayout(this);
        head.setOrientation(LinearLayout.HORIZONTAL);
        head.setGravity(Gravity.CENTER_VERTICAL);
        head.setPadding(dp(20), dp(16), dp(20), dp(2));
        p.addView(head);

        tvStep = new TextView(this);
        tvStep.setTextSize(21);
        tvStep.setTypeface(Typeface.DEFAULT_BOLD);
        tvStep.setTextColor(TEXT);
        head.addView(tvStep, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        TextView back = new TextView(this);
        back.setText("重新开始");
        back.setTextSize(13);
        back.setTextColor(MUTED);
        back.setPadding(dp(8), dp(8), dp(8), dp(8));
        back.setOnClickListener(v -> confirmRestart());
        head.addView(back);

        tvDots = new TextView(this);
        tvDots.setTextSize(18);
        tvDots.setTextColor(PRIMARY);
        tvDots.setGravity(Gravity.CENTER);
        tvDots.setPadding(0, dp(2), 0, dp(6));
        p.addView(tvDots);

        LinearLayout area = new LinearLayout(this);
        area.setOrientation(LinearLayout.VERTICAL);
        area.setPadding(dp(20), 0, dp(20), dp(8));
        shotArea = area;
        p.addView(scrollWrap(area), new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout bottom = bottomBar();
        tvUpload = new TextView(this);
        tvUpload.setTextSize(13);
        tvUpload.setTextColor(MUTED);
        tvUpload.setGravity(Gravity.CENTER);
        tvUpload.setPadding(0, 0, 0, dp(8));
        tvUpload.setOnClickListener(v -> startUpload());
        bottom.addView(tvUpload);
        p.addView(bottom);

        return p;
    }

    // ---------------------------------------------------------------- 任务完成屏

    private LinearLayout buildTaskDonePage() {
        LinearLayout p = pageShell();

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(24), dp(48), dp(24), dp(16));

        TextView tick = new TextView(this);
        tick.setText("✓");
        tick.setTextSize(76);
        tick.setTextColor(OK);
        tick.setGravity(Gravity.CENTER);
        content.addView(tick);

        tvTaskDoneTitle = new TextView(this);
        tvTaskDoneTitle.setText("任务拍完了");
        tvTaskDoneTitle.setTextSize(28);
        tvTaskDoneTitle.setTypeface(Typeface.DEFAULT_BOLD);
        tvTaskDoneTitle.setTextColor(TEXT);
        tvTaskDoneTitle.setGravity(Gravity.CENTER);
        tvTaskDoneTitle.setPadding(0, dp(6), 0, dp(8));
        content.addView(tvTaskDoneTitle);

        tvTaskDoneSub = new TextView(this);
        tvTaskDoneSub.setText("这家店还有别的任务要拍吗？");
        tvTaskDoneSub.setTextSize(17);
        tvTaskDoneSub.setTextColor(MUTED);
        tvTaskDoneSub.setGravity(Gravity.CENTER);
        content.addView(tvTaskDoneSub);

        p.addView(scrollWrap(content), new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout bottom = bottomBar();
        Button sameArea = secondaryButton("同一区域，再拍一个任务", 56);
        sameArea.setOnClickListener(v -> {
            String area = currentTask < site.tasks.size() ? site.tasks.get(currentTask).area : "";
            askTask(area);
        });
        bottom.addView(sameArea);

        Button more = primaryButton("换一个区域拍", 68, PRIMARY);
        more.setOnClickListener(v -> askTask(""));
        LinearLayout.LayoutParams mlp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(68));
        mlp.topMargin = dp(10);
        bottom.addView(more, mlp);

        Button finish = secondaryButton("没有了，全部拍完", 56);
        finish.setOnClickListener(v -> finishAll());
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
        lp.topMargin = dp(10);
        bottom.addView(finish, lp);

        p.addView(bottom);
        return p;
    }

    // ---------------------------------------------------------------- 结束屏

    private LinearLayout buildDonePage() {
        LinearLayout p = pageShell();

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(24), dp(48), dp(24), dp(16));

        TextView tick = new TextView(this);
        tick.setText("✓");
        tick.setTextSize(80);
        tick.setTextColor(OK);
        tick.setGravity(Gravity.CENTER);
        content.addView(tick);

        TextView title = new TextView(this);
        title.setText("拍摄完成");
        title.setTextSize(30);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setTextColor(TEXT);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, dp(8), 0, dp(10));
        content.addView(title);

        tvDoneStatus = new TextView(this);
        tvDoneStatus.setText("正在自动上传，请稍等…");
        tvDoneStatus.setTextSize(17);
        tvDoneStatus.setTextColor(MUTED);
        tvDoneStatus.setGravity(Gravity.CENTER);
        content.addView(tvDoneStatus);

        p.addView(scrollWrap(content), new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout bottom = bottomBar();
        Button again = primaryButton("再拍一个采集点", 68, PRIMARY);
        again.setOnClickListener(v -> resetForNext());
        bottom.addView(again);
        p.addView(bottom);

        return p;
    }

    // ---------------------------------------------------------------- 场景二级联动

    private void refreshSceneSpinner() {
        int catPos = spCat == null ? 0 : spCat.getSelectedItemPosition();
        shownIndex.clear();
        List<String> labels = new ArrayList<String>();
        if (catPos <= 0) {
            for (int i = 0; i < sceneItems.size(); i++) {
                labels.add(sceneItems.get(i)[1]);
                shownIndex.add(i);
            }
        } else {
            String cat = categories.get(catPos - 1);
            for (int i = 0; i < sceneItems.size(); i++) {
                if (cat.equals(sceneItems.get(i)[2])) {
                    labels.add(sceneItems.get(i)[1]);
                    shownIndex.add(i);
                }
            }
        }
        if (labels.isEmpty()) labels.add("请选择具体场景");
        if (spScene2 != null) {
            spScene2.setAdapter(new android.widget.ArrayAdapter<String>(this,
                    android.R.layout.simple_spinner_dropdown_item, labels));
        }
    }

'''

s = s.replace(anchor, BLOCK + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('UI 方法已重建，当前行数:', len(s.splitlines()))
