"""按「给中年人用」的原则简化：
   设置里只留服务器地址，地图 Key 不做成用户要填的东西；
   Key 由开发方编译进 App（MapSnap.DEFAULT_KEY），用户永远不需要碰。
"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

old = '''        final EditText mapKey = new EditText(this);
        mapKey.setText(store.get("map_key", MapSnap.DEFAULT_KEY));
        mapKey.setTextSize(15);
        box.addView(labelText("高德地图 Key（Web服务类型，用于水印右上角小地图）"));
        box.addView(mapKey);

'''
assert old in s
s = s.replace(old, '')

s = s.replace('''                    store.setServer(srv.getText().toString().trim());
                    store.put("map_key", mapKey.getText().toString().trim());''',
'''                    store.setServer(srv.getText().toString().trim());''')

# 读取 key 时不看用户设置，直接用编译进去的
s = s.replace('                    String key = store.get("map_key", MapSnap.DEFAULT_KEY);',
              '                    String key = MapSnap.DEFAULT_KEY;')

io.open(p, 'w', encoding='utf-8').write(s)
print('设置里去掉地图 Key')

# 版本 69
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="68"', 'android:versionCode="69"').replace('android:versionName="68.0"', 'android:versionName="69.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v68.apk', 'egoops-collect-v69.apk').replace('--version-code 68 --version-name 68.0', '--version-code 69 --version-name 69.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 69')
