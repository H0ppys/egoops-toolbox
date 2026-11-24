import io

p = 'android/src/com/egoops/collect/WatermarkVideo.java'
s = io.open(p, encoding='utf-8').read()

if 'private static java.util.List<String> splitAddress' in s:
    print('已存在方法定义')
else:
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
            if (p.measureText(a) <= maxW && p.measureText(b) <= maxW) cut = i + 1;
        }
        if (cut > 0) {
            out.add(text.substring(0, cut));
            out.add(text.substring(cut));
            return out;
        }
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
    anchor = '    /** 生成和视频同尺寸的透明水印图层 */'
    assert anchor in s, 'anchor missing'
    s = s.replace(anchor, method + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('splitAddress 已插入')
