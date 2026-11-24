#!/usr/bin/env bash
set -eu
cd /opt/lark-bot

python3 - <<'PY'
import re
p = '/opt/lark-bot/config.env'
s = open(p, encoding='utf-8').read()
if re.search(r'(?m)^DATA_AS=', s):
    s = re.sub(r'(?m)^DATA_AS=.*$', 'DATA_AS=bot', s)
else:
    s = re.sub(r'(?m)^(BASE_TOKEN=.*)$', r'\1\n# 取数身份：bot=应用身份（不依赖用户 token）\nDATA_AS=bot', s, count=1)
open(p, 'w', encoding='utf-8').write(s)
PY

grep -E '^[A-Z_]+=' config.env | sed -E 's/(LLM_API_KEY)=.*/\1=***/'

systemctl restart lark-bot.service
sleep 5
systemctl is-active lark-bot.service
journalctl -u lark-bot --no-pager -n 3 -o cat
