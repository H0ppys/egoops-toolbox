"""服务器卡住时，用更长的超时重连并清理转码进程。"""
import sys
import time

import paramiko

HOST = "<FILL_ME>"
USER = "root"
PWD = "<FILL_ME>"


def try_connect(timeout=60):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=22, username=USER, password=PWD,
              timeout=timeout, banner_timeout=timeout, auth_timeout=timeout,
              allow_agent=False, look_for_keys=False)
    return c


for attempt in range(1, 4):
    try:
        c = try_connect(60)
        print("SSH 连上了（第 %d 次）" % attempt)
        for cmd in ["uptime", "ps aux | grep '[f]fmpeg' | head -5", "free -m | head -2"]:
            stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
            out = stdout.read().decode(errors="replace").strip()
            print("$ %s\n%s" % (cmd, out[:400]))
        stdin, stdout, stderr = c.exec_command("pkill -9 -f ffmpeg; sleep 1; ps aux | grep -c '[f]fmpeg'", timeout=30)
        print("清理 ffmpeg:", stdout.read().decode().strip())
        break
    except Exception as e:
        print("第 %d 次失败: %s" % (attempt, type(e).__name__))
        time.sleep(15)
else:
    print("SSH 仍然连不上")
    sys.exit(1)

c.close()
