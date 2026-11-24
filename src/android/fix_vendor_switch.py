"""1) 服务器：厂商自己的表也要按 vendor_scenes.json 里的大类过滤
2) App：换了邀请码立刻能刷新分类（按钮 + 开始拍摄时自动检测）
"""

import io

# ---------- 服务器 ----------
p = 'relay/server.mjs'
s = io.open(p, encoding='utf-8').read()

old = """        if (fs.existsSync(own)) {
          try {
            const data = JSON.parse(fs.readFileSync(own, 'utf8'));
            const domains = [];
            for (const it of data.items || []) if (!domains.includes(it.category)) domains.push(it.category);
            return send(res, 200, { ...data, vendor: code, domains, own: true });"""

new = """        if (fs.existsSync(own)) {
          try {
            const data = JSON.parse(fs.readFileSync(own, 'utf8'));
            const allowOwn = (vendorScenes()[code] || []).map((x) => String(x));
            let itemsOwn = data.items || [];
            if (allowOwn.length > 0) {
              itemsOwn = itemsOwn.filter((it) => allowOwn.includes(it.category));
            }
            const domains = [];
            for (const it of itemsOwn) if (!domains.includes(it.category)) domains.push(it.category);
            return send(res, 200, { ...data, count: itemsOwn.length, items: itemsOwn, vendor: code, domains, own: true });"""
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('server: 自有表也按配置过滤')

# ---------- App ----------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

# 记录上次加载分类用的邀请码
if 'lastSceneInvite' not in t:
    t = t.replace('    private EditText etInvite;',
                  '    private EditText etInvite;\n    private String lastSceneInvite = "";')
    t = t.replace('''            final String tip = note;''', '''            final String tip = note;
            lastSceneInvite = code;''')

# 邀请码下面加「按这个码刷新分类」按钮
if '按这个码刷新分类' not in t:
    t = t.replace('''        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));''',
'''        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        TextView refresh = new TextView(this);
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
        content.addView(refresh);''')

# 开始拍摄时：邀请码变了就先刷新，提示再点一次
if '邀请码变了' not in t:
    t = t.replace('''        if (sceneItems.isEmpty()) {
            toast("场景分类还没准备好，请稍等");
            loadScenes();
            return;
        }''', '''        if (!invite.equals(lastSceneInvite)) {
            toast("邀请码变了，正在加载该厂商的分类，稍等再点「开始拍摄」");
            loadScenes(invite);
            return;
        }
        if (sceneItems.isEmpty()) {
            toast("场景分类还没准备好，请稍等");
            loadScenes(invite);
            return;
        }''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('App: 换码刷新分类')
