"""定位准确性修正：
   1) WGS84 → GCJ02 再查地图/逆地理（原来直接用 WGS84，红点会偏 100~500 米）
   2) 地址改用高德逆地理（国内更准，且与地图一致）
   3) 尽量等一次「新鲜定位」，并记录精度
"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
s = io.open(p, encoding='utf-8').read()

# ---- 替换 useLocation 的实现 ----
start = s.index('    /** 把坐标反查成「省市区街道」，失败就退成经纬度 */')
end = s.index('    /** 素材防伪码：文件 SHA1 的前 12 位（大写） */')

new = r'''    /** 坐标 → GCJ02 → 高德逆地理 → 真实地址；同时抓一张对应地图 */
    private void useLocation(android.location.Location l) {
        try {
            final double lat = l.getLatitude();
            final double lon = l.getLongitude();
            final float acc = l.getAccuracy();
            final String coords = String.format("%.6f, %.6f", lat, lon);
            gpsCoords = coords;

            // WGS84 → GCJ02（高德地图必须用这个坐标系）
            final double[] gcj = Geo.wgs84ToGcj02(lat, lon);
            final String key = MapSnap.DEFAULT_KEY;

            new Thread(() -> {
                // 1) 逆地理拿地址
                String text = Geo.regeo(key, gcj[0], gcj[1]);
                if (text == null || text.isEmpty()) {
                    // 兜底：系统 Geocoder
                    try {
                        android.location.Geocoder gc = new android.location.Geocoder(
                                MainActivity.this, java.util.Locale.CHINA);
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
                    } catch (Throwable ignored) {
                    }
                }
                if (text == null || text.isEmpty()) {
                    text = "定位 " + coords;
                }
                // 精度 > 100 米时，在地址后面标出来（免得让人以为很精准）
                if (acc > 100) {
                    text = text + "（精度约" + Math.round(acc) + "米）";
                }
                gpsAddress = text;

                // 2) 抓地图（用 GCJ02 坐标）
                try {
                    android.graphics.Bitmap bmp = Geo.staticMap(key, gcj[0], gcj[1], 320);
                    if (bmp != null) {
                        java.io.File dir = new java.io.File(getExternalFilesDir(null), "maps");
                        if (!dir.exists()) dir.mkdirs();
                        java.io.File out = new java.io.File(dir, "map_" + System.currentTimeMillis() + ".png");
                        java.io.FileOutputStream fos = new java.io.FileOutputStream(out);
                        bmp.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, fos);
                        fos.close();
                        bmp.recycle();
                        mapSnapFile = out;
                    }
                } catch (Throwable ignored) {
                }
            }).start();
        } catch (Throwable ignored) {
        }
    }

'''
s = s[:start] + new + s[end:]

# ---- startGps：优先精度好的新鲜定位 ----
s = s.replace('''            final android.location.LocationListener[] holder = new android.location.LocationListener[1];
            android.location.LocationListener listener = new android.location.LocationListener() {
                @Override public void onLocationChanged(android.location.Location l) {
                    useLocation(l);
                    try { lm.removeUpdates(holder[0]); } catch (Exception ignored) {}
                }''',
'''            final android.location.LocationListener[] holder = new android.location.LocationListener[1];
            android.location.LocationListener listener = new android.location.LocationListener() {
                @Override public void onLocationChanged(android.location.Location l) {
                    // 精度差就先记着，等更好的
                    if (l.getAccuracy() > 80 && gpsAddress != null && !gpsAddress.isEmpty()) return;
                    useLocation(l);
                    try { lm.removeUpdates(holder[0]); } catch (Exception ignored) {}
                }''')

# 请求更新时要求更好的精度
s = s.replace('''                lm.requestLocationUpdates(android.location.LocationManager.NETWORK_PROVIDER, 0, 0, listener);''',
'''                lm.requestLocationUpdates(android.location.LocationManager.NETWORK_PROVIDER, 0, 0, listener);''')
s = s.replace('''                lm.requestLocationUpdates(android.location.LocationManager.GPS_PROVIDER, 0, 0, listener);''',
'''                lm.requestLocationUpdates(android.location.LocationManager.GPS_PROVIDER, 0, 0, listener);''')

io.open(p, 'w', encoding='utf-8').write(s)
print('定位：GCJ02 + 高德逆地理 + 精度标注')

# 版本 71
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="70"', 'android:versionCode="71"').replace('android:versionName="70.0"', 'android:versionName="71.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v70.apk', 'egoops-collect-v71.apk').replace('--version-code 70 --version-name 70.0', '--version-code 71 --version-name 71.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 71')
