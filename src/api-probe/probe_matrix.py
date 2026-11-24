import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
URL = "https://egoops.meituan.com/api/v1/recordings?page=1&size=2"

variants = {
    "仅 Bearer": {"Authorization": f"Bearer {TOKEN}"},
    "Bearer+Referer": {
        "Authorization": f"Bearer {TOKEN}",
        "Referer": "https://egoops.meituan.com/recordings",
        "Origin": "https://egoops.meituan.com",
    },
    "Bearer+XHR+Accept": {
        "Authorization": f"Bearer {TOKEN}",
        "Referer": "https://egoops.meituan.com/recordings",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN",
    },
    "无 Bearer": {"Referer": "https://egoops.meituan.com/recordings"},
}

for name, extra in variants.items():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/143.0 Safari/537.36"}
    headers.update(extra)
    req = urllib.request.Request(URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            ct = r.headers.get("Content-Type", "")
            print(f"[{name}] status={r.status} ct={ct} len={len(body)}")
            if "json" in ct:
                print("   ", body[:400])
    except urllib.error.HTTPError as e:
        print(f"[{name}] HTTP {e.code}: {e.read()[:200]}")
    except Exception as e:
        print(f"[{name}] ERROR {e}")
