import io

# 1) network security config
open_path = 'android/res/xml/network_security_config.xml'
io.open(open_path, 'w', encoding='utf-8').write('''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- 只信任我们自己这张自签证书，其它 CA 对这台服务器无效（防中间人） -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="false"><FILL_ME></domain>
        <trust-anchors>
            <certificates src="@raw/egoops_cert" />
        </trust-anchors>
    </domain-config>
    <!-- 其它地址（如 https 外网）按系统默认 -->
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
''')
print('network_security_config.xml 写好')

# 2) Manifest 引用
p = 'android/AndroidManifest.xml'
s = io.open(p, encoding='utf-8').read()
if 'networkSecurityConfig' not in s:
    s = s.replace('        android:usesCleartextTraffic="true"',
                  '        android:usesCleartextTraffic="true"\n        android:networkSecurityConfig="@xml/network_security_config"')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('manifest 引用 network config')

# 3) 默认服务器地址换 https
p2 = 'android/src/com/egoops/collect/Store.java'
t = io.open(p2, encoding='utf-8').read()
if 'https://<FILL_ME>/relay' not in t:
    t = t.replace('"http://<FILL_ME>/relay"', '"https://<FILL_ME>/relay"')
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('Store 默认地址改 https')
