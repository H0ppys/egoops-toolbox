import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 声明字段
if 'private EditText etInvite;' not in s:
    s = s.replace('private TextView tvStep, tvDots, tvUpload, tvDoneStatus, tvTaskDoneTitle, tvTaskDoneSub, tvVendor;',
                  'private TextView tvStep, tvDots, tvUpload, tvDoneStatus, tvTaskDoneTitle, tvTaskDoneSub, tvVendor;\n    private EditText etInvite;')
    print('字段已加')

# 2) 邀请码输入框（放在厂商提示行之后）
if 'etInvite = new EditText(this);' not in s:
    anchor = '''        content.addView(tvVendor);
        refreshVendorLabel();'''
    block = '''        content.addView(tvVendor);
        refreshVendorLabel();

        TextView lInv = new TextView(this);
        lInv.setText("邀请码（必填，管理员事先约定，例如 ZJMEIYI）");
        lInv.setTextSize(15);
        lInv.setTextColor(MUTED);
        lInv.setPadding(dp(4), dp(2), 0, dp(6));
        content.addView(lInv);

        etInvite = new EditText(this);
        etInvite.setText(store.invite());
        etInvite.setHint("ZJMEIYI");
        etInvite.setTextSize(20);
        etInvite.setSingleLine(true);
        etInvite.setBackground(roundRect(CARD, 12));
        etInvite.setPadding(dp(16), dp(10), dp(16), dp(10));
        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));'''
    assert anchor in s
    s = s.replace(anchor, block, 1)
    print('输入框已加')

# 3) 开始拍摄时校验
if '请填写邀请码' not in s:
    s = s.replace('''        String addr = provName''', '''        String invite = etInvite == null ? store.invite() : etInvite.getText().toString().trim().toUpperCase();
        if (invite.isEmpty()) {
            toast("请填写邀请码");
            if (etInvite != null) etInvite.requestFocus();
            return;
        }
        store.setInvite(invite);

        String addr = provName''')
    s = s.replace('''        site.address = addr;''', '''        site.address = addr;
        site.invite = invite;''')
    print('校验已加')

io.open(p, 'w', encoding='utf-8').write(s)
print('done')
