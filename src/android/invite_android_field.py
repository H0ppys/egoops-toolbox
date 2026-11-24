import io

p = 'android/src/com/egoops/collect/Uploader.java'
s = io.open(p, encoding='utf-8').read()
s = s.replace('''        body.put("area", site.area);''', '''        body.put("area", site.area);
        body.put("invite", site.invite == null ? "" : site.invite);''')
io.open(p, 'w', encoding='utf-8').write(s)
print('Uploader: 上传带 invite')

# Model.Site 加 invite 字段
p2 = 'android/src/com/egoops/collect/Model.java'
m = io.open(p2, encoding='utf-8').read()
if 'public String invite' not in m:
    m = m.replace('''        public String scene = "";''', '''        public String scene = "";
        public String invite = "";''')
    io.open(p2, 'w', encoding='utf-8').write(m)
    print('Model: Site 加 invite')

# MainActivity：邀请码输入框 + 校验 + 写入 site
p3 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p3, encoding='utf-8').read()

if 'etInvite' not in t:
    t = t.replace('private TextView tvStep, tvDots, tvUpload, tvDoneStatus, tvTaskDoneTitle, tvTaskDoneSub, tvVendor;',
                  'private TextView tvStep, tvDots, tvUpload, tvDoneStatus, tvTaskDoneTitle, tvTaskDoneSub, tvVendor;\n    private EditText etInvite;')

    # 顶部厂商行下面加邀请码输入
    t = t.replace('''        content.addView(tvVendor);
        refreshVendorLabel();''', '''        content.addView(tvVendor);
        refreshVendorLabel();

        TextView lInv = new TextView(this);
        lInv.setText("邀请码（必填，管理员约定，例如 ZJMEIYI）");
        lInv.setTextSize(15);
        lInv.setTextColor(MUTED);
        lInv.setPadding(dp(4), 0, 0, dp(6));
        content.addView(lInv);

        etInvite = new EditText(this);
        etInvite.setText(store.invite());
        etInvite.setHint("ZJMEIYI");
        etInvite.setTextSize(20);
        etInvite.setSingleLine(true);
        etInvite.setBackground(roundRect(CARD, 12));
        etInvite.setPadding(dp(16), dp(10), dp(16), dp(10));
        content.addView(etInvite, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));''')

    # 开始拍摄时校验并保存
    t = t.replace('''        String addr = provName''', '''        String invite = etInvite.getText().toString().trim().toUpperCase();
        if (invite.isEmpty()) {
            toast("请填写邀请码");
            etInvite.requestFocus();
            return;
        }
        store.setInvite(invite);

        String addr = provName''')

    # 站点对象带上邀请码
    t = t.replace('''        site.address = addr;''', '''        site.address = addr;
        site.invite = invite;''')

    io.open(p3, 'w', encoding='utf-8').write(t)
    print('MainActivity: 邀请码输入框已加')
