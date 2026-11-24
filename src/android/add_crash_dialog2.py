"""加：启动时显示上次崩溃；askTask 点击整体 try/catch。"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) askTask 点击：整体包一层 try/catch（在 dlg.dismiss(); 之后闭合）
old = '''        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String a = etAreaName.getText().toString().trim();'''
new = '''        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            try {
            String a = etAreaName.getText().toString().trim();'''
assert old in s, '找不到点击入口'
s = s.replace(old, new, 1)

old2 = '''            dlg.dismiss();
        });
        if (presetArea != null && !presetArea.isEmpty()) etTaskName.requestFocus();'''
new2 = '''            dlg.dismiss();
            } catch (Exception ex) {
                toast("添加区域失败：" + ex);
            }
        });
        if (presetArea != null && !presetArea.isEmpty()) etTaskName.requestFocus();'''
assert old2 in s, '找不到点击结尾'
s = s.replace(old2, new2, 1)

# 2) 启动时显示上次崩溃
if 'showLastCrash' not in s:
    s = s.replace('''        resumePendingUpload();''', '''        showLastCrash();
        resumePendingUpload();''', 1)

    anchor = '    /** 启动时检查有没有新版本 */'
    assert anchor in s
    block = r'''    /** 上次崩溃过就弹出来，方便把堆栈截图发给管理员 */
    private void showLastCrash() {
        try {
            java.io.File dir = new java.io.File(getExternalFilesDir(null), "crash");
            if (!dir.exists()) return;
            java.io.File[] files = dir.listFiles();
            if (files == null || files.length == 0) return;
            java.io.File newest = files[0];
            for (java.io.File f : files) if (f.lastModified() > newest.lastModified()) newest = f;
            if (System.currentTimeMillis() - newest.lastModified() > 24L * 3600 * 1000) return;

            byte[] buf = new byte[(int) Math.min(newest.length(), 3000)];
            java.io.FileInputStream in = new java.io.FileInputStream(newest);
            int n = in.read(buf);
            in.close();
            String stack = new String(buf, 0, Math.max(n, 0), "UTF-8");
            String[] lines = stack.split("\n");
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < Math.min(lines.length, 12); i++) sb.append(lines[i]).append("\n");

            new AlertDialog.Builder(this)
                    .setTitle("上次运行出错了")
                    .setMessage(sb.toString())
                    .setPositiveButton("知道了", (d, w) -> newest.delete())
                    .setPositiveButton("知道了", null)
                    .show();
        } catch (Exception ignored) {
        }
    }

'''
    s = s.replace(anchor, block + anchor, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('已写入：崩溃弹窗 + askTask 防护')
