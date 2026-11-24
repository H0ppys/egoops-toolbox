import io

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

if 'splitAddress' not in s:
    method = r'''    /** 地址断行：第一行尽量排满，在 区/街道/路/号 等处断开 */
    private static java.util.List<String> splitAddress(Paint p, String text, float maxW) {
        java.util.List<String> out = new java.util.ArrayList<>();
        if (text == null) text = "";
        text = text.trim();
        if (text.isEmpty()) {
            out.add("（未获取到定位）");
            return out;
        }
        if (p.measureText(text) <= maxW) {
            out.add(text);
            return out;
        }
        String boundary = "区街道路号镇乡村巷弄段";
        int cut = -1;
        for (int i = 0; i < text.length(); i++) {
            if (boundary.indexOf(text.charAt(i)) < 0) continue;
            String a = text.substring(0, i + 1);
            String b = text.substring(i + 1);
            if (b.isEmpty()) continue;
            if (p.measureText(a) <= maxW && p.measureText(b) <= maxW) {
                cut = i + 1;
            }
        }
        if (cut > 0) {
            out.add(text.substring(0, cut));
            out.add(text.substring(cut));
            return out;
        }
        // 硬断
        StringBuilder cur = new StringBuilder();
        for (char ch : text.toCharArray()) {
            if (cur.length() > 0 && p.measureText(cur.toString() + ch) > maxW) {
                out.add(cur.toString());
                cur = new StringBuilder();
                if (out.size() == 1) break;
            }
            cur.append(ch);
        }
        String rest = text.substring(out.isEmpty() ? 0 : out.get(0).length());
        if (!rest.isEmpty()) out.add(rest);
        return out;
    }

'''
    anchor = '    /** 盾形勾（矢量画，不依赖字体） */'
    assert anchor in s
    s = s.replace(anchor, method + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('splitAddress 已补回')

# 版本号
m = io.open('android/AndroidManifest.xml', encoding='utf-8').read()
m = m.replace('android:versionCode="57"', 'android:versionCode="58"').replace('android:versionName="57.0"', 'android:versionName="58.0"')
io.open('android/AndroidManifest.xml', 'w', encoding='utf-8').write(m)

b = io.open('android/build.ps1', encoding='utf-8').read()
b = b.replace('egoops-collect-v57.apk', 'egoops-collect-v58.apk').replace('--version-code 57 --version-name 57.0', '--version-code 58 --version-name 58.0')
io.open('android/build.ps1', 'w', encoding='utf-8').write(b)
print('版本 58')
