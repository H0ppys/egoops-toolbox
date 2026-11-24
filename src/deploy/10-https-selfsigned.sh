#!/bin/bash
# 自签证书（IP SAN，CA:TRUE 便于 Android 信任），开启 443，保留 80
set -e
IP="<FILL_ME>"
NGX=/etc/nginx/nginx.conf
mkdir -p /etc/nginx/ssl

if [ ! -f /etc/nginx/ssl/cert.pem ]; then
  openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=CN/ST=Guangdong/L=Zhanjiang/O=EgoOps Collect/CN=${IP}" \
    -addext "subjectAltName=IP:${IP},DNS:localhost" \
    -addext "basicConstraints=critical,CA:TRUE" \
    -addext "keyUsage=critical,digitalSignature,keyEncipherment,keyCertSign"
fi

chmod 600 /etc/nginx/ssl/key.pem
openssl x509 -in /etc/nginx/ssl/cert.pem -noout -subject -enddate

cp "$NGX" "${NGX}.bak-tls-$(date +%Y%m%d%H%M%S)"

if ! grep -q 'listen       443 ssl' "$NGX"; then
  sed -i "/listen       \[::\]:80 default_server;/a\\
        listen       443 ssl http2;\\
        listen       [::]:443 ssl http2;\\
        ssl_certificate     /etc/nginx/ssl/cert.pem;\\
        ssl_certificate_key /etc/nginx/ssl/key.pem;\\
        ssl_protocols       TLSv1.2 TLSv1.3;\\
        ssl_session_cache   shared:SSL:10m;" "$NGX"
fi

nginx -t
systemctl reload nginx
echo "== nginx 已同时监听 80 / 443"
curl -sk --max-time 10 "https://${IP}/relay/api/health" && echo
