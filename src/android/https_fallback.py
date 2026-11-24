"""https 连不上时自动退回 http，并把真实错误显示出来，方便定位。"""

import io

# ---------------- Api.java：https 失败自动降级 ----------------
p = 'android/src/com/egoops/collect/Api.java'
s = io.open(p, encoding='utf-8').read()

if 'fallbackToHttp' not in s:
    s = s.replace('''    private HttpURLConnection open(String method, String path, String contentType) throws Exception {
        URL url = new URL(base + path);''',
'''    /** https 因为证书/握手失败时，自动退回 http（服务器 80 也开着） */
    private void fallbackToHttp() {
        try {
            if (base.startsWith("https://")) {
                base = "http://" + base.substring(8);
            }
        } catch (Exception ignored) { }
    }

    private HttpURLConnection open(String method, String path, String contentType) throws Exception {
        URL url = new URL(base + path);''')

    s = s.replace('''    public JSONObject request(String method, String path, JSONObject body) throws Exception {
        HttpURLConnection c = open(method, path, body == null ? null : "application/json; charset=utf-8");''',
'''    public JSONObject request(String method, String path, JSONObject body) throws Exception {
        try {
            return requestOnce(method, path, body);
        } catch (javax.net.ssl.SSLException e) {
            fallbackToHttp();
            return requestOnce(method, path, body);
        } catch (java.io.IOException e) {
            String msg = String.valueOf(e.getMessage());
            if (base.startsWith("https://") && (msg.contains("SSL") || msg.contains("Trust") || msg.contains("Certificate"))) {
                fallbackToHttp();
                return requestOnce(method, path, body);
            }
            throw e;
        }
    }

    public JSONObject requestOnce(String method, String path, JSONObject body) throws Exception {
        HttpURLConnection c = open(method, path, body == null ? null : "application/json; charset=utf-8");''')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('Api: https → http 自动降级')

# ---------------- MainActivity：错误文本带上原因 ----------------
p2 = 'android/src/com/egoops/collect/MainActivity.java'
t = io.open(p2, encoding='utf-8').read()

t = t.replace('''                runOnUiThread(() -> {
                    if (tvUpload != null) {
                        tvUpload.setText("没连上服务器，点这里重试");
                        tvUpload.setTextColor(DANGER);
                    }
                });''',
'''                final String reason = (e.getMessage() == null ? e.toString() : e.getMessage());
                runOnUiThread(() -> {
                    if (tvUpload != null) {
                        tvUpload.setText("没连上服务器：" + reason + "（点这里重试）");
                        tvUpload.setTextColor(DANGER);
                    }
                });''')

t = t.replace('''                    runOnUiThread(() -> {
                        tvUpload.setText("没连上服务器，点这里重试");
                        tvUpload.setTextColor(DANGER);
                    });''',
'''                    final String reason2 = (e.getMessage() == null ? e.toString() : e.getMessage());
                    runOnUiThread(() -> {
                        tvUpload.setText("没连上服务器：" + reason2 + "（点这里重试）");
                        tvUpload.setTextColor(DANGER);
                    });''')

io.open(p2, 'w', encoding='utf-8').write(t)
print('MainActivity: 显示真实错误')
