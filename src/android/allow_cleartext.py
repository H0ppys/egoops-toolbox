"""放行明文 http（作为 https 失败后的兜底），并把 https 的原始错误带出来。"""

import io

# 1) 网络配置允许对这台服务器的明文 http
p = 'android/res/xml/network_security_config.xml'
io.open(p, 'w', encoding='utf-8').write('''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!--
        这台服务器用自签证书：https 优先，并固定只信任下面这张证书。
        cleartextTrafficPermitted 打开是为了 https 握手失败时能退回 http，
        否则系统会直接报 "Cleartext HTTP traffic not permitted"。
    -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="false"><FILL_ME></domain>
        <trust-anchors>
            <certificates src="@raw/egoops_cert" />
        </trust-anchors>
    </domain-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
''')
print('网络配置：允许明文 http')

# 2) Api：记住 https 的失败原因
p2 = 'android/src/com/egoops/collect/Api.java'
s = io.open(p2, encoding='utf-8').read()

s = s.replace('''    /** https 因为证书/握手失败时，自动退回 http（服务器 80 也开着） */
    private void fallbackToHttp() {
        try {
            if (base.startsWith("https://")) {
                base = "http://" + base.substring(8);
            }
        } catch (Exception ignored) { }
    }''',
'''    /** 上一次 https 失败的原因（给界面显示用） */
    public String lastHttpsError = "";

    /** https 因为证书/握手失败时，自动退回 http（服务器 80 也开着） */
    private void fallbackToHttp(String reason) {
        try {
            lastHttpsError = reason;
            if (base.startsWith("https://")) {
                base = "http://" + base.substring(8);
            }
        } catch (Exception ignored) { }
    }''')

s = s.replace('''        } catch (javax.net.ssl.SSLException e) {
            fallbackToHttp();
            return requestOnce(method, path, body);
        } catch (java.io.IOException e) {
            String msg = String.valueOf(e.getMessage());
            if (base.startsWith("https://") && (msg.contains("SSL") || msg.contains("Trust") || msg.contains("Certificate"))) {
                fallbackToHttp();
                return requestOnce(method, path, body);
            }
            throw e;
        }''',
'''        } catch (javax.net.ssl.SSLException e) {
            fallbackToHttp(String.valueOf(e.getMessage()));
            return requestOnce(method, path, body);
        } catch (java.io.IOException e) {
            String msg = String.valueOf(e.getMessage());
            if (base.startsWith("https://") && (msg.contains("SSL") || msg.contains("Trust") || msg.contains("Certificate"))) {
                fallbackToHttp(msg);
                return requestOnce(method, path, body);
            }
            throw e;
        }''')

io.open(p2, 'w', encoding='utf-8').write(s)
print('Api：记录 https 失败原因')

# 3) 登录成功/失败时把 https 错误提示出来
p3 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p3, encoding='utf-8').read()

t = t.replace('''                api.token = r.optString("token");''',
'''                if (api.lastHttpsError != null && !api.lastHttpsError.isEmpty()) {
                    final String why = api.lastHttpsError;
                    runOnUiThread(() -> toast("https 不通，已自动改用 http（" + why + "）"));
                }
                api.token = r.optString("token");''')

io.open(p3, 'w', encoding='utf-8').write(t)
print('界面：提示已降级')
