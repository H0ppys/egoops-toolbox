import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 字段声明
s = s.replace("    private EditText etStoreName, etCollector, etArea;",
              "    private EditText etStoreName, etCollector, etArea, etAddress;")

# 2) beginShooting 校验并保存地址
old = '''        site.name = typed;
        String[] chosen = sceneItems.get(shownIndex.get(p2 - 1));'''
new = '''        String addr = etAddress.getText().toString().trim();
        if (addr.isEmpty()) {
            toast("请先填写现场地址");
            etAddress.requestFocus();
            return;
        }
        site.name = typed;
        site.address = addr;
        String[] chosen = sceneItems.get(shownIndex.get(p2 - 1));'''
assert old in s
s = s.replace(old, new)

# 3) 恢复上次填的地址
old2 = '''        etStoreName.setText(site.name);'''
if old2 in s:
    s = s.replace(old2, '''        etStoreName.setText(site.name);''')

io.open(p, 'w', encoding='utf-8').write(s)
print('address patched')
