import json
import urllib.parse
import urllib.request

TOKEN = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_token.json", encoding="utf-8"))["access_token"]
BASE = "https://egoops.meituan.com"


def get(path, params=None, raw=False):
    url = BASE + path
    if params:
        url += ("&" if "?" in path else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"ERROR {e}"


for label, path, params in [
    ("stats", "/api/v1/recordings/stats", {}),
    ("recordings p1", "/api/v1/recordings", {"page": 1, "size": 3}),
]:
    status, body = get(path, params)
    print(f"\n===== {label} ===== status={status} len={len(body)}")
    print(body[:1800])
