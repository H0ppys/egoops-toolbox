"""自动取回水印相机刚拍的文件：
   1) 打开水印相机时记下时间戳
   2) 回到 App 后，查询 MediaStore 里比该时间戳更新的最新照片/视频
   3) 找到就直接导入（无需用户手点相册）；找不到才退回相册选择
   4) 补上读取媒体权限
"""

import io

# ---------------- 清单：读取媒体权限 ----------------
p = 'android/AndroidManifest.xml'
s = io.open(p, encoding='utf-8').read()
add = []
if 'READ_MEDIA_IMAGES' not in s:
    add.append('<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />')
if 'READ_MEDIA_VIDEO' not in s:
    add.append('<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />')
if 'READ_EXTERNAL_STORAGE' not in s:
    add.append('<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />')
if add:
    anchor = '<uses-permission android:name="android.permission.CAMERA" />'
    s = s.replace(anchor, anchor + '\n    ' + '\n    '.join(add))
    io.open(p, 'w', encoding='utf-8').write(s)
    print('清单：媒体读权限已加')

# ---------------- MainActivity ----------------
P = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(P, encoding='utf-8').read()

# 1) 记录打开水印相机的时间
if 'wmLaunchAt' not in t:
    t = t.replace('    private boolean awaitingWatermarkImport = false;',
                  '    private boolean awaitingWatermarkImport = false;\n    private long wmLaunchAt = 0;')

    t = t.replace('''                        startActivity(it);
                        awaitingWatermarkImport = true;''',
'''                        startActivity(it);
                        wmLaunchAt = System.currentTimeMillis();
                        awaitingWatermarkImport = true;''')

# 2) onResume：先尝试自动抓取，抓不到再弹相册
old = '''            if (shot != null && !shot.isEmpty()) {
                tvStep.postDelayed(() -> {
                    toast("请选刚拍好的那张");
                    pickShot(shot, kind);
                }, 400);
            }'''
new = '''            if (shot != null && !shot.isEmpty()) {
                tvStep.postDelayed(() -> autoGrabLatest(shot, kind), 500);
            }'''
assert old in t
t = t.replace(old, new)

# 3) 自动抓最新文件
if 'autoGrabLatest' not in t:
    anchor = '    /** 从相册选已有照片/视频 */'
    block = r'''    /** 从水印相机回来：自动抓「比打开时刻更新」的最新一张/一段 */
    private void autoGrabLatest(String shot, String kind) {
        boolean video = kind.equals("video");
        Uri found = null;
        String name = "";
        try {
            long since = wmLaunchAt > 0 ? wmLaunchAt - 3000 : System.currentTimeMillis() - 300000;
            android.database.Cursor c;
            if (video) {
                c = getContentResolver().query(
                        MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                        new String[]{MediaStore.Video.Media._ID, MediaStore.Video.Media.DISPLAY_NAME,
                                MediaStore.Video.Media.DATE_ADDED},
                        MediaStore.Video.Media.DATE_ADDED + " >= ?",
                        new String[]{String.valueOf(since / 1000)},
                        MediaStore.Video.Media.DATE_ADDED + " DESC");
            } else {
                c = getContentResolver().query(
                        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                        new String[]{MediaStore.Images.Media._ID, MediaStore.Images.Media.DISPLAY_NAME,
                                MediaStore.Images.Media.DATE_ADDED},
                        MediaStore.Images.Media.DATE_ADDED + " >= ?",
                        new String[]{String.valueOf(since / 1000)},
                        MediaStore.Images.Media.DATE_ADDED + " DESC");
            }
            if (c != null && c.moveToFirst()) {
                long id = c.getLong(0);
                name = c.getString(1);
                Uri base = video ? MediaStore.Video.Media.EXTERNAL_CONTENT_URI
                        : MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
                found = android.content.ContentUris.withAppendedId(base, id);
            }
            if (c != null) c.close();
        } catch (Throwable ignored) {
        }

        if (found == null) {
            toast("没找到刚拍的，请手动选一下");
            pickShot(shot, kind);
            return;
        }
        toast("已自动取回：" + name);
        ingest(found, video);
    }

'''
    assert anchor in t
    t = t.replace(anchor, block + anchor, 1)

# 4) 把 onActivityResult 的处理抽成 ingest(Uri, boolean)，供两处调用
old_head = '''        boolean fromPick = requestCode == REQ_PICK_PHOTO || requestCode == REQ_PICK_VIDEO;
        boolean video = requestCode == REQ_VIDEO || requestCode == REQ_PICK_VIDEO;
        Uri src;
        if (fromPick) {
            src = data != null ? data.getData() : null;
        } else {
            src = (data != null && data.getData() != null) ? data.getData() : tempUri;
        }
        if (src == null) { toast("没有拿到画面，请再拍一次"); return; }

        try {'''
new_head = '''        boolean fromPick = requestCode == REQ_PICK_PHOTO || requestCode == REQ_PICK_VIDEO;
        boolean video = requestCode == REQ_VIDEO || requestCode == REQ_PICK_VIDEO;
        Uri src;
        if (fromPick) {
            src = data != null ? data.getData() : null;
        } else {
            src = (data != null && data.getData() != null) ? data.getData() : tempUri;
        }
        if (src == null) { toast("没有拿到画面，请再拍一次"); return; }
        ingest(src, video);
    }

    /** 把一份素材收进当前拍摄项（相机、相册、水印相机自动取回都走这里） */
    private void ingest(Uri src, boolean video) {
        try {'''
assert old_head in t
t = t.replace(old_head, new_head)

io.open(P, 'w', encoding='utf-8').write(t)
print('MainActivity: 自动取回 + ingest 重构')

# 5) 启动时申请媒体读权限
t = io.open(P, encoding='utf-8').read()
if 'READ_MEDIA_IMAGES' not in t.split('askAllPermissions')[1][:1500]:
    t = t.replace('''        need.add(Manifest.permission.CAMERA);''',
'''        need.add(Manifest.permission.CAMERA);
        if (Build.VERSION.SDK_INT >= 33) {
            need.add("android.permission.READ_MEDIA_IMAGES");
            need.add("android.permission.READ_MEDIA_VIDEO");
        } else {
            need.add(Manifest.permission.READ_EXTERNAL_STORAGE);
        }''')
    io.open(P, 'w', encoding='utf-8').write(t)
    print('启动时申请媒体权限')
