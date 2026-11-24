#!/usr/bin/env python3
"""在 nginx 默认 server 块里加 /relay/ 反代到本机 18090（幂等、带备份）"""
import re, shutil, subprocess, sys, time

CONF = "/etc/nginx/nginx.conf"
MARK = "location /relay/"

src = open(CONF, encoding="utf-8").read()
if MARK in src:
    print("already patched")
    sys.exit(0)

bak = CONF + ".bak-" + time.strftime("%Y%m%d%H%M%S")
shutil.copy2(CONF, bak)
print("backup:", bak)

block = """    # EgoOps 采集点中转服务（自动添加）
    location /relay/ {
        proxy_pass http://127.0.0.1:18090/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        client_max_body_size 512m;
    }

"""

# 插到第一个 location /api 之前；没有就插到 server 块内第一个 location 前
m = re.search(r"^(\s*)location\s+/api\b", src, re.M)
if not m:
    m = re.search(r"^(\s*)location\s+/", src, re.M)
    if not m:
        print("找不到可插入的位置")
        sys.exit(1)

idx = m.start()
open(CONF, "w", encoding="utf-8").write(src[:idx] + block + src[idx:])
print("patched at", idx)

r = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())
if r.returncode != 0:
    shutil.copy2(bak, CONF)
    print("nginx -t 失败，已回滚")
    sys.exit(1)

subprocess.run(["systemctl", "reload", "nginx"], check=True)
print("nginx reloaded")
