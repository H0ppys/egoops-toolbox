"""用「方法体大括号配平」精确替换 useLocation，避免切片顺序错误导致整块重复。"""

import io

p = 'android/src/com/egoops/collect/MainActivity.java'
lines = io.open(p, encoding='utf-8').read().splitlines(True)

# 找到旧 useLocation
sig = [i for i, l in enumerate(lines) if 'private void useLocation(android.location.Location l)' in l]
assert len(sig) == 1, 'useLocation 定义数 = %d' % len(sig)
start = sig[0]

# 找到 body 结束
depth = 0
end = start
for i in range(start, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth == 0 and i > start:
        end = i
        break

new = r'''    /** 坐标 → GCJ02 → 高德逆地理 → 真实地址；同时抓一张对应地图 */
    private void useLocation(android.location.Location l) {
        try {
            final double lat = l.getLatitude();
            final double lon = l.getLongitude();
            final float acc = l.getAccuracy();
            gpsCoords = String.format("%.6f, %.6f", lat, lon);

            // 手机给的是 WGS84，高德用 GCJ02，必须转换，否则红点会偏几百米
            final double[] gcj = Geo.wgs84ToGcj02(lat, lon);
            final String key = MapSnap.DEFAULT_KEY;

            new Thread(() -> {
                String text = Geo.regeo(key, gcj[0], gcj[1]);
                if (text == null || text.isEmpty()) {
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
                    text = "定位 " + gpsCoords;
                }
                if (acc > 100) {
                    text = text + "（精度约" + Math.round(acc) + "米）";
                }
                gpsAddress = text;

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

lines[start:end + 1] = [new]
io.open(p, 'w', encoding='utf-8').write(''.join(lines))
print('useLocation 已替换（行 %d-%d）' % (start + 1, end + 1))
