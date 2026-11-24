# 拆分映射（SPLIT）

原路径 → 仓库内路径。搬运为**逐字节内容 + 脱敏替换**，不改逻辑、不改文件名（仅 `config.prod.json` 按规范改名）。

## 1. 目录级映射

| 原路径 | 仓库内路径 | 数量 | 说明 |
| --- | --- | --- | --- |
| `deploy\01..10-*` | `src/deploy/` | 11 | 部署脚本，编号即执行顺序 |
| `deploy\config.prod.json` | `src/deploy/config.prod.example.json` | 1 | 脱敏并改名为 example |
| `deploy\probe-ports.js` | `src/deploy/probe-ports.js` | 1 | 端口占用探测 |
| `tools\*.py/.mjs` | `src/<category>/` | 313 | 按用途分类，文件名不变 |
| 工作区根目录的 `deploy_v2..v7.sh` 等散落脚本 | `src/<category>/` | 82 | 见下表逐文件映射 |

## 2. 根目录脚本逐文件映射（82 个）

| 原文件 | 仓库内路径 |
| --- | --- |
| `add_fields.sh` | `src/table-schema/add_fields.sh` |
| `add_ingest_field.sh` | `src/table-schema/add_ingest_field.sh` |
| `check_bot_access.js` | `src/bot/check_bot_access.js` |
| `check_metrics.py` | `src/api-probe/check_metrics.py` |
| `create_table.sh` | `src/table-schema/create_table.sh` |
| `create_table_dryrun.sh` | `src/table-schema/create_table_dryrun.sh` |
| `deploy_v2.sh` | `src/deploy/deploy_v2.sh` |
| `deploy_v3.sh` | `src/deploy/deploy_v3.sh` |
| `deploy_v4.sh` | `src/deploy/deploy_v4.sh` |
| `deploy_v5.sh` | `src/deploy/deploy_v5.sh` |
| `deploy_v6.sh` | `src/deploy/deploy_v6.sh` |
| `deploy_v7.sh` | `src/deploy/deploy_v7.sh` |
| `diag2.sh` | `src/api-probe/diag2.sh` |
| `diag_base.sh` | `src/api-probe/diag_base.sh` |
| `diag_base2.sh` | `src/api-probe/diag_base2.sh` |
| `diag_bases_all.sh` | `src/api-probe/diag_bases_all.sh` |
| `diag_chat.sh` | `src/api-probe/diag_chat.sh` |
| `diag_data.sh` | `src/data-backfill/diag_data.sh` |
| `diag_search.sh` | `src/api-probe/diag_search.sh` |
| `edge_dump_egoops.py` | `src/api-probe/edge_dump_egoops.py` |
| `edge_dump_ss.py` | `src/api-probe/edge_dump_ss.py` |
| `edge_ls_scan.py` | `src/api-probe/edge_ls_scan.py` |
| `egoops_dl.mjs` | `src/api-probe/egoops_dl.mjs` |
| `egoops_probe_sites.mjs` | `src/api-probe/egoops_probe_sites.mjs` |
| `egoops_probe_tasks.mjs` | `src/api-probe/egoops_probe_tasks.mjs` |
| `extract_oidc.py` | `src/api-probe/extract_oidc.py` |
| `extract_oidc2.py` | `src/api-probe/extract_oidc2.py` |
| `health_bot.sh` | `src/bot/health_bot.sh` |
| `inspect2.js` | `src/api-probe/inspect2.js` |
| `inspect_capacity.js` | `src/table-schema/inspect_capacity.js` |
| `inspect_tables.js` | `src/table-schema/inspect_tables.js` |
| `lark_probe.py` | `src/lark/lark_probe.py` |
| `members.js` | `src/api-probe/members.js` |
| `patch_autorefresh.py` | `src/ui-patch/patch_autorefresh.py` |
| `patch_browser_login.py` | `src/ui-patch/patch_browser_login.py` |
| `patch_check_cli.py` | `src/ui-patch/patch_check_cli.py` |
| `patch_crashlog.py` | `src/ui-patch/patch_crashlog.py` |
| `patch_feishu.py` | `src/lark/patch_feishu.py` |
| `patch_feishu_sync.py` | `src/lark/patch_feishu_sync.py` |
| `patch_gui_creds.py` | `src/ui-patch/patch_gui_creds.py` |
| `patch_hidden.py` | `src/ui-patch/patch_hidden.py` |
| `patch_hideconsole.py` | `src/ui-patch/patch_hideconsole.py` |
| `patch_identity.py` | `src/ui-patch/patch_identity.py` |
| `patch_ingest.py` | `src/ui-patch/patch_ingest.py` |
| `patch_login.py` | `src/ui-patch/patch_login.py` |
| `patch_login_dialog.py` | `src/ui-patch/patch_login_dialog.py` |
| `patch_msg.py` | `src/ui-patch/patch_msg.py` |
| `patch_title.py` | `src/ui-patch/patch_title.py` |
| `patch_wizard.py` | `src/ui-patch/patch_wizard.py` |
| `probe_787.py` | `src/api-probe/probe_787.py` |
| `probe_api.py` | `src/api-probe/probe_api.py` |
| `probe_api2.py` | `src/api-probe/probe_api2.py` |
| `probe_api3.py` | `src/api-probe/probe_api3.py` |
| `probe_bot.sh` | `src/bot/probe_bot.sh` |
| `probe_bot2.sh` | `src/bot/probe_bot2.sh` |
| `probe_daterange.py` | `src/api-probe/probe_daterange.py` |
| `probe_dates.py` | `src/api-probe/probe_dates.py` |
| `probe_groupby.py` | `src/api-probe/probe_groupby.py` |
| `probe_gui.ps1` | `src/api-probe/probe_gui.ps1` |
| `probe_matrix.py` | `src/api-probe/probe_matrix.py` |
| `probe_mtsy.sh` | `src/api-probe/probe_mtsy.sh` |
| `probe_projects.py` | `src/api-probe/probe_projects.py` |
| `probe_projects2.py` | `src/api-probe/probe_projects2.py` |
| `probe_stats.py` | `src/api-probe/probe_stats.py` |
| `probe_task_actor.py` | `src/api-probe/probe_task_actor.py` |
| `probe_tet.py` | `src/api-probe/probe_tet.py` |
| `probe_tet2.py` | `src/api-probe/probe_tet2.py` |
| `probe_vendor.py` | `src/api-probe/probe_vendor.py` |
| `recreate_table.sh` | `src/table-schema/recreate_table.sh` |
| `recreate_table2.sh` | `src/table-schema/recreate_table2.sh` |
| `recreate_table3.sh` | `src/table-schema/recreate_table3.sh` |
| `recreate_table4.sh` | `src/table-schema/recreate_table4.sh` |
| `scan_bases.js` | `src/api-probe/scan_bases.js` |
| `ssh_exec.py` | `src/deploy/ssh_exec.py` |
| `test_browser_login.py` | `src/api-probe/test_browser_login.py` |
| `test_cdp.js` | `src/api-probe/test_cdp.js` |
| `test_parse_token.py` | `src/api-probe/test_parse_token.py` |
| `verify_agg.js` | `src/api-probe/verify_agg.js` |
| `verify_cross.sh` | `src/data-backfill/verify_cross.sh` |
| `verify_final.sh` | `src/data-backfill/verify_final.sh` |
| `verify_table.sh` | `src/table-schema/verify_table.sh` |
| `watch_bot.sh` | `src/bot/watch_bot.sh` |

