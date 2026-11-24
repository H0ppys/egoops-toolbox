"""把水印用的真实地址存进 site.wmAddress，并随队列持久化。"""

import io

# Model：序列化 wmAddress
p = 'android/src/com/egoops/collect/Model.java'
s = io.open(p, encoding='utf-8').read()
if 'wmAddress' in s and 'o.put("wm_address"' not in s:
    s = s.replace('        o.put("invite", invite);', '        o.put("invite", invite);\n        o.put("wm_address", wmAddress);')
    s = s.replace('        invite = o.optString("invite");', '        invite = o.optString("invite");\n        s.wmAddress = o.optString("wm_address");')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Model: wmAddress 序列化')

# MainActivity：拍到素材时把当前定位写进 site
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()
if 'site.wmAddress = gpsAddress' not in t:
    old = '''            if (!video) stampWatermark(dest);'''
    new = '''            if (gpsAddress != null && !gpsAddress.trim().isEmpty()) {
                site.wmAddress = gpsAddress.trim();
                store.saveQueue(site);
            }
            if (!video) stampWatermark(dest);'''
    assert old in t
    t = t.replace(old, new)
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('MainActivity: 记录真实地址')
