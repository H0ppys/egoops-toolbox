"""修「某项只能从相册上传、拍照没反应」：
   1) 相机/录像 Intent 失败时自动退回相册选择，并提示原因
   2) 相机权限被永久拒绝时，弹窗引导去设置开启
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

old = '''    private void captureShot(String shot, String kind) {
        if (Build.VERSION.SDK_INT >= 23 && checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            pendingShot = shot;
            requestPermissions(new String[]{Manifest.permission.CAMERA}, REQ_PERM);
            toast("请点“允许”，才能用相机");
            return;
        }'''
new = '''    private void captureShot(String shot, String kind) {
        if (Build.VERSION.SDK_INT >= 23 && checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            pendingShot = shot;
            if (!shouldShowRequestPermissionRationale(Manifest.permission.CAMERA)
                    && getSharedPreferences("egoops", MODE_PRIVATE).getBoolean("asked_camera", false)) {
                // 被「拒绝且不再询问」了，只能去设置里开
                new AlertDialog.Builder(this)
                        .setTitle("需要相机权限")
                        .setMessage("系统里已经把相机权限关掉了，需要到「设置 → 应用 → 采集点拍照 → 权限」里打开相机。\\n\\n要现在去设置吗？")
                        .setPositiveButton("去设置", (d, w) -> {
                            try {
                                startActivity(new android.content.Intent(
                                        android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                                        android.net.Uri.parse("package:" + getPackageName())));
                            } catch (Exception ignored) {
                            }
                        })
                        .setNegativeButton("先不拍", null)
                        .show();
                return;
            }
            getSharedPreferences("egoops", MODE_PRIVATE).edit().putBoolean("asked_camera", true).apply();
            requestPermissions(new String[]{Manifest.permission.CAMERA}, REQ_PERM);
            toast("请点“允许”，才能用相机");
            return;
        }'''
assert old in s
s = s.replace(old, new)

# Intent 包一层，失败就退回相册
s = s.replace('''            startActivityForResult(i, REQ_VIDEO);''',
'''            try {
                startActivityForResult(i, REQ_VIDEO);
            } catch (Exception e) {
                toast("这台手机没有可用的录像界面，请改用「从相册选视频」");
                pickShot(shot, kind);
            }''')
s = s.replace('''            startActivityForResult(i, REQ_PHOTO);''',
'''            try {
                startActivityForResult(i, REQ_PHOTO);
            } catch (Exception e) {
                toast("这台手机没有可用的相机界面，请改用「从相册选照片」");
                pickShot(shot, kind);
            }''')

io.open(P, 'w', encoding='utf-8').write(s)
print('相机启动失败会退回相册；权限被拒可跳设置')

# 权限回调里，授权后自动继续拍
old2 = '''    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grants) {'''
if old2 in s:
    idx = s.index(old2)
    print('有权限回调')

# 版本 65
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="64"', 'android:versionCode="65"')
m = m.replace('android:versionName="64.0"', 'android:versionName="65.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v64.apk', 'egoops-collect-v65.apk')
b = b.replace('--version-code 64 --version-name 64.0', '--version-code 65 --version-name 65.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 65')