## 3. tools\ 目录映射（313 个，按分类归并，文件名不变）

| 原路径 | 仓库内路径 | 说明 |
| --- | --- | --- |
| `tools\{add_relogin.py、api_draft.py、attach_and_fill.py…}` | `src/api-probe/` | 46 个；例如 add_relogin.py、api_draft.py、attach_and_fill.py… |
| `tools\{check_storage.py、cleanup_empty_sites.py、import_scenes.py…}` | `src/data-backfill/` | 9 个；例如 check_storage.py、cleanup_empty_sites.py、import_scenes.py… |
| `tools\{add_invite_tab.py、add_invites_server.py、add_login_check.py…}` | `src/ui-patch/` | 125 个；例如 add_invite_tab.py、add_invites_server.py、add_login_check.py… |
| `tools\{rescue_server.py、setup_ssh_key.py、switch_ssh_key.py}` | `src/deploy/` | 3 个；例如 rescue_server.py、setup_ssh_key.py、switch_ssh_key.py |
| `tools\{add_anticode.py、add_area_pano.py、add_crash_dialog.py…}` | `src/android/` | 102 个；例如 add_anticode.py、add_area_pano.py、add_crash_dialog.py… |
| `tools\{lark_read.py、lark_read2.py、sync_lark_vendors.py}` | `src/lark/` | 3 个；例如 lark_read.py、lark_read2.py、sync_lark_vendors.py |
| `tools\{app2_polish.py、calib_thresholds.py、calibrate_qc.py…}` | `src/misc/` | 25 个；例如 app2_polish.py、calib_thresholds.py、calibrate_qc.py… |

## 4. 未纳入仓库的源

| 原路径 | 原因 |
| --- | --- |
| `tools\build-tools`、`tools\jdk`、`tools\platform`、`tools\download` | 大体积工具链（约 1.1 GB），只记录在 [TOOLCHAIN.md](TOOLCHAIN.md) |
| `tools\__pycache__` | 编译缓存（.pyc），规范禁止入库 |
| `tools\_note.txt` | 与脚本无关的便签 |
| `tools\*.mjs` 之外的抓取结果、`.csv/.ndjson` 业务数据 | 业务数据不入库 |
| `sim\*.jpg/.mp4`、`sim\dl_check`、`sim\dl_test` | 二进制样本（单文件 1–7 MB），只保留极小文本样例到 `examples\` |
| 工作区根目录 `egoops_token.json`、`*.log`、`tmp_*`、`*.spec`、`.exe` | 令牌/日志/构建产物，禁止入库 |
| `legacy\` 逐字节镜像 | 原文件含真实密钥，与「真实值绝不进仓库」冲突，故本仓不做 legacy 镜像，脱敏唯一副本见 `src\` |

