"""把地图小图接进照片/视频水印：
   · 定位拿到后抓一张高德静态地图，缓存成本地文件
   · 照片烧水印时贴右上角
   · 视频 overlay 也贴（Uploader 读缓存文件）
"""

import io

# ---------- 1) WatermarkVideo.drawStamp 增加地图参数 ----------
p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

s = s.replace('    public static void drawStamp(Canvas c, int w, int h, String addr, long whenMs, String antiCode) {',
              '    public static void drawStamp(Canvas c, int w, int h, String addr, long whenMs, String antiCode, Bitmap map) {')
s = s.replace('    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h, long whenMs, String antiCode) {',
              '    public static Bitmap makeOverlay(String addr, String store, String who, int w, int h, long whenMs, String antiCode, Bitmap map) {')
s = s.replace('            drawStamp(c, w, h, addr, whenMs, antiCode);',
              '            drawStamp(c, w, h, addr, whenMs, antiCode, map);')

# 在方法末尾（防伪码之后）画地图
s = s.replace('''            String line = "防伪 " + antiCode;
            float cw = code.measureText(line);
            c.drawText(line, w - margin - cw, h - margin * 0.55f, code);
        }
    }''',
'''            String line = "防伪 " + antiCode;
            float cw = code.measureText(line);
            c.drawText(line, w - margin - cw, h - margin * 0.55f, code);
        }

        MapSnap.draw(c, map, w, h, margin);
    }''')

io.open(p, 'w', encoding='utf-8').write(s)
print('WatermarkVideo: 地图参数')

# ---------- 2) MainActivity ----------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
a = io.open(p2, encoding='utf-8').read()

if 'mapSnapFile' not in a:
    a = a.replace('    private volatile String gpsCoords = "";',
                  '    private volatile String gpsCoords = "";\n    private volatile java.io.File mapSnapFile = null;')

    # 定位成功后抓地图
    a = a.replace('''                gpsAddress = text.isEmpty() ? ("定位 " + coords) : text;''',
'''                gpsAddress = text.isEmpty() ? ("定位 " + coords) : text;

                // 顺手抓一张附近地图（给水印右上角用）
                try {
                    java.io.File dir = new java.io.File(getExternalFilesDir(null), "maps");
                    if (!dir.exists()) dir.mkdirs();
                    String key = store.get("map_key", MapSnap.DEFAULT_KEY);
                    java.io.File f = MapSnap.fetch(key, lat, lon, 320, dir);
                    if (f != null) mapSnapFile = f;
                } catch (Throwable ignored) {
                }''')

    # 照片水印：贴地图
    a = a.replace('            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr, whenMs, antiCode);',
'''            android.graphics.Bitmap map = null;
            try {
                if (mapSnapFile != null && mapSnapFile.exists()) {
                    map = android.graphics.BitmapFactory.decodeFile(mapSnapFile.getAbsolutePath());
                }
            } catch (Throwable ignored) {
            }
            WatermarkVideo.drawStamp(c, bmp.getWidth(), bmp.getHeight(), addr, whenMs, antiCode, map);''')

io.open(p2, 'w', encoding='utf-8').write(a)
print('MainActivity: 定位后抓图 + 照片贴图')

# ---------- 3) Uploader：视频贴地图 ----------
p3 = 'android/src/com/egoops/collect/Uploader.java'
u = io.open(p3, encoding='utf-8').read()
u = u.replace('''            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1, when, code);''',
'''            android.graphics.Bitmap map = null;
            try {
                java.io.File dir = new java.io.File(src.getParentFile().getParentFile(), "maps");
                java.io.File[] maps = dir.listFiles();
                if (maps != null && maps.length > 0) {
                    java.io.File newest = maps[0];
                    for (java.io.File f : maps) if (f.lastModified() > newest.lastModified()) newest = f;
                    if (System.currentTimeMillis() - newest.lastModified() < 6L * 3600 * 1000) {
                        map = android.graphics.BitmapFactory.decodeFile(newest.getAbsolutePath());
                    }
                }
            } catch (Throwable ignored) {
            }
            android.graphics.Bitmap overlay = WatermarkVideo.makeOverlay(
                    wmAddr, "", "", w & ~1, h & ~1, when, code, map);''')
io.open(p3, 'w', encoding='utf-8').write(u)
print('Uploader: 视频贴地图')

# ---------- 4) Store.get/set 支持 map_key ----------
p4 = 'android/src/com/egoops/collect/Store.java'
st = io.open(p4, encoding='utf-8').read()
if 'public String get(' not in st:
    st = st.replace('    public String vendor()', '''    public String get(String k, String def) { return sp.getString(k, def); }
    public void put(String k, String v) { sp.edit().putString(k, v).apply(); }

    public String vendor()''')
    io.open(p4, 'w', encoding='utf-8').write(st)
    print('Store: get/put')

# 版本 67
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="66"', 'android:versionCode="67"').replace('android:versionName="66.0"', 'android:versionName="67.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)
b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v66.apk', 'egoops-collect-v67.apk').replace('--version-code 66 --version-name 66.0', '--version-code 67 --version-name 67.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 67')
