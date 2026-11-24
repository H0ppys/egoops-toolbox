#!/usr/bin/env bash
echo "=== 服务状态 ==="
systemctl is-enabled lark-bot.service
systemctl is-active lark-bot.service
systemctl show lark-bot.service -p NRestarts -p ActiveEnterTimestamp -p MemoryCurrent -p MemoryMax --no-pager
echo
echo "=== 开机自启 & 崩溃重启策略 ==="
systemctl cat lark-bot.service --no-pager | grep -E 'Restart|WantedBy'
echo
echo "=== 当前 consume 进程 ==="
pgrep -af 'event consume' | head
echo
echo "=== 最近 5 条日志 ==="
journalctl -u lark-bot --no-pager -n 5 -o cat
echo
echo "=== 磁盘/内存 ==="
df -h / | tail -1
free -m | head -2
