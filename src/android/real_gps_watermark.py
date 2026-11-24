"""水印改成真实定位：
   · 加定位权限，启动时取一次 GPS/网络定位，反查成地址
   · 水印里只放「打卡时间 + 真实地址 + 日期」，不再放门店名/采集员
   · 定位不可用时退回自填地址，并标注「自填」
"""

import io

# ---------------- 1) AndroidManifest 权限 ----------------
p = 'android/AndroidManifest.xml'
s = io.open(p, encoding='utf-8').read()
if 'ACCESS_FINE_LOCATION' not in s:
    old = '<uses-permission android:name="android.permission.CAMERA" />'
    if old in s:
        s = s.replace(old, old + '\n    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />'
                                + '\n    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />')
        io.open(p, 'w', encoding='utf-8').write(s)
        print('manifest: 定位权限已加')
    else:
        print('manifest: 找不到 CAMERA 权限行，请手动确认')

# ---------------- 2) MainActivity ----------------
P = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(P, encoding='utf-8').read()

# 2.1 字段
if 'gpsAddress' not in t:
    t = t.replace('    private String lastSceneInvite = "";',
                  '    private String lastSceneInvite = "";\n    private volatile String gpsAddress = "";\n    private volatile String gpsCoords = "";')

# 2.2 取定位 + 反查地址
if 'private void startGps()' not in t:
    anchor = '    private void askTask(String presetArea) {'
    block = r'''    /** 取一次真实定位，反查成文字地址（水印用） */
    private void startGps() {
        try {
            final android.location.LocationManager lm =
                    (android.location.LocationManager) getSystemService(LOCATION_SERVICE);
            if (lm == null) return;
            android.location.Location best = null;
            for (String pv : new String[]{android.location.LocationManager.GPS_PROVIDER,
                    android.location.LocationManager.NETWORK_PROVIDER}) {
                try {
                    android.location.Location l = lm.getLastKnownLocation(pv);
                    if (l == null) continue;
                    if (best == null || l.getTime() > best.getTime()) best = l;
                } catch (Exception ignored) {}
            }
            if (best != null) useLocation(best);

            final android.location.LocationListener[] holder = new android.location.LocationListener[1];
            android.location.LocationListener listener = new android.location.LocationListener() {
                @Override public void onLocationChanged(android.location.Location l) {
                    useLocation(l);
                    try { lm.removeUpdates(holder[0]); } catch (Exception ignored) {}
                }
                @Override public void onStatusChanged(String p, int s, android.os.Bundle b) {}
                @Override public void onProviderEnabled(String p) {}
                @Override public void onProviderDisabled(String p) {}
            };
            holder[0] = listener;
            try {
                lm.requestLocationUpdates(android.location.LocationManager.NETWORK_PROVIDER, 0, 0, listener);
            } catch (Exception ignored) {}
            try {
                lm.requestLocationUpdates(android.location.LocationManager.GPS_PROVIDER, 0, 0, listener);
            } catch (Exception ignored) {}
        } catch (Exception ignored) {
        }
    }

    /** 把坐标反查成「省市区街道」，失败就退成经纬度 */
    private void useLocation(android.location.Location l) {
        try {
            double lat = l.getLatitude(), lon = l.getLongitude();
            final String coords = String.format("%.5f, %.5f", lat, lon);
            gpsCoords = coords;
            final android.location.Geocoder gc = new android.location.Geocoder(this, java.util.Locale.CHINA);
            new Thread(() -> {
                String text = "";
                try {
                    java.util.List<android.location.Address> list = gc.getFromLocation(lat, lon, 1);
                    if (list != null && !list.isEmpty()) {
                        android.location.Address a = list.get(0);
                        StringBuilder sb = new StringBuilder();
                        if (a.getAdminArea() != null) sb.append(a.getAdminArea());
                        if (a.getLocality() != null) sb.append(a.getLocality());
                        if (a.getSubLocality() != null) sb.append(a.getSubLocality());
                        if (a.getThoroughfare() != null) sb.append(a.getThoroughfare());
                        if (a.getSubThoroughfare() != null) sb.append(a.getSubThoroughfare());
                        text = sb.toString().replace(" ", "");
                    }
                } catch (Exception ignored) {
                }
                gpsAddress = text.isEmpty() ? ("定位 " + coords) : text;
            }).start();
        } catch (Exception ignored) {
        }
    }

'''
    assert anchor in t
    t = t.replace(anchor, block + anchor, 1)

# 2.3 权限申请里带上定位
t = t.replace('new String[]{Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO}',
              'new String[]{Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO, Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}')

# 2.4 开始拍摄时启动定位
t = t.replace('        if (api.token.isEmpty()) autoLogin();',
              '        startGps();\n        if (api.token.isEmpty()) autoLogin();')

# 2.5 水印内容：真实定位优先，去掉门店/采集员
old = '''            String addr = (site.address == null || site.address.trim().isEmpty()) ? "（未填地址）" : site.address.trim();
            String store = site.name == null ? "" : site.name.trim();
            String who = (etCollector == null || etCollector.getText() == null) ? "" : etCollector.getText().toString().trim();'''
new = '''            String gps = gpsAddress == null ? "" : gpsAddress.trim();
            String addr = gps.isEmpty()
                    ? ((site.address == null || site.address.trim().isEmpty()) ? "（未填地址）" : site.address.trim() + "（自填）")
                    : gps;'''
assert old in t
t = t.replace(old, new)

t = t.replace('''            String bottom = date + " " + week + (store.isEmpty() ? "" : "  " + store)
                    + (who.isEmpty() ? "" : "  " + who);''',
'''            String bottom = date + " " + week;''')

io.open(P, 'w', encoding='utf-8').write(t)
print('MainActivity: 真实定位 + 水印只留地址/时间')

# ---------------- 3) 视频水印（同规则） ----------------
p3 = 'android/src/com/egoops/collect/WatermarkVideo.java'
w = io.open(p3, encoding='utf-8').read()
w = w.replace('''            String bottom = date + " " + week
                    + (store == null || store.isEmpty() ? "" : "  " + store)
                    + (who == null || who.isEmpty() ? "" : "  " + who);
            c.drawText(bottom, x, y + 8 * u, p);''',
'''            String bottom = date + " " + week;
            c.drawText(bottom, x, y + 8 * u, p);''')
io.open(p3, 'w', encoding='utf-8').write(w)

# Uploader 传真实地址
p4 = 'android/src/com/egoops/collect/Uploader.java'
u = io.open(p4, encoding='utf-8').read()
u = u.replace('''            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    site.address, site.name, site.collector, w & ~1, h & ~1);''',
'''            String wmAddr = site.wmAddress == null || site.wmAddress.isEmpty() ? site.address : site.wmAddress;
            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1);''')
io.open(p4, 'w', encoding='utf-8').write(u)

# Model.Site 加 wmAddress
p5 = 'android/src/com/egoops/collect/Model.java'
m = io.open(p5, encoding='utf-8').read()
if 'wmAddress' not in m:
    m = m.replace('        public String collector = "";', '        public String collector = "";\n        public String wmAddress = "";')
    io.open(p5, 'w', encoding='utf-8').write(m)
    print('Model.Site.wmAddress 已加')

print('完成')
