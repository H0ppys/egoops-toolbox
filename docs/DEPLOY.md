# 部署流程（DEPLOY）

服务器：单机 CentOS/RHEL 系 + systemd + nginx，relay 服务只监听 `127.0.0.1:18090`，由 nginx 反代 `/relay/` 对外。**必须按编号顺序执行**，每步都自带健康检查输出，任一步失败先回滚再继续。

前置：root 权限、80/443 放行、`/opt` 可写。所有脚本已脱敏，运行前把 `<FILL_ME>` 换成实际值。

## 编号流程

| 步骤 | 脚本 | 做什么 | 关键校验 |
| --- | --- | --- | --- |
| 01 | `01-install-node.sh` | 从腾讯云镜像装 Node **v22.14.0** 到 `/opt/node22`，验证内置 `node:sqlite` 可用，建 `/opt/egoops/relay` | `/opt/node22/bin/node -v`；`:memory:` 建表成功打印 `node:sqlite OK` |
| 02 | `02-check-net.sh` | 出网体检：DNS + HTTPS 可达性（`mrobo.uav.meituan.com`、`egoops.meituan.com`） | curl 返回码与耗时 |
| 03 | `03-install-relay.sh` | 写 `egoops-relay.service`（`ExecStart=/opt/node22/bin/node server.mjs`，`Restart=always`），reload + 启动 | `systemctl is-active`；`curl 127.0.0.1:18090/api/health`；journal 末 8 行 |
| 04 | `04-nginx-relay.py` | 在 nginx 默认 server 块插入 `location /relay/` 反代到 `127.0.0.1:18090`（幂等 + 时间戳备份，`nginx -t` 失败自动回滚） | 打印 `patched at <idx>`、`nginx -t` 结果 |
| 05 | `05-harden.sh` | 备份试跑一次，写 cron `10 3 * * *` 每日备份，重启服务并确认只监听本机 | `ss -lntp` 输出含 18090；`curl /relay/api/health` |
| 06 | `06-switch-to-collect.sh` | 切到「采集点提报」业务：停服务 → 清 `relay.db`/`egoops_token.json`/`data/` → 重建空目录 → 启动 | 本机 + 经 nginx 两路 health；`du -sh data` |
| 07 | `07-install-ffmpeg.sh` | 装静态 ffmpeg 到 `/opt/ffmpeg`（johnvansickle 静态包） | `ffmpeg -version` 前两行 |
| 08 | `08-https-prep.sh` | 装 acme.sh（纯 shell，不依赖 yum 源），准备 `/var/www/acme/.well-known/acme-challenge` | acme.sh 存在性；打印 nginx 现有 location |
| 09 | `09-https-issue.sh` | 用 `nip.io` 域名（`<FILL_ME>.nip.io`）给纯 IP 服务器申真证书，装到 `/etc/nginx/ssl`，同 server 块开 443 | `nginx -t`；`--install-cert` 的 reloadcmd |
| 10 | `10-https-selfsigned.sh` | 备选方案：自签证书（IP SAN + `CA:TRUE` 便于 Android 信任 Android 7+ 的用户 CA 策略），开 443 保留 80 | `openssl x509 -noout -subject -enddate`；`curl -sk https://<FILL_ME>/relay/api/health` |

09 与 10 二选一：能出网优先 09（浏览器可信任）；内网/证书链不通时用 10，并在客户端固定该证书（`src/ui-patch/wire_tls_viewer.py`、`src/android/wire_tls_android.py` 就是干这个的）。

## 运维补充脚本（同一分类，不参与编号顺序）

| 脚本 | 用途 |
| --- | --- |
| `src/deploy/ssh_exec.py` | 非交互 SSH 执行器：`python ssh_exec.py "<cmd>"`、`-f script.sh`（走 `bash -s`）、`-u 本地文件 -d 远端目录` |
| `src/deploy/setup_ssh_key.py` | 生成 ed25519 密钥并装到服务器，之后免密 |
| `src/deploy/switch_ssh_key.py` | 把 `ssh_exec.py` 的默认口令认证切换为密钥认证 |
| `src/deploy/rescue_server.py` | 服务器卡住时用更长超时重连，并清理残留转码进程 |
| `src/deploy/deploy_v2.sh` … `deploy_v7.sh` | 早期迭代版本（v2 规范化备份名 / v3 写 base token / v4-v7 增量修补），保留做进化史参照，生产用 01–10 |
| `src/deploy/probe-ports.js` | 在 8080/8443/9000/3000/8000/18091/5000 上临时起监听，探测哪些端口被占用（60 秒后自动退出） |

## 配置模板

`src/deploy/config.prod.example.json`（原 `deploy\config.prod.json`，`adminKey` 已脱敏）：

```json
{
  "port": 18090,
  "host": "127.0.0.1",
  "dbFile": "relay.db",
  "dataDir": "data",
  "chunkSize": 4194304,
  "maxFileBytes": 1073741824,
  "inviteCode": "",
  "adminKey": "<FILL_ME>",
  "backupDir": "backup",
  "backupKeepDays": 14
}
```

| 字段 | 含义 |
| --- | --- |
| `port` / `host` | relay 监听端口与地址（只绑本机，靠 nginx 对外） |
| `dbFile` / `dataDir` | SQLite 文件与素材目录 |
| `chunkSize` | 分片上传块大小（4 MiB） |
| `maxFileBytes` | 单文件上限（1 GiB） |
| `inviteCode` | 采集员邀请码（空 = 不校验） |
| `adminKey` | 管理接口口令，`<FILL_ME>` |
| `backupDir` / `backupKeepDays` | 备份目录与保留天数（14 天） |

## 回滚要点

- nginx：04/09/10 都会先 `cp nginx.conf nginx.conf.bak-<时间戳>`，失败时脚本自身回滚，手工回滚直接 `cp` 回去再 `nginx -t && systemctl reload nginx`。
- 服务：`systemctl stop egoops-relay` + 恢复 `relay.db`/`data/` 备份。
- 06 会删库重建，**执行前务必备份** `relay.db` 与 `data/`。
