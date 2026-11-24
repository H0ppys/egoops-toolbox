#!/bin/bash
# 用 nip.io 域名给纯 IP 的服务器申请真证书（浏览器可信任）
set -e
DOMAIN="<FILL_ME>.nip.io"
NGX=/etc/nginx/nginx.conf
BAK=${NGX}.bak-https-$(date +%Y%m%d%H%M%S)

cp "$NGX" "$BAK"
echo "备份: $BAK"

# 1) 加 acme 校验路径（80 端口）
if ! grep -q 'well-known/acme-challenge' "$NGX"; then
  sed -i "/server_name  _;/a\\        location /.well-known/acme-challenge/ { root /var/www/acme; }" "$NGX"
fi
nginx -t
systemctl reload nginx
echo "== acme 路径已就绪"

mkdir -p /var/www/acme/.well-known/acme-challenge
echo ok > /var/www/acme/.well-known/acme-challenge/ping
curl -s --max-time 10 "http://${DOMAIN}/.well-known/acme-challenge/ping" || echo "(本地校验失败，继续尝试签发)"

# 2) 签发证书
/root/.acme.sh/acme.sh --set-default-ca --server letsencrypt >/dev/null 2>&1 || true
/root/.acme.sh/acme.sh --issue -d "$DOMAIN" -w /var/www/acme --force

# 3) 装证书到 nginx 目录
mkdir -p /etc/nginx/ssl
/root/.acme.sh/acme.sh --install-cert -d "$DOMAIN" \
  --key-file       /etc/nginx/ssl/key.pem \
  --fullchain-file /etc/nginx/ssl/fullchain.pem \
  --reloadcmd      "systemctl reload nginx"

# 4) 同一个 server 块上开 443
if ! grep -q 'listen       443 ssl' "$NGX"; then
  sed -i "/listen       \[::\]:80 default_server;/a\\
        listen       443 ssl http2;\\
        listen       [::]:443 ssl http2;\\
        ssl_certificate     /etc/nginx/ssl/fullchain.pem;\\
        ssl_certificate_key /etc/nginx/ssl/key.pem;\\
        ssl_protocols       TLSv1.2 TLSv1.3;\\
        ssl_session_cache   shared:SSL:10m;" "$NGX"
fi
nginx -t
systemctl reload nginx
echo "== HTTPS 配置完成"
