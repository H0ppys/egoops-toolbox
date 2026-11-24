"""App：检查更新 + 下载 + 调系统安装器。"""

import io

# ---------- Manifest：安装权限 + provider ----------
p = 'android/AndroidManifest.xml'
s = io.open(p, encoding='utf-8').read()

if 'REQUEST_INSTALL_PACKAGES' not in s:
    s = s.replace('    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />',
'''    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />''')

if 'ApkProvider' not in s:
    s = s.replace('''        <service
            android:name=".UploadService"''', '''        <provider
            android:name=".ApkProvider"
            android:authorities="com.egoops.collect.apk"
            android:exported="false"
            android:grantUriPermissions="true" />

        <service
            android:name=".UploadService"''')

io.open(p, 'w', encoding='utf-8').write(s)
print('manifest: 安装权限 + ApkProvider')

# ---------- MainActivity：检查更新 ----------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

if 'checkUpdate' not in t:
    anchor = '    private void startUpload() {'
    block = r'''    /** 启动时检查有没有新版本 */
    private void checkUpdate() {
        new Thread(() -> {
            try {
                org.json.JSONObject v = api.request("GET", "/api/app/version", null);
                final int code = v.optInt("versionCode", 0);
                final String name = v.optString("versionName", "");
                final String url = v.optString("url", "");
                final String notes = v.optString("notes", "");
                final long size = v.optLong("size", 0);
                if (code <= BuildConfigVersion.CODE || url.isEmpty()) return;
                runOnUiThread(() -> {
                    String msg = "发现新版本 " + name
                            + (size > 0 ? "（" + Math.round(size / 1048576.0 * 10) / 10.0 + "MB）" : "")
                            + (notes.isEmpty() ? "" : "\n\n" + notes)
                            + "\n\n要现在更新吗？";
                    new AlertDialog.Builder(this)
                            .setTitle("有新版本")
                            .setMessage(msg)
                            .setPositiveButton("立即更新", (d, w) -> downloadAndInstall(url))
                            .setNegativeButton("以后再说", null)
                            .show();
                });
            } catch (Exception ignored) {
            }
        }).start();
    }

    /** 下载 APK 并交给系统安装器 */
    private void downloadAndInstall(final String url) {
        toast("开始下载新版本…");
        new Thread(() -> {
            try {
                java.net.HttpURLConnection c = (java.net.HttpURLConnection)
                        new java.net.URL(url).openConnection();
                c.setConnectTimeout(15000);
                c.setReadTimeout(120000);
                c.connect();
                if (c.getResponseCode() >= 300) throw new Exception("HTTP " + c.getResponseCode());
                int total = c.getContentLength();
                java.io.File out = new java.io.File(getCacheDir(), "egoops-update.apk");
                java.io.FileOutputStream fos = new java.io.FileOutputStream(out);
                java.io.InputStream in = c.getInputStream();
                byte[] buf = new byte[64 * 1024];
                int n;
                long done = 0;
                while ((n = in.read(buf)) > 0) {
                    fos.write(buf, 0, n);
                    done += n;
                    if (total > 0) {
                        final int pct = (int) (done * 100 / total);
                        runOnUiThread(() -> {
                            if (tvUpload != null) tvUpload.setText("正在下载新版本 " + pct + "%");
                        });
                    }
                }
                fos.close();
                in.close();
                if (out.length() < 100000) throw new Exception("下载的文件不完整");
                installApk(out);
            } catch (final Exception e) {
                final String msg = e.getMessage() == null ? e.toString() : e.getMessage();
                runOnUiThread(() -> {
                    toast("下载失败：" + msg);
                    if (tvUpload != null) tvUpload.setText("下载失败，点这里重试");
                });
            }
        }).start();
    }

    private void installApk(java.io.File apk) {
        try {
            if (Build.VERSION.SDK_INT >= 26 && !getPackageManager().canRequestPackageInstalls()) {
                runOnUiThread(() -> {
                    toast("请允许安装未知来源应用");
                    try {
                        startActivity(new android.content.Intent(
                                android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                android.net.Uri.parse("package:" + getPackageName())));
                    } catch (Exception ignored) { }
                });
                return;
            }
            android.net.Uri uri = ApkProvider.uriFor(apk.getName());
            android.content.Intent i = new android.content.Intent(android.content.Intent.ACTION_VIEW);
            i.setDataAndType(uri, "application/vnd.android.package-archive");
            i.addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION
                    | android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
            runOnUiThread(() -> {
                try {
                    startActivity(i);
                } catch (Exception e) {
                    toast("打不开安装器：" + e.getMessage());
                }
            });
        } catch (Exception e) {
            runOnUiThread(() -> toast("安装失败：" + e.getMessage()));
        }
    }

'''
    t = t.replace(anchor, block + anchor, 1)

    # onCreate 里触发检查（登录之后再查，避免没网时打扰）
    t = t.replace('''        resumePendingUpload();
        askAllPermissions();''', '''        resumePendingUpload();
        askAllPermissions();
        tvUpload.postDelayed(this::checkUpdate, 3000);''')

    io.open(p2, 'w', encoding='utf-8').write(t)
    print('MainActivity: 检查更新已加')

# ---------- 版本常量 ----------
p3 = 'android/src/com/egoops/collect/BuildConfigVersion.java'
io.open(p3, 'w', encoding='utf-8').write('''package com.egoops.collect;

/** 当前 APK 的版本号，构建时由 build.ps1 改写 */
public class BuildConfigVersion {
    public static final int CODE = 39;
    public static final String NAME = "39.0";
}
''')
print('BuildConfigVersion 已建')
