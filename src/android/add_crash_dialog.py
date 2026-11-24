"""1) askTask 点击全程 try/catch，异常只提示不闪退
2) 启动时如果上次崩溃了，把崩溃堆栈弹出来（方便截图发我）
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

# 1) 包住点击逻辑
old = '''        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String a = etAreaName.getText().toString().trim();'''
new = '''        dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            try {
            String a = etAreaName.getText().toString().trim();'''
assert old in s
s = s.replace(old, new)

old2 = '''            } catch (Exception e) {
                toast("打开拍摄页失败：" + e);
            }
        });'''
new2 = '''            } catch (Exception e) {
                toast("打开拍摄页失败：" + e);
            }
            } catch (Exception e) {
                toast("添加区域失败：" + e);
            }
        });'''
assert old2 in s
s = s.replace(old2, new2)

# 2) 启动时显示上次崩溃
if 'showLastCrash' not in s:
    s = s.replace('''        resumePendingUpload();''', '''        showLastCrash();
        resumePendingUpload();''', 1)

    s = s.replace('''    /** 启动时检查有没有新版本 */''', '''    /** 上次崩溃过就弹出来，方便把堆栈发给开发 */
    private void showLastCrash() {
        try {
            java.io.File dir = new java.io.File(getExternalFilesDir(null), "crash");
            if (!dir.exists()) return;
            java.io.File[] files = dir.listFiles();
            if (files == null || files.length == 0) return;
            java.io.File newest = files[0];
            for (java.io.File f : files) if (f.lastModified() > newest.lastModified()) newest = f;
            if (System.currentTimeMillis() - newest.lastModified() > 24L * 3600 * 1000) return;

            byte[] buf = new byte[(int) Math.min(newest.length(), 4000)];
            java.io.FileInputStream in = new java.io.FileInputStream(newest);
            int n = in.read(buf);
            in.close();
            String stack = new String(buf, 0, Math.max(n, 0), "UTF-8");
            String[] lines = stack.split("\\n");
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < Math.min(lines.length, 12); i++) sb.append(lines[i]).append("\\n");

            new AlertDialog.Builder(this)
                    .setTitle("上次运行出错了（可截图发给管理员）")
                    .setMessage(sb.toString())
                    .setPositiveButton("知道了", (d, w) -> newest.delete())
                    .setNegativeButton("关闭", null)
                    .show();
        } catch (Exception ignored) {
        }
    }

    /** 启动时检查有没有新版本 */''')

io.open(P, 'w', encoding='utf-8').write(s)
print('崩溃提示 + askTask 防护 已加')
