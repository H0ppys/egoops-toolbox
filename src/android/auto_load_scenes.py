"""邀请码改成自动加载分类：输入停顿 0.8 秒自动拉，去掉那个按钮。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 去掉刷新按钮
old_btn = '''        TextView refresh = new TextView(this);
        refresh.setText("按这个邀请码刷新分类 →");
        refresh.setTextSize(14);
        refresh.setTextColor(Color.parseColor("#1B63D6"));
        refresh.setPadding(dp(6), dp(8), dp(6), dp(2));
        refresh.setOnClickListener(v -> {
            String code = etInvite.getText().toString().trim().toUpperCase();
            if (code.isEmpty()) {
                toast("先填邀请码");
                return;
            }
            store.setInvite(code);
            toast("正在按 " + code + " 加载分类…");
            loadScenes(code);
        });
        content.addView(refresh);'''
if old_btn in s:
    s = s.replace(old_btn, '')
    print('刷新按钮已移除')

# 2) 输入自动加载（防抖 800ms）
if 'autoLoadScenes' not in s:
    s = s.replace('''        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));''',
'''        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        // 邀请码一变（停顿 0.8 秒）就自动按这个码拉分类
        etInvite.addTextChangedListener(new android.text.TextWatcher() {
            private final android.os.Handler h = new android.os.Handler(android.os.Looper.getMainLooper());
            private Runnable pending;

            private void schedule() {
                if (pending != null) h.removeCallbacks(pending);
                pending = () -> autoLoadScenes();
                h.postDelayed(pending, 800);
            }

            @Override public void beforeTextChanged(CharSequence s2, int a, int b, int c) { }
            @Override public void onTextChanged(CharSequence s2, int a, int b, int c) { }
            @Override public void afterTextChanged(android.text.Editable e2) { schedule(); }
        });''')

    s = s.replace('''    private void loadScenes() {''', '''    /** 输入框里的邀请码变了：自动按它加载分类（同码不重复加载） */
    private void autoLoadScenes() {
        if (etInvite == null) return;
        String code = etInvite.getText().toString().trim().toUpperCase();
        if (code.length() < 4) return;
        if (code.equals(lastSceneInvite)) return;
        store.setInvite(code);
        loadScenes(code);
    }

    private void loadScenes() {''')

io.open(P, 'w', encoding='utf-8').write(s)
print('邀请码自动加载已加')
