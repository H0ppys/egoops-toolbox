"""受控实验：上传一个 200KB 测试文件 → 看磁盘 → 删除 → 再看磁盘，证明删除真的清理服务器备份。"""

import io
import json
import os
import sys
import urllib.request

sys.path.insert(0, "viewer")

import tls
from api import Api

BASE = "https://<FILL_ME>/relay"


def disk_bytes():
    import subprocess
    cmd = "du -sb /opt/egoops/relay/data | cut -f1"
    r = subprocess.run([sys.executable, "ssh_exec.py", cmd], capture_output=True, text=True)
    return int((r.stdout or "0").strip().splitlines()[-1])


def req(method, path, body=None, token=""):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    return json.loads(tls.urlopen(r, timeout=30).read())


def main():
    a = Api(BASE)
    a.login("存储测试")
    tok = getattr(a, "token", "")
    site = [s for s in a.sites() if s["name"] == "盛宴公寓"][0]

    before = disk_bytes()
    print("上传前磁盘:", before, "字节")

    payload = os.urandom(200 * 1024)
    up = req("POST", "/api/sites/%s/uploads" % site["id"],
             {"filename": "test_storage.bin", "kind": "photo", "size": len(payload),
              "content_type": "image/jpeg"}, tok)
    uid, chunk = up["upload_id"], up["chunk_size"]
    n = 0
    for i in range(0, len(payload), chunk):
        r = urllib.request.Request(BASE + "/api/uploads/%s/%d" % (uid, n), data=payload[i:i + chunk], method="PUT")
        r.add_header("Authorization", "Bearer " + tok)
        tls.urlopen(r, timeout=30).read()
        n += 1
    done = req("POST", "/api/uploads/%s/complete" % uid, {}, tok)
    fid = done["file"]["id"]
    mid = disk_bytes()
    print("上传后磁盘:", mid, "（增加 %d 字节）" % (mid - before))

    req("DELETE", "/api/files/" + fid, None, tok)
    after = disk_bytes()
    print("删除后磁盘:", after, "（相对上传后减少 %d 字节）" % (mid - after))
    print("结论:", "删除确实清理了服务器文件" if mid > after else "删除没有释放磁盘！")


if __name__ == "__main__":
    main()
