import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 网络拉不到场景时，用 APK 内置的 scenes.json 兜底
old = '''    private void loadScenes() {
        new Thread(() -> {
            try {
                org.json.JSONObject r = api.request("GET", "/api/scenes", null);
                org.json.JSONArray items = r.optJSONArray("items");'''
new = '''    private void loadScenes() {
        new Thread(() -> {
            try {
                org.json.JSONArray items = null;
                String failReason = "";
                try {
                    org.json.JSONObject r = api.request("GET", "/api/scenes", null);
                    items = r.optJSONArray("items");
                } catch (Exception e) {
                    failReason = e.getMessage() == null ? e.toString() : e.getMessage();
                }
                if (items == null || items.length() == 0) {
                    // 网络不可用：用安装包里自带的分类表，保证一定能选
                    try {
                        java.io.InputStream in = getResources().openRawResource(R.raw.scenes);
                        java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
                        byte[] buf = new byte[8192];
                        int n;
                        while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
                        in.close();
                        items = new org.json.JSONObject(bos.toString("UTF-8")).optJSONArray("items");
                        if (items != null) toast("场景分类用本地缓存（没连上服务器）");
                    } catch (Exception e2) {
                        final String msg = failReason.isEmpty() ? "读取失败" : failReason;
                        runOnUiThread(() -> toast("场景分类加载失败：" + msg));
                    }
                }'''
assert old in s
s = s.replace(old, new)

# 2) 地址：省/市一行，区/街道一行，避免下拉框把"广东省"挤成"广.."
old2 = '''        LinearLayout addrRow = new LinearLayout(this);
        addrRow.setOrientation(LinearLayout.HORIZONTAL);
        content.addView(addrRow, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));'''
new2 = '''        LinearLayout addrRow = new LinearLayout(this);
        addrRow.setOrientation(LinearLayout.HORIZONTAL);
        content.addView(addrRow, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));'''
# 保持不变，改为把区放到第二行（与街道同排）

s = s.replace('''        spDist = new android.widget.Spinner(this);
        spDist.setBackground(roundRect(CARD, 12));
        spDist.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"区 / 县"}));
        LinearLayout.LayoutParams dlp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f);
        dlp.leftMargin = dp(8);
        addrRow.addView(spDist, dlp);''',
'''        spDist = new android.widget.Spinner(this);
        spDist.setBackground(roundRect(CARD, 12));
        spDist.setAdapter(new android.widget.ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_dropdown_item, new String[]{"区 / 县"}));''')

s = s.replace('''        etStreet = new EditText(this);
        etStreet.setHint("街道、门牌号、园区或楼栋");''',
'''        LinearLayout addrRow2 = new LinearLayout(this);
        addrRow2.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams r2lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(54));
        r2lp.topMargin = dp(8);
        content.addView(addrRow2, r2lp);

        LinearLayout.LayoutParams dlp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 0.62f);
        addrRow2.addView(spDist, dlp);

        etStreet = new EditText(this);
        etStreet.setHint("街道、门牌号");''')

s = s.replace('''        LinearLayout.LayoutParams slp2 = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(58));
        slp2.topMargin = dp(8);
        content.addView(etStreet, slp2);''',
'''        LinearLayout.LayoutParams slp2 = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1.38f);
        slp2.leftMargin = dp(8);
        addrRow2.addView(etStreet, slp2);''')

# 省/市各占一半，文字不再被截
s = s.replace('''        addrRow.addView(spProv, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f));''',
'''        addrRow.addView(spProv, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 1f));''')

io.open(p, 'w', encoding='utf-8').write(s)
print('场景兜底 + 地址两行布局')
