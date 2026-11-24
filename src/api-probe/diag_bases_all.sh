#!/usr/bin/env bash
set -u
export HOME=/root
L=/usr/local/bin/lark-cli

for t in KWQgbb9duaH8mmsvJ9xc3bBKnof H9SbbrYeFa5InIsl28UcMLzbnQf AKFeba8MNaoM0ds8TfDcpnfon3g EqkWbrSCjaehIvsOGYEcDGCingh Ikydwd9KGiqXOwk82WlclAVjnyg; do
  info=$($L base +base-get --base-token "$t" 2>&1)
  name=$(printf '%s' "$info" | grep -oE '"name": *"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//')
  tabs=$($L base +table-list --base-token "$t" 2>&1)
  cnt=$(printf '%s' "$tabs" | grep -c '"id": "tbl')
  echo "=== $t | ${name:-读取失败} | 表数=$cnt ==="
  printf '%s' "$tabs" | grep -oE '"name": *"[^"]*"' | sed 's/.*: *"//;s/"$//' | head -30
  echo
done
