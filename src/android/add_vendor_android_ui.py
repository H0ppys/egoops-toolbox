import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 声明 tvVendor
s = s.replace('private TextView tvStep, tvDots, tvUpload, tvDoneStatus, tvTaskDoneTitle, tvTaskDoneSub;',
              'private TextView tvStep, tvDots, tvUpload, tvDoneStatus, tvTaskDoneTitle, tvTaskDoneSub, tvVendor;')

# 2) 开始页顶部加厂商行（放在内容最上面）
old = '''        TextView l2 = new TextView(this);
        l2.setText("门店名称（必填）");'''
new = '''        tvVendor = new TextView(this);
        tvVendor.setTextSize(15);
        tvVendor.setTextColor(MUTED);
        tvVendor.setPadding(dp(6), dp(4), dp(6), dp(12));
        tvVendor.setOnClickListener(v -> askInvite());
        content.addView(tvVendor);
        refreshVendorLabel();

        TextView l2 = new TextView(this);
        l2.setText("门店名称（必填）");'''
assert old in s
s = s.replace(old, new)

# 3) 设置里加「重填邀请码」
s = s.replace('''                .setNegativeButton("取消", null)
                .show();
    }

    private void loginNow(String name)''', '''                .setNeutralButton("改邀请码", (d, w) -> askInvite())
                .setNegativeButton("取消", null)
                .show();
    }

    private void loginNow(String name)''')

io.open(p, 'w', encoding='utf-8').write(s)
print('Android 厂商行已加')
