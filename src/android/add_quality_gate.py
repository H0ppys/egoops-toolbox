import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# 1) 拍完先质检，不合格就提示重拍
old = '''            Model.Media m = new Model.Media(dest.getAbsolutePath(), video ? "video" : "photo",
                    video ? "video/mp4" : "image/jpeg", dest.length());'''
new = '''            String problem = checkQuality(dest.getAbsolutePath(), video);
            if (problem != null) {
                final File tmpFile = dest;
                final Uri oldUri = src;
                new AlertDialog.Builder(this)
                        .setTitle("这张可能不合格")
                        .setMessage(problem + "\\n\\n建议重拍，也可以先留着。")
                        .setPositiveButton("重拍", (d, w) -> {
                            try { tmpFile.delete(); } catch (Exception ignored) {}
                            shoot(pendingShot);
                        })
                        .setNegativeButton("仍然使用", (d, w) -> acceptCapture(tmpFile, video))
                        .setCancelable(false)
                        .show();
                return;
            }

            Model.Media m = new Model.Media(dest.getAbsolutePath(), video ? "video" : "photo",
                    video ? "video/mp4" : "image/jpeg", dest.length());'''
assert old in s
s = s.replace(old, new)

# 2) 把「收下这份素材」的逻辑抽成方法（重拍确认后会再调一次）
old2 = '''            if (doneCount(currentTask) >= shotsOf(task).length) {
                toast("这个任务拍完了");'''
new2 = '''            if (doneCount(currentTask) >= shotsOf(task).length) {
                toast("这个任务拍完了");'''
# 上面这段保持不动，改成把整段包进新方法需要更大幅度改动，这里只做最小侵入：
# 把 acceptCapture 作为独立方法追加（内部复用同一段落）
tail = '''    /** 质检：模糊 / 过暗 / 视频太短 返回问题描述，合格返回 null */
    private String checkQuality(String path, boolean video) {
        try {
            if (video) {
                android.media.MediaMetadataRetriever r = new android.media.MediaMetadataRetriever();
                r.setDataSource(path);
                String dur = r.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_DURATION);
                r.release();
                long ms = dur == null ? 0 : Long.parseLong(dur);
                if (ms < 2000) return "视频只有 " + (ms / 1000.0) + " 秒，太短了（至少 2 秒）";
                return null;
            }
            android.graphics.BitmapFactory.Options opt = new android.graphics.BitmapFactory.Options();
            opt.inSampleSize = 4;
            android.graphics.Bitmap bmp = android.graphics.BitmapFactory.decodeFile(path, opt);
            if (bmp == null) return null;
            int w = bmp.getWidth(), h = bmp.getHeight();
            int[] px = new int[w * h];
            bmp.getPixels(px, 0, w, 0, 0, w, h);
            bmp.recycle();
            if (w < 8 || h < 8) return null;
            long sum = 0;
            for (int v : px) {
                int g = (int) (((v >> 16) & 0xFF) * 0.299 + ((v >> 8) & 0xFF) * 0.587 + (v & 0xFF) * 0.114);
                sum += g;
            }
            double mean = sum / (double) px.length;
            double lapSum = 0, lapSq = 0;
            int cnt = 0;
            for (int y = 1; y < h - 1; y++) {
                for (int x = 1; x < w - 1; x++) {
                    int c = gray(px[y * w + x]);
                    int lap = 4 * c - gray(px[(y - 1) * w + x]) - gray(px[(y + 1) * w + x])
                            - gray(px[y * w + x - 1]) - gray(px[y * w + x + 1]);
                    lapSum += lap;
                    lapSq += (double) lap * lap;
                    cnt++;
                }
            }
            double var = cnt == 0 ? 0 : (lapSq / cnt - Math.pow(lapSum / cnt, 2));
            if (var < 25) return String.format("画面偏模糊（清晰度 %.0f）", var);
            if (mean < 40) return String.format("画面偏暗（亮度 %.0f）", mean);
            if (mean > 225) return String.format("画面过亮（亮度 %.0f）", mean);
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private int gray(int c) {
        return (int) (((c >> 16) & 0xFF) * 0.299 + ((c >> 8) & 0xFF) * 0.587 + (c & 0xFF) * 0.114);
    }

    /** 质检通过后收下这份素材（原逻辑） */
    private void acceptCapture(File dest, boolean video) {
        Model.Media m = new Model.Media(dest.getAbsolutePath(), video ? "video" : "photo",
                video ? "video/mp4" : "image/jpeg", dest.length());
        m.shot = pendingShot;
        Model.Task task = task(currentTask);
        for (int i = task.media.size() - 1; i >= 0; i--) {
            Model.Media old = task.media.get(i);
            if (pendingShot.equals(old.shot)) {
                if ("uploaded".equals(old.state) && old.fileId != null && !old.fileId.isEmpty()) {
                    deleteFileRemote(old.fileId);
                }
                task.media.remove(i);
            }
        }
        task.media.add(m);
        store.saveQueue(site);
        if (doneCount(currentTask) >= shotsOf(task).length) {
            toast("这个任务拍完了");
            tvTaskDoneTitle.setText(labelOf(task) + " 拍完了");
            tvTaskDoneSub.setText("site".equals(task.type) ? "这个采集点还有区域要拍吗？" : "还有区域或任务要拍吗？");
            showPage(3);
            if (!uploading) startUpload();
        } else {
            currentShot = firstUndone(currentTask);
            toast("再拍下一项");
            renderShot();
        }
    }

    private void confirmRestart() {'''

s = s.replace('    private void confirmRestart() {', tail, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('质检闸门已加')
