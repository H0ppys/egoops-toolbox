#!/usr/bin/env bash
LOG=/opt/lark-bot/events.ndjson
START=$(wc -l < "$LOG")
echo "当前日志行数：$START，开始监听 110 秒…"
END=$((SECONDS + 110))
while [ $SECONDS -lt $END ]; do
  NOW=$(wc -l < "$LOG")
  if [ "$NOW" -gt "$START" ]; then
    tail -n $((NOW - START)) "$LOG" | grep -vE '"ev":"(cli_stderr|session_end|heartbeat)"' | cut -c1-800
    START=$NOW
  fi
  sleep 2
done
echo "--- 监听结束，新增重要事件行数：$(tail -n +$((START+1)) "$LOG" | wc -l) ---"
echo "=== 服务当前状态 ==="
systemctl is-active lark-bot.service
pgrep -af 'event consume' | grep -v pgrep | head -2
