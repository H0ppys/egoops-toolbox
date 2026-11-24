"""水印相机跳转更可靠：
   1) 先按已知包名找（今日水印相机等常见包名）
   2) 再按名字含「水印 / Watermark」找
   3) 还找不到就列出手机里所有相机类 App 让用户点一次，记住选择
"""

import io

P = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(P, encoding='utf-8').read()

start = s.index('    /** 打开已安装的水印相机（名字里带「水印」），回来后自动弹相册 */')
end = s.index('    /** 从水印相机回来：自动抓「比打开时刻更新」的最新一张/一段 */')

new = r'''    /** 已知的水印相机包名（按顺序尝试） */
    private static final String[] WM_PACKAGES = {
            "com.chanjikeji.watermarkcamera",
            "com.chanjikeji.todaywatermark",
            "com.chanjikeji.watermark",
            "com.todaywatermark.camera",
            "com.watermark.camera",
            "com.tencent.watermark",
            "com.yuandao.camera",
            "com.kkmh.watermark",
    };

    /** 打开水印相机：已知包名 → 名字含「水印」 → 让用户从相机类 App 里选一次 */
    private void openWatermarkCamera(String shot, String kind) {
        pendingShot = shot;
        android.content.pm.PackageManager pm = getPackageManager();

        // 0) 上次选过的
        String saved = store.get("wm_pkg", "");
        if (!saved.isEmpty()) {
            try {
                android.content.Intent it = pm.getLaunchIntentForPackage(saved);
                if (it != null) {
                    launchWm(it);
                    return;
                }
            } catch (Throwable ignored) {
            }
        }

        // 1) 已知包名
        for (String pkg : WM_PACKAGES) {
            try {
                android.content.Intent it = pm.getLaunchIntentForPackage(pkg);
                if (it != null) {
                    store.put("wm_pkg", pkg);
                    launchWm(it);
                    return;
                }
            } catch (Throwable ignored) {
            }
        }

        // 2) 名字含「水印 / Watermark」
        java.util.List<String[]> cams = new java.util.ArrayList<>();
        java.util.List<String[]> named = new java.util.ArrayList<>();
        try {
            java.util.List<android.content.pm.ApplicationInfo> apps =
                    pm.getInstalledApplications(android.content.pm.PackageManager.GET_META_DATA);
            for (android.content.pm.ApplicationInfo ai : apps) {
                String label = String.valueOf(pm.getApplicationLabel(ai));
                if (pm.getLaunchIntentForPackage(ai.packageName) == null) continue;
                boolean isCam = label.contains("相机") || label.contains("摄像") || label.contains("Watermark")
                        || label.contains("水印") || label.toLowerCase().contains("camera");
                if (!isCam) continue;
                cams.add(new String[]{label, ai.packageName});
                if (label.contains("水印") || label.contains("Watermark")) {
                    named.add(new String[]{label, ai.packageName});
                }
            }
        } catch (Throwable ignored) {
        }

        if (named.size() == 1) {
            store.put("wm_pkg", named.get(0)[1]);
            android.content.Intent it = pm.getLaunchIntentForPackage(named.get(0)[1]);
            if (it != null) {
                launchWm(it);
                return;
            }
        }

        // 3) 让用户选一次（水印类排前面）
        java.util.List<String[]> show = new java.util.ArrayList<>();
        show.addAll(named);
        for (String[] c : cams) {
            boolean dup = false;
            for (String[] x : show) if (x[1].equals(c[1])) dup = true;
            if (!dup) show.add(c);
        }

        if (show.isEmpty()) {
            new AlertDialog.Builder(this)
                    .setTitle("没找到水印相机")
                    .setMessage("手机里没装名字带「水印」的相机 App。\n\n可以先去应用商店装「今日水印相机」，再回来点这个按钮。")
                    .setPositiveButton("去应用商店", (d, w) -> {
                        try {
                            startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,
                                    android.net.Uri.parse("market://search?q=今日水印相机")));
                        } catch (Throwable e) {
                            try {
                                startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW,
                                        android.net.Uri.parse("https://sj.qq.com/appdetail/com.tencent.tmgp.sgame")));
                            } catch (Throwable ignored) {
                                toast("请手动打开应用商店搜索「今日水印相机」");
                            }
                        }
                    })
                    .setNegativeButton("知道了", null)
                    .show();
            return;
        }

        String[] items = new String[show.size()];
        for (int i = 0; i < show.size(); i++) {
            items[i] = show.get(i)[0];
        }
        new AlertDialog.Builder(this)
                .setTitle("用哪个 App 拍？")
                .setItems(items, (d, which) -> {
                    String pkg = show.get(which)[1];
                    store.put("wm_pkg", pkg);
                    try {
                        android.content.Intent it = pm.getLaunchIntentForPackage(pkg);
                        if (it != null) launchWm(it);
                    } catch (Throwable ignored) {
                    }
                })
                .setNegativeButton("取消", null)
                .show();
    }

    /** 真正跳转，并记下开始时间（回来后自动抓文件） */
    private void launchWm(android.content.Intent it) {
        try {
            startActivity(it);
            wmLaunchAt = System.currentTimeMillis();
            awaitingWatermarkImport = true;
            toast("拍完按返回，会自动取回刚拍的");
        } catch (Throwable e) {
            toast("打不开这个应用：" + e);
        }
    }

'''
s = s[:start] + new + s[end:]
io.open(P, 'w', encoding='utf-8').write(s)
print('水印相机跳转逻辑重写')
