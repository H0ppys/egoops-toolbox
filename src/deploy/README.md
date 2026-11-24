# deploy（服务器部署与运维）

本组 **22** 个脚本。单机 relay 服务从零到 HTTPS 的 10 步部署流程 + SSH 传输、密钥安装、故障救援。

## 代表脚本

- `01-install-node.sh` ~ `10-https-selfsigned.sh`：见 [../docs/DEPLOY.md](../docs/DEPLOY.md)
- `ssh_exec.py`：非交互 SSH 执行/上传（`-f` 走 `bash -s`）
- `setup_ssh_key.py` / `switch_ssh_key.py`：改免密登录
- `rescue_server.py`：长超时重连 + 清理转码进程
- `deploy_v2.sh` ~ `deploy_v7.sh`：历史迭代版本
- `probe-ports.js`：批量探测端口占用

## 运行前提

Linux 服务器（systemd + nginx）、root 权限、`paramiko`（Python 侧）。

## 注意

01–10 必须按序；06 会清库重建，先备份。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
