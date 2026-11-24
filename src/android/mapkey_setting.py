"""设置里加「地图 Key」输入框，方便换成 Web服务 类型的 Key。"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

old = '''        final EditText srv = new EditText(this);
        srv.setText(store.server());
        srv.setTextSize(15);
        box.addView(labelText("服务器地址"));
        box.addView(srv);

        new AlertDialog.Builder(this)
                .setTitle("设置")
                .setView(box)
                .setPositiveButton("保存", (d, w) -> {
                    store.setServer(srv.getText().toString().trim());
                    api.base = store.server();
                    api.token = "";
                    store.setToken("");
                    autoLogin();
                })'''

new = '''        final EditText srv = new EditText(this);
        srv.setText(store.server());
        srv.setTextSize(15);
        box.addView(labelText("服务器地址"));
        box.addView(srv);

        final EditText mapKey = new EditText(this);
        mapKey.setText(store.get("map_key", MapSnap.DEFAULT_KEY));
        mapKey.setTextSize(15);
        box.addView(labelText("高德地图 Key（Web服务类型，用于水印右上角小地图）"));
        box.addView(mapKey);

        new AlertDialog.Builder(this)
                .setTitle("设置")
                .setView(box)
                .setPositiveButton("保存", (d, w) -> {
                    store.setServer(srv.getText().toString().trim());
                    store.put("map_key", mapKey.getText().toString().trim());
                    api.base = store.server();
                    api.token = "";
                    store.setToken("");
                    autoLogin();
                    startGps();
                })'''
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('设置里加了地图 Key')

# 版本 68
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="67"', 'android:versionCode="68"').replace('android:versionName="67.0"', 'android:versionName="68.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v67.apk', 'egoops-collect-v68.apk').replace('--version-code 67 --version-name 67.0', '--version-code 68 --version-name 68.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 68')
