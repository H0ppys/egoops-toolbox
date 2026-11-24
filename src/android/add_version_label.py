"""1) 首页底部显示当前版本，方便确认装没装上
2) 选「以后再说」记住这个版本，同一版本不再反复弹
"""

import io

# ---------- Store：记录跳过的版本 ----------
p = 'android/src/com/egoops/collect/Store.java'
s = io.open(p, encoding='utf-8').read()
if 'skippedVersion' not in s:
    s = s.replace('''    public String vendor()''', '''    public int skippedVersion() { return sp.getInt("skippedVersion", 0); }
    public void setSkippedVersion(int v) { sp.edit().putInt("skippedVersion", v).apply(); }

    public String vendor()''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Store: 跳过版本')

# ---------- MainActivity ----------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

# 跳过已忽略的版本
if 'skippedVersion()' not in t:
    t = t.replace('''                if (code <= BuildConfigVersion.CODE || url.isEmpty()) return;''',
'''                if (code <= BuildConfigVersion.CODE || url.isEmpty()) return;
                if (code <= store.skippedVersion()) return;      // 用户选过「以后再说」''')

    t = t.replace('''                            .setNegativeButton("以后再说", null)''',
'''                            .setNegativeButton("以后再说", (d, w) -> store.setSkippedVersion(code))''')

# 首页底部显示版本
if '当前版本' not in t:
    t = t.replace('''        TextView settings = new TextView(this);
        settings.setText("设置服务器");''',
'''        TextView version = new TextView(this);
        version.setText("当前版本 " + BuildConfigVersion.NAME + "（" + BuildConfigVersion.CODE + "）");
        version.setTextSize(12);
        version.setTextColor(MUTED);
        version.setGravity(Gravity.CENTER);
        version.setPadding(0, dp(8), 0, 0);
        bottom.addView(version);

        TextView settings = new TextView(this);
        settings.setText("设置服务器");''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('首页显示版本 + 跳过低版本')
