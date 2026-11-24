import io

p = 'android/AndroidManifest.xml'
s = io.open(p, encoding='utf-8').read()

s = s.replace('''    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />''',
'''    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />''')

s = s.replace('''        </activity>
    </application>''', '''        </activity>

        <service
            android:name=".UploadService"
            android:exported="false"
            android:foregroundServiceType="dataSync" />
    </application>''')

io.open(p, 'w', encoding='utf-8').write(s)
print('manifest: service + permissions')

# MainActivity：上传开始时起前台服务，结束时停掉
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('''        uploading = true;
        tvUpload.setText("正在上传…");
        tvUpload.setTextColor(MUTED);''', '''        uploading = true;
        tvUpload.setText("正在上传…");
        tvUpload.setTextColor(MUTED);
        UploadService.start(this, "准备上传…");''')

t = t.replace('''            @Override public void onStage(String msg) { }''',
'''            @Override public void onStage(String msg) {
                runOnUiThread(() -> UploadService.update(MainActivity.this, msg, -1, 0, 0));
            }''')

t = t.replace('''                String s = "已上传 " + done + "/" + total + " 个文件 · " + pct + "%";
                tvUpload.setText(s);''', '''                String s = "已上传 " + done + "/" + total + " 个文件 · " + pct + "%";
                UploadService.update(MainActivity.this, s, pct, done, total);
                tvUpload.setText(s);''')

t = t.replace('''            @Override public void onDone(int files) {
                uploading = false;''', '''            @Override public void onDone(int files) {
                uploading = false;
                UploadService.stop(MainActivity.this, "上传完成，共 " + files + " 个文件");''')

t = t.replace('''            @Override public void onError(String message, String detail) {
                uploading = false;''', '''            @Override public void onError(String message, String detail) {
                uploading = false;
                UploadService.stop(MainActivity.this, "上传中断，打开 App 可继续");''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('MainActivity: 上传挂到前台服务')
