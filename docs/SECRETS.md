# 脱敏记录（SECRETS）

仓库内所有脚本中的真实密钥类内容已替换为 `<FILL_ME>`，替换只动值、保留字段名，因此脚本结构、调用链、参数名完全不变。下表为被脱敏的位置（`文件:行号` + 字段名），**不含真实值**。

## 脱敏规则

| 规则 | 匹配对象 | 替换为 |
| --- | --- | --- |
| `bearer` | `Authorization: Bearer <token>` | `<FILL_ME>` |
| `access_token` | JWT（`eyJ...`）形态的 access_token | `<FILL_ME>` |
| `secret_kv` | `token`/`password`/`app_secret`/`adminKey`/`api_key`/`cookie` 等键的字符串值 | `<FILL_ME>` |
| `secret_kv_plain` | `PASS=xxx`、`export TOKEN=xxx` 这类大写键赋值 | `<FILL_ME>` |
| `env_get_default` | `os.environ.get("DEPLOY_PASS", "...")` 的默认值 | `<FILL_ME>` |
| `cookie_header` | `Cookie: ...` 请求头 | `<FILL_ME>` |
| `ip` / `ip_public` | 内网地址与生产主机 IPv4（保留 127.0.0.1 / 0.0.0.0） | `<FILL_ME>` |
| `phone` | 11 位手机号 | `<FILL_ME>` |
| `open_id` | `ou_`/`om_`/`oc_`/`cli_` 前缀的 open_id、应用 ID | `<FILL_ME>` |
| `long_token` | 26–34 位长令牌（飞书 base token、地图 Key 等） | `<FILL_ME>` |
| `known_value` | 已确认为真实口令/令牌的字面值（逐条比对替换） | `<FILL_ME>` |

## 被脱敏的位置

