# api-probe（接口探测与只读核查）

本组 **85** 个脚本。对 EgoOps 开放接口、relay 中继服务、飞书 Bitable、Edge 调试端口做**只读**探测：抓响应结构、翻页验证、统计口径核对、令牌/Cookie 提取。多数脚本只打印不写库。

## 代表脚本

- `probe_api.py` / `probe_api2.py` / `probe_api3.py`：`/api/v1/recordings*` 的响应结构与翻页
- `probe_daterange.py` / `probe_dates.py` / `probe_groupby.py` / `probe_matrix.py`：日期区间、分组、矩阵统计口径
- `egoops_probe_sites.mjs` / `egoops_probe_tasks.mjs`：采集点与任务集接口探测（ESM + fetch）
- `extract_oidc.py` / `extract_oidc2.py` / `edge_*.py`：从 Edge 的 LevelDB/Session 文件里挖 OIDC 令牌
- `inspect_tables.js` / `members.js` / `scan_bases.js`：飞书多维表格字段与人表清单
- `diag_*.sh`：登录服务器后对 lark-cli / relay 健康状态做一次性体检

## 运行前提

需要 `Authorization: Bearer <FILL_ME>` 或本地 `egoops_token.json`（不入库）；`*.mjs` 需要 Node 18+；`playwright` 类脚本需要 `python -m playwright install chromium`。

## 注意

全部只读；`diag_*.sh` 里 `BASE_TOKEN`/`TABLE_ID` 已置空，跑之前先导出。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
