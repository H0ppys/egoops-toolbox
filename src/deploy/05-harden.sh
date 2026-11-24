#!/bin/bash
set -e
cd /opt/egoops/relay

# 1) 备份脚本试跑
/opt/node22/bin/node backup.mjs

# 2) 每日 03:10 备份
CRON_LINE="10 3 * * * /opt/node22/bin/node /opt/egoops/relay/backup.mjs >> /var/log/egoops-backup.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'egoops/relay/backup.mjs' ; echo "$CRON_LINE" ) | crontab -
echo "--- crontab ---"
crontab -l | tail -3

# 3) 重启并确认只监听本机
systemctl restart egoops-relay
sleep 2
systemctl is-active egoops-relay
ss -lntp | grep 18090 || echo "!! 18090 未监听"
echo "--- 内部健康检查 ---"
curl -s --max-time 8 http://127.0.0.1:18090/api/health
echo
echo "--- 经 nginx 访问 ---"
curl -s --max-time 8 http://127.0.0.1/relay/api/health
echo
echo "--- 最近日志 ---"
journalctl -u egoops-relay -n 5 --no-pager
