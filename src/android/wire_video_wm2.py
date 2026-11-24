"""接线视频水印（用实际存在的代码片段）。"""

import io

p = 'android/src/com/egoops/collect/Uploader.java'
s = io.open(p, encoding='utf-8').read()

if 'WatermarkVideo' not in s:
    old = '''                        stage("上传：" + task.name + " · " + new File(m.path).getName());
                        sentAll += uploadOneWithRetry(task, m);'''
    new = '''                        if ("video".equals(m.kind)) watermarked(m);
                        stage("上传：" + task.name + " · " + new File(m.path).getName());
                        sentAll += uploadOneWithRetry(task, m);'''
    assert old in s
    s = s.replace(old, new)

    helper = '''    /** 视频上传前烧水印；失败就用原文件，不阻断上传 */
    private void watermarked(Model.Media m) {
        try {
            File src = new File(m.path);
            if (!src.exists() || src.length() > 200L * 1024 * 1024) return;
            File out = new File(src.getParentFile(), "wm_" + src.getName());
            if (out.exists() && out.length() > 0) {
                String oldPath = m.path;
                m.path = out.getAbsolutePath();
                m.watermarkSrc = oldPath;
                return;
            }
            int w = 0, h = 0;
            try {
                android.media.MediaMetadataRetriever r = new android.media.MediaMetadataRetriever();
                r.setDataSource(src.getAbsolutePath());
                w = Integer.parseInt(r.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH));
                h = Integer.parseInt(r.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT));
                r.release();
            } catch (Throwable ignored) {
            }
            if (w <= 0 || h <= 0) return;

            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    site.address, site.name, site.collector, w & ~1, h & ~1);
            if (overlay == null) return;
            stage("给视频加水印：" + src.getName());
            WatermarkVideo wv = new WatermarkVideo(overlay, w, h);
            boolean ok = wv.burn(src, out);
            overlay.recycle();
            if (ok && out.exists() && out.length() > 0) {
                String oldPath = m.path;
                m.path = out.getAbsolutePath();
                m.watermarkSrc = oldPath;
            }
        } catch (Throwable ignored) {
        }
    }

'''
    anchor = '    /** 把后加的区域任务登记到服务器，拿回 task_id */'
    assert anchor in s
    s = s.replace(anchor, helper + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Uploader 接线完成')

# Model.Media 加字段
p2 = 'android/src/com/egoops/collect/Model.java'
t = io.open(p2, encoding='utf-8').read()
if 'watermarkSrc' not in t:
    old2 = '        public String state = "local";       // local | uploaded'
    new2 = old2 + '\n        public String watermarkSrc = "";     // 加水印前的原文件路径'
    assert old2 in t
    t = t.replace(old2, new2)
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('Model.Media.watermarkSrc 已加')

# Site 加 collector（水印要用）
if 'public String collector' not in t:
    anchor2 = '        public String name = "";'
    idx = t.find('class Site')
    seg = t[idx:idx + 400]
    if 'collector' not in seg:
        t = t[:idx] + t[idx:].replace('        public String name = "";',
                                      '        public String name = "";\n        public String collector = "";', 1)
        io.open(p2, 'w', encoding='utf-8').write(t)
        print('Model.Site.collector 已加')
