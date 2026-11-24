#!/bin/bash
set -e
cd /opt/egoops/relay

echo "--- 停服务 ---"
systemctl stop egoops-relay || true

echo "--- 清理旧数据（旧 schema / 美团 token） ---"
rm -f relay.db relay.db-wal relay.db-shm
rm -f egoops_token.json
rm -rf data
mkdir -p data

echo "--- 启动 ---"
systemctl restart egoops-relay
sleep 2
systemctl is-active egoops-relay
ss -lntp | grep 18090 || echo "!! 18090 未监听"

echo "--- 本机健康检查 ---"
curl -s --max-time 8 http://127.0.0.1:18090/api/health
echo
echo "--- 经 nginx ---"
curl -s --max-time 8 http://127.0.0.1/relay/api/health
echo
echo "--- 目录 ---"
du -sh /opt/egoops/relay/data 2>/dev/null || true
ls -la /opt/egoops/relay | head -15
echo "--- 日志 ---"
journalctl -u egoops-relay -n 6 --no-pager
