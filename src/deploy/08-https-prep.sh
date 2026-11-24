#!/bin/bash
set -e
# 1) 装 acme.sh（纯 shell，不依赖 yum 源）
if [ ! -x /root/.acme.sh/acme.sh ]; then
  curl -fsSL https://get.acme.sh | sh -s email=admin@example.com >/tmp/acme_install.log 2>&1 || true
fi
ls -la /root/.acme.sh/acme.sh 2>/dev/null || { echo "acme.sh 安装失败"; tail -20 /tmp/acme_install.log; exit 1; }

# 2) 准备 webroot
mkdir -p /var/www/acme/.well-known/acme-challenge
chown -R nginx:nginx /var/www/acme 2>/dev/null || true

# 3) nginx 加 acme 校验路径（不重启前先测试配置）
CONF=/etc/nginx/conf.d/egoops.conf
if ! grep -q 'well-known/acme-challenge' "$CONF" 2>/dev/null; then
  echo "需要在 nginx 加 location（手动确认）"
fi
grep -n "location" /etc/nginx/conf.d/*.conf | head -5
echo "---"
cat /etc/nginx/conf.d/*.conf | head -40
