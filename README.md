# egoops-toolbox

EgoOps（美团采集点提报）项目在 2026 年 10–11 月沉淀下来的运维/探针/补丁脚本合集：**407 个脚本**，按用途分成 9 类，全部完成脱敏处理，可直接作为工程经验归档或复用的脚手架。

## 1. 定位

把「散落在工作区根目录的一次性运维脚本 + tools\ 下的 313 个补丁脚本 + deploy\ 的 12 个部署脚本」收拢成一个可检索、可分类、可复用的工具仓。只用标准工具链（Python 3 / Node 18+ / bash），不需要额外框架。

## 2. 原始来源

| 项 | 值 |
| --- | --- |
| 原始工作区 | `C:\Users\Administrator\Documents\deepseek-harness\default-workspace` |
| 来源目录 | 工作区根目录散落脚本、`tools\`、`deploy\`、`sim\`（样例） |
| 归属业务 | EgoOps 采集点提报 / relay 中继服务 / 飞书多维表格日报 / 安卓采集 App |
| 时间跨度 | 2026-11（脚本内注释时间戳 20261119–20261122） |
| 文件构成 | py 341 个、js/mjs 26 个、sh 38 个、ps1 1 个、json 1 个 |

## 3. 目录结构

```
egoops-toolbox/
  README.md                 # 本文件
  LICENSE                   # MIT
  .gitignore
  src/
    api-probe/    (85)      # 接口探测 / 只读核查
    table-schema/ (11)      # 表结构建立与校验
    data-backfill/(12)      # 数据回填 / 导入 / 清理
    ui-patch/     (139)      # 查看器与后端代码补丁
    deploy/       (22)      # 部署脚本 01..10 + 运维传输
    bot/          ( 5)      # 飞书机器人巡检
    android/      (102)      # 安卓端补丁 / 构建 / 发布
    lark/         ( 6)      # 飞书多维表格
    misc/         (25)      # 水印预览与杂项
  examples/                 # 极小脱敏样例（每类 ≤ 2KB）
  docs/
    INVENTORY.md            # 407 个脚本的分类清单（用途/依赖/是否含密钥）
    SECRETS.md              # 脱敏位置清单（文件:行号 + 字段名，无真实值）
    SPLIT.md                # 原路径 → 仓库内路径映射
    DEPLOY.md               # 部署编号流程 01-install-node.sh … 10-https-selfsigned.sh
    TOOLCHAIN.md            # 未纳入的大体积工具链说明（Android SDK / JDK）
    ARCHITECTURE.md         # 组件职责与数据流
    VALIDATION.md           # 语法校验真实输出
  legacy/                   # 空：原文件含真实密钥，不做逐字节镜像（理由见 SPLIT.md）
  tests/                    # 冒烟脚本
```

## 4. 安装与运行

```bash
# 依赖（按需）
pip install paramiko playwright openpyxl pillow numpy   # Python 侧
npm i -g @larksuite/cli                                  # 飞书多维表格读写（lark-cli）
# playwright 首次需要下载浏览器
python -m playwright install chromium
```

运行前先填占位符：仓库里所有密钥、内网 IP、手机号、open_id、app_secret、数据库口令均为 `<FILL_ME>`，按 [docs/SECRETS.md](docs/SECRETS.md) 的清单补自己的值（建议放环境变量，不要写回文件）。

```bash
# 例：探测 EgoOps 统计接口（需先填 token）
python src/api-probe/probe_api.py
# 例：校验全部脚本语法
python -m compileall -q src
node --check src/api-probe/verify-prod.mjs
```

## 5. 模块说明

| 目录 | 数量 | 职责 |
| --- | --- | --- |
| `api-probe/` | 85 | 接口探测与只读核查：EgoOps/relay/飞书接口、令牌抓取、CDP 检查 |
| `table-schema/` | 11 | 飞书多维表格与 relay SQLite 的建表/重建/字段与容量校验 |
| `data-backfill/` | 12 | 数据回填、场景表导入、清理与存储一致性核对 |
| `ui-patch/` | 139 | 查看器（Tkinter）与 relay 后端（server.mjs/db.mjs/api.py）的代码补丁 |
| `deploy/` | 22 | 服务器部署运维：Node/relay/nginx/证书/备份/SSH 传输 |
| `bot/` | 5 | 飞书机器人 lark-bot 服务状态与事件巡检 |
| `android/` | 102 | 安卓采集端 Java/Manifest 补丁、构建、APK 发布 |
| `lark/` | 6 | 飞书多维表格读写与厂商→邀请码→大类同步 |
| `misc/` | 25 | 水印样式预览与度量、杂项演示脚本 |

逐脚本用途见 [docs/INVENTORY.md](docs/INVENTORY.md)。

## 6. 配置项

配置只有三种形态，均以占位符入库：

| 形态 | 文件 | 说明 |
| --- | --- | --- |
| JSON 配置 | `src/deploy/config.prod.example.json` | relay 服务配置模板：`port`/`host`/`dbFile`/`dataDir`/`chunkSize`/`maxFileBytes`/`inviteCode`/`adminKey`/`backupDir`/`backupKeepDays`。`adminKey` 已置 `<FILL_ME>` |
| 环境变量 | `DEPLOY_HOST`、`DEPLOY_PORT`、`DEPLOY_USER`、`DEPLOY_PASS`、`DEPLOY_KEY` | SSH 传输类脚本（`src/deploy/ssh_exec.py` 等）的默认值已是 `<FILL_ME>`，运行前导出 |
| 脚本内常量 | 各脚本顶部 `BASE`/`TOKEN`/`RELAY` | 一律 `<FILL_ME>`；推荐改成读环境变量 |

示例（PowerShell）：

```powershell
$env:DEPLOY_HOST = "relay.example.com"
$env:DEPLOY_USER = "root"
$env:DEPLOY_PASS = "<YOUR_PASS>"
python src\deploy\ssh_exec.py "systemctl is-active egoops-relay"
```

## 7. 打包与分发

本仓是脚本集合，没有统一入口，因此**不产物化**；分发方式是 `git archive` 或 zip：

```bash
git archive --format=zip -o egoops-toolbox.zip HEAD
```

如需把单个工具做成免装 Python 的可执行文件（例如 `ssh_exec.py`，仅依赖 paramiko）：

```bash
pyinstaller --onefile --name ssh_exec ^
  --hidden-import paramiko --collect-submodules paramiko ^
  src\deploy\ssh_exec.py
```

要点：`--onefile` + `--collect-submodules paramiko`（paramiko 的 ed25519/crypto 后端是动态导入，不收集会运行时报错）；产物不入库（`.gitignore` 已排除 `dist/`、`build/`、`*.exe`）。

## 8. 拆分说明

原路径到仓库内路径的逐文件映射见 [docs/SPLIT.md](docs/SPLIT.md)；脱敏位置见 [docs/SECRETS.md](docs/SECRETS.md)；未纳入的大体积工具链见 [docs/TOOLCHAIN.md](docs/TOOLCHAIN.md)。

关键取舍：

1. **不改逻辑**：只替换敏感值（值 → `<FILL_ME>`），函数体、参数名、调用顺序逐字保留。
2. **不做 legacy 镜像**：原脚本含真实口令/令牌，与「真实值绝不进仓库」冲突，故 `legacy/` 留空。
3. **二进制样本不入库**：`sim\` 下的 jpg/mp4（单文件 1–7 MB）只取脱敏文本样例到 `examples\`。
