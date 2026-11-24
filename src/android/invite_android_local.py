import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 校验逻辑改成纯本地：不连服务器，只记下来
start = s.index('    /** 调服务器确认邀请码，拿到厂商名 */')
end = s.index('    /** 拍摄页顶部显示厂商 */')
new = '''    /** 邀请码由管理员和采集员事先约定，服务器不校验，这里只检查格式并记住 */
    private void checkInviteThen(final String code) {
        if (code.length() < 4) {
            toast("邀请码太短，至少 4 位");
            askInvite();
            return;
        }
        store.setInvite(code);
        refreshVendorLabel();
        api.token = "";
        store.setToken("");
        toast("邀请码已记录：" + code);
        startUpload();
    }

'''
s = s[:start] + new + s[end:]

# 2) 顶部那行改成显示邀请码
start2 = s.index('    /** 拍摄页顶部显示厂商 */')
end2 = s.index('    private void loginNow(String name)')
new2 = '''    /** 拍摄页顶部显示当前邀请码 */
    private void refreshVendorLabel() {
        if (tvVendor == null) return;
        String code = store.invite();
        if (code == null || code.isEmpty()) {
            tvVendor.setText("邀请码：未填写（点这里填）");
            tvVendor.setTextColor(DANGER);
        } else {
            tvVendor.setText("邀请码：" + code + "　（点这里可改）");
            tvVendor.setTextColor(MUTED);
        }
        if (etInvite != null && !code.isEmpty() && etInvite.getText().toString().trim().isEmpty()) {
            etInvite.setText(code);
        }
    }

'''
s = s[:start2] + new2 + s[end2:]

# 3) 登录回来不再需要写 vendor
s = s.replace('''        String vendor = r.optString("vendor", "");
        if (vendor != null && !vendor.isEmpty()) {
            store.setVendor(vendor);
            final String vname = vendor;
            runOnUiThread(() -> toast("厂商：" + vname));
        }
        runOnUiThread(this::refreshVendorLabel);''', '''        runOnUiThread(this::refreshVendorLabel);''')

io.open(p, 'w', encoding='utf-8').write(s)
print('邀请码改成纯本地')
