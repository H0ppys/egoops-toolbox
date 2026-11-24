#!/bin/bash
set -e
cd /opt/egoops/relay

cat > /etc/systemd/system/egoops-relay.service <<'EOF'
[Unit]
Description=EgoOps relay (collection site application)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/egoops/relay
ExecStart=/opt/node22/bin/node server.mjs
Restart=always
RestartSec=3
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable egoops-relay >/dev/null 2>&1 || true
systemctl restart egoops-relay
sleep 2
systemctl is-active egoops-relay
echo "--- local health ---"
curl -s --max-time 8 http://127.0.0.1:18090/api/health
echo
echo "--- firewalld ---"
systemctl is-active firewalld || true
firewall-cmd --list-ports 2>/dev/null || true
echo "--- journal ---"
journalctl -u egoops-relay -n 8 --no-pager || true