| 文件:行号 | 字段 | 说明 |
| --- | --- | --- |
| `src/android/allow_cleartext.py:15` | `ip` | 内网/主机 IP |
| `src/android/publish_apk.py:15` | `ip` | 内网/主机 IP |
| `src/android/publish_apk.py:17` | `secret_kv` | 密钥类字段值（token/password/app_secret 等） |
| `src/android/publish_apk.py:20` | `ip` | 内网/主机 IP |
| `src/android/set_map_key.py:5` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/android/set_map_key.py:6` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/android/wire_tls_android.py:9` | `ip` | 内网/主机 IP |
| `src/android/wire_tls_android.py:36` | `ip` | 内网/主机 IP |
| `src/android/wire_tls_android.py:37` | `ip` ×2 | 内网/主机 IP |
| `src/api-probe/check_videos.mjs:3` | `ip` | 内网/主机 IP |
| `src/api-probe/create_draft.py:15` | `ip` | 内网/主机 IP |
| `src/api-probe/dl_media.mjs:3` | `ip` | 内网/主机 IP |
| `src/api-probe/e2e-test.mjs:47` | `phone` | 手机号 |
| `src/api-probe/export_named.mjs:3` | `ip` | 内网/主机 IP |
| `src/api-probe/export_site.mjs:3` | `ip` | 内网/主机 IP |
| `src/api-probe/inspect2.js:22` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/inspect2.js:23` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/inspect2.js:24` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/make_draft.py:11` | `ip` | 内网/主机 IP |
| `src/api-probe/members.js:4` | `open_id` | open_id / app_id（ou_/cli_ 前缀） |
| `src/api-probe/members.js:21` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/members.js:22` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/members.js:23` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/members.js:24` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/members.js:25` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/api-probe/probe_mtsy.sh:4` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/api-probe/sim_chunk.mjs:4` | `ip` | 内网/主机 IP |
| `src/api-probe/sim_upload.mjs:5` | `ip` | 内网/主机 IP |
| `src/api-probe/sim_viewer.py:13` | `ip` | 内网/主机 IP |
| `src/api-probe/test_draft_live.py:12` | `ip` | 内网/主机 IP |
| `src/api-probe/test_draft_live2.py:10` | `ip` | 内网/主机 IP |
| `src/api-probe/test_sop_rows.py:14` | `ip` | 内网/主机 IP |
| `src/api-probe/verify-prod-e2e.mjs:2` | `ip` | 内网/主机 IP |
| `src/api-probe/verify-prod.mjs:2` | `ip` | 内网/主机 IP |
| `src/api-probe/verify-prod.mjs:3` | `ip` | 内网/主机 IP |
| `src/api-probe/verify_agg.js:4` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/bot/check_bot_access.js:4` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/data-backfill/test_delete_frees_disk.py:14` | `ip` | 内网/主机 IP |
| `src/data-backfill/verify_cross.sh:4` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/data-backfill/verify_final.sh:4` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/deploy/09-https-issue.sh:4` | `ip` | 内网/主机 IP |
| `src/deploy/10-https-selfsigned.sh:4` | `ip` | 内网/主机 IP |
| `src/deploy/config.prod.example.json:9` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/deploy/deploy_v3.sh:12` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/deploy/rescue_server.py:7` | `ip` | 内网/主机 IP |
| `src/deploy/rescue_server.py:9` | `secret_kv` | 密钥类字段值（token/password/app_secret 等） |
| `src/deploy/setup_ssh_key.py:8` | `ip` | 内网/主机 IP |
| `src/deploy/setup_ssh_key.py:10` | `secret_kv` | 密钥类字段值（token/password/app_secret 等） |
| `src/deploy/ssh_exec.py:14` | `ip` | 内网/主机 IP |
| `src/deploy/ssh_exec.py:17` | `env_get_default` | 代码内默认口令/主机（os.environ.get 默认值） |
| `src/deploy/switch_ssh_key.py:7` | `env_get_default` | 代码内默认口令/主机（os.environ.get 默认值） |
| `src/deploy/switch_ssh_key.py:8` | `env_get_default` | 代码内默认口令/主机（os.environ.get 默认值） |
| `src/lark/lark_probe.py:7` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/lark/lark_read.py:7` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/lark/lark_read2.py:7` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/lark/sync_lark_vendors.py:22` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/misc/calibrate_qc.py:11` | `ip` | 内网/主机 IP |
| `src/misc/preview_with_map.py:13` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/misc/watermark_on_real_photo.py:17` | `ip` | 内网/主机 IP |
| `src/misc/watermark_on_real_photo2.py:16` | `ip` | 内网/主机 IP |
| `src/table-schema/add_fields.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/add_ingest_field.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/create_table.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/create_table_dryrun.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/inspect_capacity.js:4` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/table-schema/inspect_tables.js:19` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/table-schema/inspect_tables.js:20` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/table-schema/inspect_tables.js:21` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/table-schema/inspect_tables.js:22` | `long_token` | 长令牌/资源 token（26–34 位） |
| `src/table-schema/recreate_table.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/recreate_table2.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/recreate_table3.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/recreate_table4.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/table-schema/verify_table.sh:5` | `known_value` | 已确认的真实密钥/口令字面值 |
| `src/ui-patch/fix_cert_bom.py:25` | `ip` | 内网/主机 IP |
| `src/ui-patch/fix_cert_bom.py:26` | `ip` | 内网/主机 IP |
| `src/ui-patch/fix_draft.py:13` | `ip` | 内网/主机 IP |
| `src/ui-patch/fix_settings_layout.py:29` | `ip` | 内网/主机 IP |
| `src/ui-patch/patch_wizard.py:9` | `open_id` | open_id / app_id（ou_/cli_ 前缀） |
| `src/ui-patch/patch_wizard.py:49` | `open_id` | open_id / app_id（ou_/cli_ 前缀） |
| `src/ui-patch/patch_wizard.py:105` | `open_id` | open_id / app_id（ou_/cli_ 前缀） |
| `src/ui-patch/wire_tls_viewer.py:43` | `ip` ×2 | 内网/主机 IP |
| `src/ui-patch/wire_tls_viewer.py:44` | `ip` ×2 | 内网/主机 IP |

合计 **86** 处，涉及 **59** 个文件。

## 复查方法

```powershell
$files = (Get-ChildItem src -Recurse -File).FullName
Select-String -Path $files -Pattern 'eyJ[A-Za-z0-9_-]{20,}','(?<!\d)1[3-9]\d{9}(?!\d)',
  '\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b','(?i)bearer\s+[A-Za-z0-9._-]{20,}'
```

本地复跑结果：全部 0 命中。

