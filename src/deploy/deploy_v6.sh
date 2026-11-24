#!/usr/bin/env bash
set -eu
cd /opt/lark-bot

python3 - <<'PY'
import re
p = '/opt/lark-bot/config.env'
s = open(p, encoding='utf-8').read()
if re.search(r'(?m)^DAYS_WINDOW=', s):
    s = re.sub(r'(?m)^DAYS_WINDOW=.*$', 'DAYS_WINDOW=3', s)
else:
    s = re.sub(r'(?m)^(MAX_AGE_MINUTES=.*)$', r'\1\n# 只加载最近 N 天（含今天）的数据\nDAYS_WINDOW=3', s, count=1)
open(p, 'w', encoding='utf-8').write(s)
PY

grep -E '^[A-Z_]+=' config.env | sed -E 's/(LLM_API_KEY)=.*/\1=***/'

systemctl restart lark-bot.service
sleep 5
systemctl is-active lark-bot.service
journalctl -u lark-bot --no-pager -n 2 -o cat
