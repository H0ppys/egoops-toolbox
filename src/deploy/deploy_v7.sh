#!/usr/bin/env bash
set -eu
cd /opt/lark-bot

python3 - <<'PY'
import re
p = '/opt/lark-bot/config.env'
s = open(p, encoding='utf-8').read()

def upsert(s, key, val, after):
    if re.search(r'(?m)^%s=' % key, s):
        return re.sub(r'(?m)^%s=.*$' % key, f'{key}={val}', s)
    return re.sub(r'(?m)^(%s=.*)$' % after, r'\1\n%s=%s' % (key, val), s, count=1)

s = upsert(s, 'MAX_ANSWER_CHARS', '600', 'DAYS_WINDOW')
s = upsert(s, 'LLM_MAX_TOKENS', '1500', 'MAX_ANSWER_CHARS')
open(p, 'w', encoding='utf-8').write(s)
PY

grep -E '^[A-Z_]+=' config.env | sed -E 's/(LLM_API_KEY)=.*/\1=***/'

systemctl restart lark-bot.service
sleep 5
systemctl is-active lark-bot.service
journalctl -u lark-bot --no-pager -n 2 -o cat
