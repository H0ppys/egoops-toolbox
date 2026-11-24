"""把构建好的 APK 发布到服务器：上传文件 + 写版本信息。

用法：
    python tools/publish_apk.py android/egoops-collect-v39.apk "修复场景分类"
"""

import hashlib
import io
import json
import os
import sys

import paramiko

HOST = "<FILL_ME>"
USER = "root"
PWD = "<FILL_ME>"
KEY = os.path.join(os.path.expanduser("~"), ".ssh", "egoops_ed25519")
REMOTE_DIR = "/opt/egoops/relay"
PUBLIC = "https://<FILL_ME>/relay"


def version_of(apk):
    """从 AndroidManifest 里读 versionCode / versionName"""
    manifest = io.open("android/AndroidManifest.xml", encoding="utf-8").read()
    import re
    vc = re.search(r'android:versionCode="(\d+)"', manifest).group(1)
    vn = re.search(r'android:versionName="([^"]+)"', manifest).group(1)
    return int(vc), vn


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    apk = sys.argv[1]
    notes = sys.argv[2] if len(sys.argv) > 2 else ""
    if not os.path.exists(apk):
        print("找不到文件:", apk)
        return

    vc, vn = version_of(apk)
    data = open(apk, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    size = len(data)
    print("APK: %s | versionCode=%s versionName=%s | %.0fKB | sha256=%s…" %
          (os.path.basename(apk), vc, vn, size / 1024, sha[:12]))

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PWD,
              key_filename=KEY if os.path.exists(KEY) else None,
              timeout=30, banner_timeout=30, auth_timeout=30,
              allow_agent=False, look_for_keys=False)

    c.exec_command(f"mkdir -p {REMOTE_DIR}/apk")[1].channel.recv_exit_status()
    sftp = c.open_sftp()
    sftp.putfo(io.BytesIO(data), f"{REMOTE_DIR}/apk/egoops-collect-latest.apk")
    sftp.close()

    info = {
        "versionCode": vc,
        "versionName": vn,
        "url": PUBLIC + "/apk/latest.apk",
        "size": size,
        "sha256": sha,
        "notes": notes,
        "publishedAt": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
    }
    sftp = c.open_sftp()
    sftp.putfo(io.BytesIO(json.dumps(info, ensure_ascii=False, indent=1).encode()), f"{REMOTE_DIR}/app_version.json")
    sftp.close()
    c.exec_command("systemctl restart egoops-relay")[1].channel.recv_exit_status()
    c.close()

    print("已发布:", json.dumps(info, ensure_ascii=False))
    print("验证:", PUBLIC + "/api/app/version")


if __name__ == "__main__":
    main()
