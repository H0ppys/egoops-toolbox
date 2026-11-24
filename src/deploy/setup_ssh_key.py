"""生成 SSH 密钥并装到服务器，之后不再用密码登录。"""
import os
import subprocess
import sys

import paramiko

HOST = "<FILL_ME>"
USER = "root"
PWD = "<FILL_ME>"
KEY = os.path.join(os.path.expanduser("~"), ".ssh", "egoops_ed25519")

os.makedirs(os.path.dirname(KEY), exist_ok=True)
if not os.path.exists(KEY):
    subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", KEY, "-N", "", "-C", "egoops-collect"],
                   check=True)
    print("已生成密钥:", KEY)

pub = open(KEY + ".pub", encoding="utf-8").read().strip()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=22, username=USER, password=PWD, timeout=30,
          banner_timeout=30, auth_timeout=30, allow_agent=False, look_for_keys=False)

cmd = (
    "mkdir -p /root/.ssh && chmod 700 /root/.ssh && "
    "grep -qF '%s' /root/.ssh/authorized_keys 2>/dev/null || echo '%s' >> /root/.ssh/authorized_keys; "
    "chmod 600 /root/.ssh/authorized_keys; wc -l < /root/.ssh/authorized_keys"
) % (pub, pub)
stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
print("authorized_keys 行数:", stdout.read().decode().strip())
print(stderr.read().decode()[:200])
c.close()

# 用密钥验证
test = paramiko.SSHClient()
test.set_missing_host_key_policy(paramiko.AutoAddPolicy())
test.connect(HOST, port=22, username=USER, key_filename=KEY, timeout=30,
             banner_timeout=30, auth_timeout=30, allow_agent=False, look_for_keys=False)
stdin, stdout, stderr = test.exec_command("hostname; uptime", timeout=20)
print("密钥登录成功:\n" + stdout.read().decode().strip())
test.close()
