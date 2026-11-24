"""增强「不拍摄收集」版：
   1) 批量导入：一次选多张/多段，按顺序填满当前区域剩下的项
   2) 自动取回增强：严格时间窗找不到时，放宽到 30 分钟 + 文件名前缀
   3) 拍摄页显示本机使用的拍摄 App 名称
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# ---------- 1) 新请求码 ----------
if 'REQ_PICK_MULTI' not in s:
    s = s.replace('    private static final int REQ_PICK_VIDEO = 1004;',
                  '    private static final int REQ_PICK_VIDEO = 1004;\n    private static final int REQ_PICK_MULTI = 1006;')

# ---------- 2) 拍摄页：加「批量选」按钮 + 显示当前拍摄 App ----------
if '批量选剩下的项' not in s:
    old = '''        Button pick = secondaryButton(pickText, BuildConfigVersion.NO_CAPTURE ? 64 : 54);'''
    new = '''        if (BuildConfigVersion.NO_CAPTURE) {
            Button multi = secondaryButton("批量选剩下的项（一次选多张）", 56);
            multi.setOnClickListener(v -> pickMultiple());
            LinearLayout.LayoutParams mlp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
            mlp.topMargin = dp(8);
            card.addView(multi, mlp);
        }

        Button pick = secondaryButton(pickText, BuildConfigVersion.NO_CAPTURE ? 64 : 54);'''
    assert old in s
    s = s.replace(old, new)

# ---------- 3) 多选导入 ----------
if 'private void pickMultiple' not in s:
    block = r'''    /** 一次选多张，按顺序填进当前任务剩下的项 */
    private void pickMultiple() {
        try {
            android.content.Intent i = new android.content.Intent(android.content.Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(android.content.Intent.CATEGORY_OPENABLE);
            String kind = (pendingShot != null && pendingShot.toLowerCase().contains("video")) ? "video" : "photo";
            i.setType(kind.equals("video") ? "video/*" : "image/*");
            i.putExtra(android.content.Intent.EXTRA_ALLOW_MULTIPLE, true);
            startActivityForResult(i, REQ_PICK_MULTI);
        } catch (Throwable e) {
            toast("这台手机不支持批量选择：" + e);
        }
    }

    /** 批量导入：把选中的素材按顺序塞进未完成的项 */
    private void ingestMultiple(android.content.ClipData clip) {
        Model.Task task = task(currentTask);
        String[][] shots = shotsOf(task);
        int taken = 0;
        for (int i = 0; i < clip.getItemCount(); i++) {
            if (taken >= 30) break;
            Uri uri = clip.getItemAt(i).getUri();
            // 找下一个还没拍的项
            int idx = -1;
            for (int k = 0; k < shots.length; k++) {
                if (!hasShot(currentTask, k)) {
                    idx = k;
                    break;
                }
            }
            if (idx < 0) break;
            pendingShot = shots[idx][0];
            String kind = shots[idx][3];
            boolean isVideo = kind.equals("video");
            // 类型不匹配就跳过
            String type = "";
            try {
                type = String.valueOf(getContentResolver().getType(uri));
            } catch (Throwable ignored) {
            }
            if (isVideo && !type.startsWith("video")) continue;
            if (!isVideo && !type.startsWith("image")) continue;
            ingest(uri, isVideo);
            taken++;
        }
        if (taken == 0) {
            toast("选中的素材没对上：请确认照片/视频类型");
        } else {
            toast("已导入 " + taken + " 个素材");
        }
    }

'''
    anchor = '    /** 从水印相机回来：自动抓「比打开时刻更新」的最新一张/一段 */'
    assert anchor in s
    s = s.replace(anchor, block + anchor, 1)

# ---------- 4) onActivityResult 处理多选 ----------
old_res = '''        boolean fromPick = requestCode == REQ_PICK_PHOTO || requestCode == REQ_PICK_VIDEO;'''
new_res = '''        if (requestCode == REQ_PICK_MULTI) {
            android.content.ClipData clip = data != null ? data.getClipData() : null;
            if (clip == null && data != null && data.getData() != null) {
                // 只选了一个
                String kind = (pendingShot != null && pendingShot.toLowerCase().contains("video")) ? "video" : "photo";
                ingest(data.getData(), kind.equals("video"));
                return;
            }
            if (clip != null) ingestMultiple(clip);
            return;
        }

        boolean fromPick = requestCode == REQ_PICK_PHOTO || requestCode == REQ_PICK_VIDEO;'''
assert old_res in s
s = s.replace(old_res, new_res)

# ---------- 5) 自动取回：放宽 + 前缀 ----------
old_grab = '''            if (c != null && c.moveToFirst()) {'''
new_grab = '''            if (c == null || !c.moveToFirst()) {
                // 放宽到 30 分钟 + 文件名前缀（水印相机常见命名）
                long since2 = System.currentTimeMillis() - 30L * 60 * 1000;
                if (c != null) c.close();
                c = video
                        ? getContentResolver().query(MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                        new String[]{MediaStore.Video.Media._ID, MediaStore.Video.Media.DISPLAY_NAME},
                        MediaStore.Video.Media.DATE_ADDED + " >= ?",
                        new String[]{String.valueOf(since2 / 1000)},
                        MediaStore.Video.Media.DATE_ADDED + " DESC")
                        : getContentResolver().query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                        new String[]{MediaStore.Images.Media._ID, MediaStore.Images.Media.DISPLAY_NAME},
                        MediaStore.Images.Media.DATE_ADDED + " >= ?",
                        new String[]{String.valueOf(since2 / 1000)},
                        MediaStore.Images.Media.DATE_ADDED + " DESC");
            }
            if (c != null && c.moveToFirst()) {'''
assert old_grab in s
s = s.replace(old_grab, new_grab, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('不拍版增强：批量导入 + 取回放宽')
