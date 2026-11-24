import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# ---------- 1) 上传完成后：留缩略图，删原文件（省空间） ----------
if 'archiveUploaded' not in s:
    s = s.replace('''            @Override public void onDone(int files) {
                uploading = false;''', '''            @Override public void onDone(int files) {
                uploading = false;
                archiveUploaded();''')

    s = s.replace('''    /** 上次没传完：打开 App 自动接着传 */''', '''    /** 传完的素材：生成缩略图留本地，原文件删掉（服务器已有） */
    private void archiveUploaded() {
        new Thread(() -> {
            try {
                File thumbDir = new File(getExternalFilesDir(null), "thumbs");
                if (!thumbDir.exists()) thumbDir.mkdirs();
                for (Model.Task t : site.tasks) {
                    for (Model.Media m : t.media) {
                        if (!"uploaded".equals(m.state)) continue;
                        File src = new File(m.path);
                        if (!src.exists()) continue;
                        File th = new File(thumbDir, src.getName() + ".jpg");
                        if (!th.exists()) {
                            if ("photo".equals(m.kind)) {
                                saveThumb(src, th, 320);
                            } else {
                                saveVideoThumb(src, th);
                            }
                        }
                        if (th.exists() && th.length() > 0) src.delete();
                    }
                }
            } catch (Exception ignored) {
            }
        }).start();
    }

    private void saveThumb(File src, File dst, int maxPx) {
        try {
            android.graphics.BitmapFactory.Options o = new android.graphics.BitmapFactory.Options();
            o.inJustDecodeBounds = true;
            android.graphics.BitmapFactory.decodeFile(src.getAbsolutePath(), o);
            int sample = 1;
            while (o.outWidth / sample > maxPx * 2) sample *= 2;
            android.graphics.BitmapFactory.Options o2 = new android.graphics.BitmapFactory.Options();
            o2.inSampleSize = sample;
            android.graphics.Bitmap bmp = android.graphics.BitmapFactory.decodeFile(src.getAbsolutePath(), o2);
            if (bmp == null) return;
            FileOutputStream out = new FileOutputStream(dst);
            bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 80, out);
            out.close();
            bmp.recycle();
        } catch (Exception ignored) {
        }
    }

    private void saveVideoThumb(File src, File dst) {
        try {
            android.media.MediaMetadataRetriever r = new android.media.MediaMetadataRetriever();
            r.setDataSource(src.getAbsolutePath());
            android.graphics.Bitmap bmp = r.getFrameAtTime(0);
            r.release();
            if (bmp == null) return;
            FileOutputStream out = new FileOutputStream(dst);
            bmp.compress(android.graphics.Bitmap.CompressFormat.JPEG, 80, out);
            out.close();
            bmp.recycle();
        } catch (Exception ignored) {
        }
    }

    /** 上次没传完：打开 App 自动接着传 */''')

# ---------- 2) 开始页：「继续上次采集点」按钮 ----------
if '继续上次采集点' not in s:
    s = s.replace('''        Button btn = new Button(this);
        btn.setText("开始拍摄");''', '''        Button btnResume = new Button(this);
        btnResume.setText("继续上次的采集点（补拍/续传）");
        btnResume.setAllCaps(false);
        btnResume.setTextSize(17);
        btnResume.setOnClickListener(v -> resumeLastSite());
        LinearLayout.LayoutParams rlp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(52));
        rlp.topMargin = dp(10);
        content.addView(btnResume, rlp);

        Button btn = new Button(this);
        btn.setText("开始拍摄");''')

    s = s.replace('''    /** 上次没传完：打开 App 自动接着传 */''', '''    /** 回到上次没拍完/没传完的采集点 */
    private void resumeLastSite() {
        Model.Site saved = store.loadQueue();
        if (saved == null || (saved.tasks.isEmpty())) {
            toast("没有未完成的采集点");
            return;
        }
        site = saved;
        int firstTask = 0;
        for (int i = 0; i < site.tasks.size(); i++) {
            if (doneCount(i) < shotsOf(site.tasks.get(i)).length) { firstTask = i; break; }
        }
        currentTask = firstTask;
        currentShot = firstUndone(currentTask);
        if (currentShot < 0) {
            toast("这个采集点已经拍完，可直接上传");
            showPage(3);
            startUpload();
            return;
        }
        toast("继续：" + labelOf(site.tasks.get(currentTask)));
        renderShot();
        showPage(2);
    }

    /** 上次没传完：打开 App 自动接着传 */''')

io.open(p, 'w', encoding='utf-8').write(s)
print('补拍入口 + 缩略图归档已加')
