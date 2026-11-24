"""「不拍摄收集」版加一键调用水印相机：
   · 扫描已安装应用里名字带「水印」的（今日水印相机等）
   · 点按钮直接打开它；回到本 App 时自动弹出相册选择
   · 找不到就提示去应用商店装
"""

import io

# ---------- 清单：允许查询已安装应用 ----------
p = 'android/AndroidManifest.xml'
s = io.open(p, encoding='utf-8').read()
if 'QUERY_ALL_PACKAGES' not in s:
    old = '<uses-permission android:name="android.permission.CAMERA" />'
    s = s.replace(old, old + '\n    <uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('清单：QUERY_ALL_PACKAGES')

# ---------- MainActivity ----------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

if 'openWatermarkCamera' not in t:
    # 1) 增加状态字段
    t = t.replace('    private volatile java.io.File mapSnapFile = null;',
                  '    private volatile java.io.File mapSnapFile = null;\n    private boolean awaitingWatermarkImport = false;')

    # 2) 拍照区：不拍版加「打开水印相机」按钮
    t = t.replace('''        Button pick = secondaryButton(pickText, BuildConfigVersion.NO_CAPTURE ? 64 : 54);''',
'''        if (BuildConfigVersion.NO_CAPTURE) {
            Button openWm = secondaryButton("① 打开水印相机去拍", 60);
            openWm.setOnClickListener(v -> openWatermarkCamera(key, kind));
            LinearLayout.LayoutParams wlp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(60));
            wlp.topMargin = dp(10);
            card.addView(openWm, wlp);

            TextView tip2 = new TextView(this);
            tip2.setText("拍完按返回，会自动让你从相册里选刚拍的那张");
            tip2.setTextSize(13);
            tip2.setTextColor(MUTED);
            tip2.setGravity(Gravity.CENTER);
            tip2.setPadding(0, dp(8), 0, dp(2));
            card.addView(tip2);
        }

        Button pick = secondaryButton(pickText, BuildConfigVersion.NO_CAPTURE ? 64 : 54);''')

    # 3) 实现：找带「水印」的应用并打开
    anchor = '    /** 从相册选已有照片/视频 */'
    block = '''    /** 打开已安装的水印相机（名字里带「水印」），回来后自动弹相册 */
    private void openWatermarkCamera(String shot, String kind) {
        pendingShot = shot;
        String found = null;
        try {
            android.content.pm.PackageManager pm = getPackageManager();
            java.util.List<android.content.pm.ApplicationInfo> apps =
                    pm.getInstalledApplications(android.content.pm.PackageManager.GET_META_DATA);
            for (android.content.pm.ApplicationInfo ai : apps) {
                String label = String.valueOf(pm.getApplicationLabel(ai));
                if (label.contains("水印")) {
                    android.content.Intent it = pm.getLaunchIntentForPackage(ai.packageName);
                    if (it != null) {
                        found = ai.packageName;
                        startActivity(it);
                        awaitingWatermarkImport = true;
                        toast("拍完返回这里，会自动让你选照片");
                        break;
                    }
                }
            }
        } catch (Throwable ignored) {
        }
        if (found == null) {
            new AlertDialog.Builder(this)
                    .setTitle("没找到水印相机")
                    .setMessage("手机里没装名字带「水印」的相机 App。\\n\\n可以先去应用商店装「今日水印相机」，再回来点这个按钮。")
                    .setPositiveButton("去应用商店", (d, w) -> {
                        try {
                            startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,
                                    android.net.Uri.parse("market://search?q=今日水印相机")));
                        } catch (Throwable e) {
                            toast("请手动打开应用商店搜索「今日水印相机」");
                        }
                    })
                    .setNegativeButton("知道了", null)
                    .show();
        }
    }

'''
    assert anchor in t
    t = t.replace(anchor, block + anchor, 1)

    # 4) onResume：从水印相机回来后自动弹相册
    if 'protected void onResume' not in t:
        t = t.replace('''    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {''',
'''    @Override
    protected void onResume() {
        super.onResume();
        if (awaitingWatermarkImport) {
            awaitingWatermarkImport = false;
            String kind = (pendingShot != null && pendingShot.toLowerCase().contains("video")) ? "video" : "photo";
            final String shot = pendingShot;
            if (shot != null && !shot.isEmpty()) {
                tvStep.postDelayed(() -> {
                    toast("请选刚拍好的那张");
                    pickShot(shot, kind);
                }, 400);
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {''')

    io.open(p2, 'w', encoding='utf-8').write(t)
    print('MainActivity：一键打开水印相机 + 回来自动选图')
