import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 启动时把需要的权限一次性要齐（含 Android 13 的通知权限，否则上传进度看不到）
if 'askAllPermissions' not in s:
    s = s.replace('''    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {''',
'''    /** 相机 / 录音 / 读媒体 / 通知（上传进度的通知要它） */
    private void askAllPermissions() {
        if (Build.VERSION.SDK_INT < 23) return;
        java.util.List<String> need = new java.util.ArrayList<>();
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED)
            need.add(Manifest.permission.CAMERA);
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED)
            need.add(Manifest.permission.RECORD_AUDIO);
        if (Build.VERSION.SDK_INT >= 33) {
            if (checkSelfPermission("android.permission.POST_NOTIFICATIONS") != PackageManager.PERMISSION_GRANTED)
                need.add("android.permission.POST_NOTIFICATIONS");
            if (checkSelfPermission("android.permission.READ_MEDIA_IMAGES") != PackageManager.PERMISSION_GRANTED)
                need.add("android.permission.READ_MEDIA_IMAGES");
            if (checkSelfPermission("android.permission.READ_MEDIA_VIDEO") != PackageManager.PERMISSION_GRANTED)
                need.add("android.permission.READ_MEDIA_VIDEO");
        }
        if (!need.isEmpty()) requestPermissions(need.toArray(new String[0]), REQ_PERM_ALL);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {''')

    s = s.replace('private static final int REQ_PHOTO = 1001;',
                  'private static final int REQ_PHOTO = 1001;\n    private static final int REQ_PERM_ALL = 1100;')

    # onCreate 里调用
    s = s.replace('''        resumePendingUpload();''', '''        resumePendingUpload();
        askAllPermissions();''', 1)

# 2) 返回键：在拍摄/完成页按返回先确认，避免误退丢进度
if 'onBackPressed' not in s:
    s = s.replace('''    private void showPage(int p) {''', '''    @Override
    public void onBackPressed() {
        if (page > 0) {
            new AlertDialog.Builder(this)
                    .setTitle("要退出吗？")
                    .setMessage("拍到的东西已经存在手机里，下次打开可以接着拍，不会丢。")
                    .setPositiveButton("退出", (d, w) -> finish())
                    .setNegativeButton("继续拍", null)
                    .show();
            return;
        }
        super.onBackPressed();
    }

    private void showPage(int p) {''')

io.open(p, 'w', encoding='utf-8').write(s)
print('Android 权限 + 返回键 已加')
