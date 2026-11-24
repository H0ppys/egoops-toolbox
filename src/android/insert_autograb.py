import io

P = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(P, encoding='utf-8').read()

if 'private void autoGrabLatest' in t:
    print('方法已存在')
    raise SystemExit(0)

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
                        new String[]{MediaStore.Video.Media._ID, MediaStore.Video.Media.DISPLAY_NAME},
                        MediaStore.Video.Media.DATE_ADDED + " >= ?",
                        new String[]{String.valueOf(since / 1000)},
                        MediaStore.Video.Media.DATE_ADDED + " DESC");
            } else {
                c = getContentResolver().query(
                        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                        new String[]{MediaStore.Images.Media._ID, MediaStore.Images.Media.DISPLAY_NAME},
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

anchor = '    /** 从相册选已有照片/视频 */'
assert anchor in t
t = t.replace(anchor, block + anchor, 1)
io.open(P, 'w', encoding='utf-8').write(t)
print('autoGrabLatest 已插入')
