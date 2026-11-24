import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

feishu = '''
# ---------------------------------------------------------------- 飞书开放接口（免 lark-cli）
class Feishu:
    """直接调用飞书 OpenAPI，只需 App ID + App Secret，便于换机便携使用。"""

    OPEN = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id, app_secret, base_token, table_id, timeout=60):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_token = base_token
        self.table_id = table_id
        self.timeout = timeout
        self._token = None
        self._exp = 0

    def _req(self, method, url, payload=None, headers=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        h = {"Content-Type": "application/json; charset=utf-8"}
        h.update(headers or {})
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
        if body.get("code") not in (0, None):
            raise RuntimeError(f"飞书接口错误 code={body.get('code')} msg={body.get('msg')}")
        return body

    def token(self):
        if self._token and self._exp - time.time() > 120:
            return self._token
        body = self._req("POST", f"{self.OPEN}/auth/v3/tenant_access_token/internal",
                         {"app_id": self.app_id, "app_secret": self.app_secret})
        self._token = body["tenant_access_token"]
        self._exp = time.time() + int(body.get("expire", 7200))
        return self._token

    def _hdr(self):
        return {"Authorization": f"Bearer {self.token()}"}

    def _records_url(self, suffix=""):
        return f"{self.OPEN}/bitable/v1/apps/{self.base_token}/tables/{self.table_id}/records{suffix}"

    def list_ids(self):
        ids = []
        page_token = None
        while True:
            q = {"page_size": "500"}
            if page_token:
                q["page_token"] = page_token
            url = self._records_url() + "?" + urllib.parse.urlencode(q)
            body = self._req("GET", url, headers=self._hdr())
            data = body.get("data") or {}
            for it in data.get("items") or []:
                ids.append(it.get("record_id"))
            page_token = data.get("page_token")
            if not data.get("has_more"):
                break
        return [i for i in ids if i]

    def batch_delete(self, ids):
        n = 0
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            self._req("POST", self._records_url("/batch_delete"),
                      {"records": chunk}, headers=self._hdr())
            n += len(chunk)
        return n

    def batch_create(self, records):
        n = 0
        for i in range(0, len(records), 500):
            chunk = records[i:i + 500]
            payload = {"records": [{"fields": r} for r in chunk]}
            self._req("POST", self._records_url("/batch_create"), payload, headers=self._hdr())
            n += len(chunk)
        return n


def to_feishu_fields(row):
    """把行数据转成飞书 CellValue（datetime 用毫秒时间戳）。"""
    out = {}
    for k, v in row.items():
        if k == "更新时间" and isinstance(v, str) and v:
            try:
                out[k] = int(datetime.strptime(v, "%Y-%m-%d %H:%M").timestamp() * 1000)
                continue
            except Exception:
                pass
        if v is None or v == "":
            continue
        out[k] = v
    return out


'''
s = s.replace("\n# ---------------------------------------------------------------- 组表", feishu + "\n# ---------------------------------------------------------------- 组表", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched feishu class")
