import io

# ---------------- Store：记住厂商 ----------------
p = 'android/src/com/egoops/collect/Store.java'
s = io.open(p, encoding='utf-8').read()
if 'setVendor' not in s:
    s = s.replace('''    public String invite() { return sp.getString("invite", ""); }
    public void setInvite(String v) { sp.edit().putString("invite", v).apply(); }''',
'''    public String invite() { return sp.getString("invite", ""); }
    public void setInvite(String v) { sp.edit().putString("invite", v).apply(); }

    public String vendor() { return sp.getString("vendor", ""); }
    public void setVendor(String v) { sp.edit().putString("vendor", v).apply(); }''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Store 加了 vendor')

# ---------------- MainActivity ----------------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

# 1) 登录后记住厂商
t = t.replace('''        api.token = r.optString("token");
        store.setToken(api.token);
        store.setName(name);''', '''        api.token = r.optString("token");
        store.setToken(api.token);
        store.setName(name);
        String vendor = r.optString("vendor", "");
        if (vendor != null && !vendor.isEmpty()) {
            store.setVendor(vendor);
            final String vname = vendor;
            runOnUiThread(() -> toast("厂商：" + vname));
        }
        runOnUiThread(this::refreshVendorLabel);''')

# 2) 邀请码弹窗：先校验，再保存
old_ask = '''    /** 没有邀请码 / 邀请码不对：让采集员填，填完自动重试 */
    private void askInvite() {
        final EditText et = new EditText(this);
        et.setText(store.invite());
        et.setHint("管理员给的 8 位字母数字");
        et.setTextSize(20);
        new AlertDialog.Builder(this)
                .setTitle("需要邀请码")
                .setMessage("第一次用这台手机，要填一次邀请码。\\n请向管理员要（他可以在电脑端「采集数据查看器」里生成）。")
                .setView(et)
                .setCancelable(false)
                .setPositiveButton("确定", (d, w) -> {
                    store.setInvite(et.getText().toString().trim());
                    api.token = "";
                    startUpload();
                })
                .setNegativeButton("取消", null)
                .show();
    }'''
new_ask = '''    /** 邀请码：填对之后就知道拍的是哪个厂商的店 */
    private void askInvite() {
        final EditText et = new EditText(this);
        et.setText(store.invite());
        et.setHint("管理员给的邀请码，例如 ZJMEIYI");
        et.setTextSize(20);
        et.setSingleLine(true);
        new AlertDialog.Builder(this)
                .setTitle("填写邀请码")
                .setMessage("邀请码决定这批照片属于哪个厂商。\\n填对后会在拍摄页显示厂商名称。")
                .setView(et)
                .setCancelable(false)
                .setPositiveButton("确定", (d, w) -> {
                    final String code = et.getText().toString().trim().toUpperCase();
                    if (code.isEmpty()) {
                        toast("请填邀请码");
                        return;
                    }
                    checkInviteThen(code);
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /** 调服务器确认邀请码，拿到厂商名 */
    private void checkInviteThen(final String code) {
        new Thread(() -> {
            try {
                org.json.JSONObject r = api.request("GET", "/api/invite/check?code=" + android.net.Uri.encode(code), null);
                if (!r.optBoolean("ok", false)) {
                    runOnUiThread(() -> {
                        toast("邀请码不存在，请核对后重填");
                        askInvite();
                    });
                    return;
                }
                final String vendor = r.optString("vendor", "");
                store.setInvite(code);
                store.setVendor(vendor);
                api.token = "";
                store.setToken("");
                runOnUiThread(() -> {
                    toast("厂商：" + vendor);
                    refreshVendorLabel();
                    startUpload();
                });
            } catch (final Exception e) {
                runOnUiThread(() -> {
                    toast("校验失败：" + e.getMessage());
                    askInvite();
                });
            }
        }).start();
    }

    /** 拍摄页顶部显示厂商 */
    private void refreshVendorLabel() {
        if (tvVendor == null) return;
        String vendor = store.vendor();
        String code = store.invite();
        if (vendor == null || vendor.isEmpty()) {
            tvVendor.setText("厂商：未设置（点这里填邀请码）");
            tvVendor.setTextColor(DANGER);
        } else {
            tvVendor.setText("厂商：" + vendor + "　（邀请码 " + code + "，点这里可改）");
            tvVendor.setTextColor(MUTED);
        }
    }'''
assert old_ask in t
t = t.replace(old_ask, new_ask)

io.open(p2, 'w', encoding='utf-8').write(t)
print('MainActivity 邀请码逻辑已改')
