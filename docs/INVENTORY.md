# 脚本清点清单（INVENTORY）

工作区根目录散落的运维/探针/补丁脚本 + `tools\` + `deploy\` 共 **407** 个文件，按用途分为 9 类。每个脚本的用途取自文件头注释（读取前 30 行）；无注释者按代码中出现的锚点文件 / API 路径判定，并在描述里注明。全部脚本已脱敏（见 [SECRETS.md](SECRETS.md)）。

## 分类统计

| 分类 | 数量 | 用途 |
| --- | --- | --- |
| `src/api-probe/` | 85 | 接口探测 / 只读核查（EgoOps、飞书 Bitable、中转服务 relay、CDP、令牌抓取） |
| `src/table-schema/` | 11 | 飞书多维表格与 relay SQLite 的表结构建立/重建/校验 |
| `src/data-backfill/` | 12 | 数据回填、导入、清理与一致性核对 |
| `src/ui-patch/` | 139 | 查看器（Tkinter）与 relay 后端（server.mjs/db.mjs/api.py）的代码补丁 |
| `src/deploy/` | 22 | 服务器部署与运维（Node 安装、relay 服务、nginx、证书、备份、SSH 传输） |
| `src/bot/` | 5 | 飞书机器人（lark-bot）服务状态、事件与巡检 |
| `src/android/` | 102 | 安卓采集端（MainActivity/WatermarkVideo/Uploader、构建、打包、发布） |
| `src/lark/` | 6 | 飞书开放平台/多维表格读写与厂商同步 |
| `src/misc/` | 25 | 水印样式预览与度量、杂项演示与实验脚本 |
| **合计** | **407** | |

## api-probe（85）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/api-probe/add_relogin.py` | 用保存的态开浏览器，若仍登录就重新抓一遍 cookie/storage 刷新时间戳 | playwright | 否 |
| `src/api-probe/api_draft.py` | 用接口创建一份「申请采集点」草稿（等价于点页面填写后保存草稿），只建草稿、不提交审核 | 本地模块: address_parse、agent_fill | 否 |
| `src/api-probe/attach_and_fill.py` | 接上已开的 Edge（CDP 9222）：抓登录态存盘 → 填申请采集点 → 保存草稿 | playwright；本地模块: agent_fill | 否 |
| `src/api-probe/check_draft.py` | 无文件头注释；按名称+代码判定：只读核查，关键调用 `b = p.chromium.connect_over_cdp(CDP)` | playwright | 否 |
| `src/api-probe/check_metrics.py` | 无文件头注释；按名称+代码判定：只读核查，关键调用 `d = json.load(open(r"C:\Users\Administrator\Documents\deepse` | 标准库 | 否 |
| `src/api-probe/check_site_online.py` | 用保存的 token 查一下线上有没有「美宜佳」这个采集点（只读） | 标准库 | 否 |
| `src/api-probe/check_videos.mjs` | 无文件头注释；按名称+代码判定：只读核查，关键调用 `const login = await (await fetch(B + '/api/auth/login', {` | node:fs；命令: node | 是（1 处） |
| `src/api-probe/create_draft.py` | 用采集数据创建/更新一条 EgoOps 草稿（地址取自采集字段，不编造） | 本地模块: address_parse、agent_fill、transcode_pc | 是（1 处） |
| `src/api-probe/demo2.py` | 完整演示：申请采集点 → 填表（含场景/地址/媒体）→ 保存草稿。只动弹窗内元素 | playwright；本地模块: address_parse、agent_fill | 否 |
| `src/api-probe/demo3.py` | 按索引填表（EgoOps 弹窗里的 input/textarea 顺序固定），再保存草稿 | playwright；本地模块: agent_fill | 否 |
| `src/api-probe/demo4.py` | 最终演示：按索引填表 + 搜索选场景 + 直接塞文件 + 保存草稿 | playwright；本地模块: address_parse、agent_fill | 否 |
| `src/api-probe/demo_save_draft.py` | 在 EgoOps 上完整走一次「申请采集点 → 保存草稿」，只动弹窗内元素 | playwright；本地模块: address_parse、agent_fill | 否 |
| `src/api-probe/diag2.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `/usr/local/bin/lark-cli im +chat-list --as bot --format json` | bash + lark-cli | 否 |
| `src/api-probe/diag_base.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 否 |
| `src/api-probe/diag_base2.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 否 |
| `src/api-probe/diag_bases_all.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 否 |
| `src/api-probe/diag_chat.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `/usr/local/bin/lark-cli im +chats --as bot 2>&1 \| head -60` | bash + lark-cli | 否 |
| `src/api-probe/diag_search.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 否 |
| `src/api-probe/dl_media.mjs` | 无文件头注释；按名称+代码判定：脚本，关键调用 `const login = await (await fetch(B + '/api/auth/login', {` | node:fs；命令: node | 是（1 处） |
| `src/api-probe/download.mjs` | 无文件头注释；按名称+代码判定：下载，关键调用 `const res = await fetch(url, { redirect: 'follow' });` | node:fs、node:path；命令: node | 否 |
| `src/api-probe/draft_fallback.py` | 让建草稿永不留下空任务： · 内容生成失败 → 用模板兜底 · 每个任务整体 try/except，一个失败不影响其它 · 无论怎样都要给任务写名称/描述/SOP · 出错时把原始异常写进日志，方便定位 | 标准库 | 否 |
| `src/api-probe/draft_multi_task.py` | 美团「申请采集点」：按区域逐个建 EgoOps 任务（每个任务带自己的素材和看图 SOP）。 之前的做法只建一个任务，把第一个区域的内容塞进去，其它区域直接丢掉了。 现在： 采集点字段（名称/地址/场景/描述）→ 写一次 每个任务（含采集点 | 标准库 | 否 |
| `src/api-probe/draft_resilient.py` | 建草稿改成「先写文字字段，再传素材」： 即使素材下载/看图/上传失败，任务也至少有名称、描述、SOP，不会出现空任务 | 标准库 | 否 |
| `src/api-probe/e2e-test.mjs` | 无文件头注释；按名称+代码判定：脚本，调用 /api/v1/__mock/sites，关键调用 `async function api(method, path, body, opts = {}) {` | 命令: node | 是（1 处） |
| `src/api-probe/edge_dump_egoops.py` | 无文件头注释；按名称+代码判定：Edge 配置/存储解析，关键调用 `data = open(f, "rb").read()` | 标准库 | 否 |
| `src/api-probe/edge_dump_ss.py` | 只保留可打印字符与换行 / 单独把所有 access_token 片段挖出来 | 标准库 | 否 |
| `src/api-probe/edge_ls_scan.py` | ASCII 可打印串 / UTF-16LE 串 | 标准库 | 否 |
| `src/api-probe/egoops_dl.mjs` | 无文件头注释；按名称+代码判定：脚本，关键调用 `const res = await fetch(url, { headers: { 'user-agent': 'Moz` | node:fs、node:path；命令: node | 否 |
| `src/api-probe/egoops_probe_sites.mjs` | 无文件头注释；按名称+代码判定：脚本，调用 /api/v1/users/me，关键调用 `const tok = JSON.parse(fs.readFileSync('egoops_token.json', ` | node:fs；命令: node | 否 |
| `src/api-probe/egoops_probe_tasks.mjs` | 无文件头注释；按名称+代码判定：脚本，调用 /api/v1/task-sets，关键调用 `const tok = JSON.parse(fs.readFileSync('egoops_token.json', ` | node:fs；命令: node | 否 |
| `src/api-probe/export_named.mjs` | 无文件头注释；按名称+代码判定：导出，关键调用 `const login = await (await fetch(B + '/api/auth/login', {` | node:fs；命令: node | 是（1 处） |
| `src/api-probe/export_site.mjs` | 无文件头注释；按名称+代码判定：导出，关键调用 `const login = await (await fetch(B + '/api/auth/login', {` | node:fs；命令: node | 是（1 处） |
| `src/api-probe/extract_oidc.py` | 从 raw 里找第一个 '{'，按 UTF-16LE 解码并用括号配对切出完整 JSON | 标准库 | 否 |
| `src/api-probe/extract_oidc2.py` | start 指向 UTF-16LE 值的第一个字节；读到下一个 \" (UTF-16LE) 为止 | 标准库 | 否 |
| `src/api-probe/fetch-scenes.mjs` | 无文件头注释；按名称+代码判定：抓取，调用 /api/v1/tet-snapshots/active，关键调用 `const tok = JSON.parse(fs.readFileSync('egoops_token.json', ` | node:fs；命令: node | 否 |
| `src/api-probe/fetch_pca.mjs` | 无文件头注释；按名称+代码判定：抓取，对象 viewer，关键调用 `const res = await fetch(url);` | node:fs；命令: node | 否 |
| `src/api-probe/fill_attach.py` | 带调试端口启动 Edge，等用户登录后，自动填「申请采集点」并点【保存草稿】。 思路：EgoOps 的登录态在 sessionStorage（关浏览器就丢），所以必须接管**同一个**浏览器窗口， 不能另开新实例。做法是 Edge 启动时加 | playwright；本地模块: agent_fill | 否 |
| `src/api-probe/fill_live.py` | 真机操作：用本机 Edge 配置打开 EgoOps，填「申请采集点」并点【保存草稿】（不提交审核）。 前置：Edge 必须先关闭 | playwright；本地模块: agent_fill | 否 |
| `src/api-probe/inspect2.js` | 无文件头注释；按名称+代码判定：结构查看，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 是（3 处） |
| `src/api-probe/list_ark_chat.py` | 从 Ark /models 里挑出支持 chat/completions 的模型 id | 标准库 | 否 |
| `src/api-probe/make_draft.py` | 按 EgoOps「申请采集点」真实表单结构生成草稿（HTML），任务级字段由 agent 补全 | 本地模块: agent_fill | 是（1 处） |
| `src/api-probe/members.js` | 无文件头注释；按名称+代码判定：脚本，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 是（6 处） |
| `src/api-probe/probe_787.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_api.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings/stats，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_api2.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_api3.py` | 翻页验证 | 标准库 | 否 |
| `src/api-probe/probe_ark_models.py` | 列出 Ark 可用模型（或试一批候选 id） | 标准库 | 否 |
| `src/api-probe/probe_ark_open.py` | 看这个 Ark 账号开通了哪些 chat 模型 | 标准库 | 否 |
| `src/api-probe/probe_daterange.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_dates.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_egoops_form.py` | 复制 Edge 配置 → 打开 EgoOps → 检查登录态并 dump 申请采集点弹窗结构（不提交） | playwright | 否 |
| `src/api-probe/probe_groupby.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings/group-stats，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_gui.ps1` | 无文件头注释；按名称+代码判定：接口探测 | bash | 否 |
| `src/api-probe/probe_llm.py` | 试探这个 key 能用哪个接口 + 哪个模型名（只看是否 200 且返回文本） | 标准库 | 否 |
| `src/api-probe/probe_matrix.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_mtsy.sh` | 无文件头注释；按名称+代码判定：接口探测，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/api-probe/probe_projects.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/projects，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_projects2.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/projects，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_scene.py` | 看看「采集场景分类」下拉展开后是什么结构 | playwright | 否 |
| `src/api-probe/probe_scene2.py` | 探测场景下拉的两级结构（只点下拉，不保存） | playwright | 否 |
| `src/api-probe/probe_scene3.py` | 探测：场景弹层结构 + 文件 input | playwright | 否 |
| `src/api-probe/probe_stats.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings/stats，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_task_actor.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings/group-stats，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_tet.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/recordings/group-stats，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_tet2.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/tet-snapshots/active，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_tet_depth.py` | 看 EgoOps 的 TET 分类树到底有几层 | 本地模块: egoops_auth、tls | 否 |
| `src/api-probe/probe_vendor.py` | 无文件头注释；按名称+代码判定：接口探测，调用 /api/v1/vendors，关键调用 `TOKEN = json.load(open(r"C:\Users\Administrator\Documents\de` | 标准库 | 否 |
| `src/api-probe/probe_vision.py` | 测哪个 Ark 模型能读图（vision） | PIL | 否 |
| `src/api-probe/replay_auth.py` | 用存下来的登录态直接开浏览器，验证是否免登录 | playwright | 否 |
| `src/api-probe/scan_bases.js` | 无文件头注释；按名称+代码判定：扫描，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 否 |
| `src/api-probe/seed.mjs` | 无文件头注释；按名称+代码判定：造数，关键调用 `async function api(method, path, body) {` | 标准库 | 否 |
| `src/api-probe/sim_chunk.mjs` | 无文件头注释；按名称+代码判定：仿真，关键调用 `const r = await fetch(BASE + p, opt);` | node:fs；命令: node | 是（1 处） |
| `src/api-probe/sim_upload.mjs` | 无文件头注释；按名称+代码判定：仿真，关键调用 `const req = (p, opt = {}) => fetch(BASE + p, opt);` | node:fs、node:path；命令: node | 是（1 处） |
| `src/api-probe/sim_viewer.py` | 模拟查看器：拉列表 → 厂商解析 → 质检 → 导出 → 建草稿 | 本地模块: api、egoops_draft、extras | 是（1 处） |
| `src/api-probe/test-upload.mjs` | 无文件头注释；按名称+代码判定：测试，关键调用 `async function api(method, path, body, opts = {}) {` | 标准库 | 否 |
| `src/api-probe/test_browser_login.py` | 无文件头注释；按名称+代码判定：测试，关键调用 `sys.path.insert(0, r"C:\Users\Administrator\Documents\deepse` | 本地模块: egoops_gui | 否 |
| `src/api-probe/test_cdp.js` | 无文件头注释；按名称+代码判定：测试，关键调用 `const r = await fetch(url, { method });` | node:child_process、node:fs、node:os、node:path；命令: node | 否 |
| `src/api-probe/test_draft_live.py` | 实测：对「盛宴便利店」跑一遍多任务建草稿，并回查每个任务 | 本地模块: api、egoops_auth、egoops_draft、egoops_status | 是（1 处） |
| `src/api-probe/test_draft_live2.py` | 对最新的「盛宴公寓」跑一遍完整建草稿，看真实失败点 | 本地模块: api、egoops_auth、egoops_draft | 是（1 处） |
| `src/api-probe/test_parse_token.py` | 无文件头注释；按名称+代码判定：测试，调用 /api/v1/recordings，关键调用 `sys.path.insert(0, r"C:\Users\Administrator\Documents\deepse` | 本地模块: egoops_gui | 否 |
| `src/api-probe/test_sop_rows.py` | 把「看图」生成的任务名/描述/SOP 写进已有草稿，验证 EgoOps 里是分开的多行 | 本地模块: agent_fill、api、egoops_auth、extras | 是（1 处） |
| `src/api-probe/update_draft_sop.py` | 用 GLM 生成的描述/SOP 更新 EgoOps 草稿（只改草稿，不提交） | 本地模块: agent_fill | 否 |
| `src/api-probe/verify-prod-e2e.mjs` | 无文件头注释；按名称+代码判定：结果校验，关键调用 `async function api(method, path, body) {` | 标准库 | 是（1 处） |
| `src/api-probe/verify-prod.mjs` | 无文件头注释；按名称+代码判定：结果校验，关键调用 `const res = await fetch(BASE + path, {` | 命令: node | 是（2 处） |
| `src/api-probe/verify_agg.js` | 无文件头注释；按名称+代码判定：结果校验，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 是（1 处） |

## table-schema（11）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/table-schema/add_fields.sh` | 无文件头注释；按名称+代码判定：新增功能/字段，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/add_ingest_field.sh` | 无文件头注释；按名称+代码判定：新增功能/字段，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/create_table.sh` | 无文件头注释；按名称+代码判定：建表，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/create_table_dryrun.sh` | 无文件头注释；按名称+代码判定：建表，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/inspect_capacity.js` | 无文件头注释；按名称+代码判定：结构查看，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 是（1 处） |
| `src/table-schema/inspect_tables.js` | 无文件头注释；按名称+代码判定：结构查看，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 是（4 处） |
| `src/table-schema/recreate_table.sh` | 无文件头注释；按名称+代码判定：重建表，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/recreate_table2.sh` | 无文件头注释；按名称+代码判定：重建表，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/recreate_table3.sh` | 无文件头注释；按名称+代码判定：重建表，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/recreate_table4.sh` | 无文件头注释；按名称+代码判定：重建表，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |
| `src/table-schema/verify_table.sh` | 无文件头注释；按名称+代码判定：结果校验，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli | 是（1 处） |

## data-backfill（12）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/data-backfill/check_storage.py` | 查看服务器上「数据库记录」和「磁盘文件」是否一致（有没有删不掉/对不上的备份） | 标准库 | 否 |
| `src/data-backfill/cleanup_empty_sites.py` | 空采集点处理： · 删除勾选时，如果勾的采集点里一个文件都没有 → 提示并可直接删除这些空采集点 · 菜单「采集点 → 清理空采集点（0 文件）」一键清掉所有空壳 | 标准库 | 否 |
| `src/data-backfill/diag_data.sh` | 无文件头注释；按名称+代码判定：远程诊断，关键调用 `/usr/local/bin/lark-cli base +record-list --base-token "$BAS` | bash + lark-cli、node | 否 |
| `src/data-backfill/import_scenes.py` | 导入新一版「场景分类」Excel，自动比对差异并保留各厂商配置。 用法： python tools/import_scenes.py "C:\\path\\MT-EGO TET v2.3 场景分类.xlsx" 做的事： 1. 读新表的 do | openpyxl | 否 |
| `src/data-backfill/import_vendor_scenes.py` | 按厂商导入各自的场景分类表（每个厂商一套大类/分类，互不影响）。 用法： python tools/import_scenes.py --vendor KWQZB "D:\\美团.xlsx" # 美团自己的分类 python tools/i | openpyxl | 否 |
| `src/data-backfill/importer_three_level.py` | 导入脚本支持三种表头： 大类 + 场景 （现在美团这份） 大类 + 分类 + 场景 （有的厂商是三级） 带三级时，items 里会多一个 group 字段，App 会显示三个下拉 | 标准库 | 否 |
| `src/data-backfill/rebuild_scenes.py` | 用官方 Excel 重建场景分类表（12 个 domain / 254 个 scene），并尽量映射回 TET path | openpyxl | 否 |
| `src/data-backfill/restore_deletes.py` | 无文件头注释；按名称+代码判定：恢复被删代码，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/data-backfill/test_delete_frees_disk.py` | 受控实验：上传一个 200KB 测试文件 → 看磁盘 → 删除 → 再看磁盘，证明删除真的清理服务器备份 | 本地模块: api、tls | 是（1 处） |
| `src/data-backfill/verify_cross.sh` | 无文件头注释；按名称+代码判定：结果校验，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli、python3 | 是（1 处） |
| `src/data-backfill/verify_final.sh` | 无文件头注释；按名称+代码判定：结果校验，关键调用 `L=/usr/local/bin/lark-cli` | bash + lark-cli、python3 | 是（1 处） |
| `src/data-backfill/verify_storage_consistency.py` | 核对：数据库里的文件记录 vs 磁盘上的实际文件（找出“删了还在”或“记录在没文件”） | 标准库 | 否 |

## ui-patch（139）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/ui-patch/add_invite_tab.py` | 无文件头注释；按名称+代码判定：新增功能/字段，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/add_invites_server.py` | ---------------- 1) db.mjs：邀请码表 + sites.vendor / collectors.vendor ---------------- / 迁移：sites.vendor / collectors.vendo | 标准库 | 否 |
| `src/ui-patch/add_login_check.py` | 修当前崩溃（var_* 未初始化 / Entry 插入重复），并加：启动即检查 EgoOps 登录态，掉了立刻提示登录 | 标准库 | 否 |
| `src/ui-patch/add_merged_prefix.py` | 无文件头注释；按名称+代码判定：新增功能/字段，对象 viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/add_vendor_site.py` | 1) 建采集点时写入厂商（来自采集员的邀请码） / 2) 采集点列表支持按厂商过滤 | 标准库 | 否 |
| `src/ui-patch/add_vendor_viewer.py` | ---------------- api.py：邀请码 + 厂商 ---------------- | 标准库 | 否 |
| `src/ui-patch/add_vision_sop.py` | 压成小图再送模型，省 token | PIL | 否 |
| `src/ui-patch/app2_complete.py` | app2 补全：缩略图回调防崩、建草稿、质检、导出 CSV | 本地模块: egoops_draft | 否 |
| `src/ui-patch/audit_dialogs.py` | 逐个打开对话框，检查按钮文字/尺寸是否正常（防止再出现空按钮） | 本地模块: app | 否 |
| `src/ui-patch/auto_sync_drafts.py` | 每次刷新列表，自动核对草稿是否还在： · 还在 → 显示「草稿/待审核/已通过」+ 号 · 已被删（404）→ 清掉本地记录，显示「未建」 · 登录态失效 → 静默跳过，不打扰 | 标准库 | 否 |
| `src/ui-patch/clean_entry_left.py` | 清掉重做后残留的旧控件引用 | 标准库 | 否 |
| `src/ui-patch/delete_rework.py` | 彻底重做「勾选→删除/下载」： · 统一解析：勾采集点 / 勾任务 / 勾文件，三种都支持，一次请求按需拉取 · 任何异常都弹出来（不再静默） · 删除前弹出「预览清单」窗口：列出要删的文件名，确认后才删 · 窗口标题带版本号，方便确认装的 | 标准库 | 否 |
| `src/ui-patch/empty_msg.py` | 空结果提示改成逐条列出每个采集点有多少文件；并在解析报告里带上明细 | 标准库 | 否 |
| `src/ui-patch/file_list_view.py` | 去掉图片预览，素材改成清单表格（勾选 + 文件名 + 类型 + 大小 + 时间） | 标准库 | 否 |
| `src/ui-patch/fix_async_preview.py` | 后台线程下载照片，绝不阻塞界面 | PIL | 否 |
| `src/ui-patch/fix_bar_label.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_canvas.py` | 无文件头注释；按名称+代码判定：缺陷修复，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_cascade_and_media.py` | 1) 勾选父级后，子节点（含尚未展开加载的）也跟着勾 2) 建草稿后回查任务，素材数量不一致会明确提示 | 标准库 | 否 |
| `src/ui-patch/fix_cert_bom.py` | 去掉证书文件的 BOM/CRLF——Android 解析带 BOM 的 PEM 会失败（https 一直握手不上的真因） | 标准库 | 是（2 处） |
| `src/ui-patch/fix_checkbox_cascade.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_checked_fallback.py` | 勾了采集点但没展开时，「下载勾选 / 删除勾选」也能用： 拿不到已加载文件时，直接用勾选的采集点去服务器取文件列表 | 标准库 | 否 |
| `src/ui-patch/fix_columns2.py` | 1) 列宽收窄，保证 1100px 窗口下所有列都能放下 / 2) 选中行时，把完整信息显示在上方那一行，避免被列宽截断 | 标准库 | 否 |
| `src/ui-patch/fix_delete_checked.py` | 修两个问题： 1) 刷新时在工作线程里调 root.after() 导致异常（草稿自动同步因此失效） 2) 删除勾选：勾了采集点但没展开时拿到 0 个文件 → 现在自动去服务器取该采集点的文件再删 | 标准库 | 否 |
| `src/ui-patch/fix_delete_v2.py` | 谨慎地改三处（按缩进定位方法边界，避免切掉别的方法） | 标准库 | 否 |
| `src/ui-patch/fix_download_tls.py` | 下载走 tls.urlopen（服务器是自签证书，必须带固定证书的 context） | 标准库 | 否 |
| `src/ui-patch/fix_download_ux.py` | 下载流程的几个体验修正： 1) 目录名取勾选采集点的名字，而不是固定的"采集点" 2) 开始下载前把状态写清楚，失败时把原因带到提示里 3) 目录选择框强制置前，避免"点了没反应"" | 标准库 | 否 |
| `src/ui-patch/fix_draft.py` | 把草稿修正成正确内容：真实任务名、真实素材上传、地址不编造 | 本地模块: agent_fill | 是（1 处） |
| `src/ui-patch/fix_draft_done_ui.py` | 查看器的建草稿成功弹窗改成多任务版（原来读 res["hours"]/res["sop"]） | 标准库 | 否 |
| `src/ui-patch/fix_dup_detect.py` | 重复检测：只在同一任务内比较，且收紧到 3 位距离 | 标准库 | 否 |
| `src/ui-patch/fix_dup_upload.py` | 删掉重复的旧上传块（174-188 行），并给素材加数量上限（EgoOps：照片≤8、视频≤3） | 标准库 | 否 |
| `src/ui-patch/fix_dup_v2.py` | 1) 指纹从 8x8 升级到 16x16（256 位），更能区分相似但不相同的照片 / 2) 比较时带上清晰度差异：清晰度差太多的不算重复（避免"模糊版 vs 原图"误报） | 标准库 | 否 |
| `src/ui-patch/fix_entry_refs.py` | 修：代码里还在用 ent_server/ent_name 这些旧控件，改成 var_server/var_name | 标准库 | 否 |
| `src/ui-patch/fix_ffmpeg_download.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_footer_order.py` | 修底部状态栏看不见：footer 必须在可伸展的 body 之前 pack(side=bottom) | 标准库 | 否 |
| `src/ui-patch/fix_import_deploy.py` | 无文件头注释；按名称+代码判定：缺陷修复，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_init_state.py` | 1) 初始化容器 / 2) _poll 里捕获异常并显示，别静默吞掉 | 标准库 | 否 |
| `src/ui-patch/fix_lambda_e.py` | 把在 except 里创建、随后在 lambda 里引用 e 的写法，改成绑定默认参数 / 通用兜底：把所有 "lambda: ... % e" 和 "lambda: ... , e)" 形式改为默认参数绑定 | 标准库 | 否 |
| `src/ui-patch/fix_login_window.py` | 让「点击登录」一定能弹出可见的浏览器窗口： · 先清掉残留的临时登录窗口 · 用独立配置 + 调试端口新开一个窗口，并置到最前 | 标准库 | 否 |
| `src/ui-patch/fix_preview_impl.py` | 选中照片时在预览区显示 | PIL | 否 |
| `src/ui-patch/fix_preview_layout.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_progress_bar.py` | 修进度条一直满：下载把 maximum 改成了文件个数，草稿又按 0-100 写 value，导致溢出。 统一成 maximum=100，value 一律是百分比 | 标准库 | 否 |
| `src/ui-patch/fix_relogin_capture.py` | 登录抓取修正： · 只有拿到有效 token 才覆盖保存（避免把好数据冲掉） · 等 login 页面真正结束 + sessionStorage 里出现 oidc.user 才算成功 | 标准库 | 否 |
| `src/ui-patch/fix_settings_layout.py` | 1) 底部按钮条提前 pack（否则被 Notebook 的 expand 挤成一条缝，按钮文字看起来是空的） / 去掉后面重复创建 bar 的那两行 | 标准库 | 是（1 处） |
| `src/ui-patch/fix_table_scroll.py` | 1) 表格加横向滚动条并让列宽自适应，避免文字被切 2) 不再自动弹登录（只有点了才登录） | 标准库 | 否 |
| `src/ui-patch/fix_target_site.py` | 修：勾了采集点但没点行 → 提示"先选中"。 1) 点勾选框时同时把该行设为选中 2) 建草稿 / 质检 / 下载全部：优先当前行，没有就用勾选的第一条 | 标准库 | 否 |
| `src/ui-patch/fix_taskname.py` | 根据画面内容和步骤反推一个 8~14 字任务名；纯文本调用，快且便宜 | 标准库 | 否 |
| `src/ui-patch/fix_thumb_thread.py` | 修缩略图：PhotoImage 必须在主线程创建（原来在线程里建，静默失败） | PIL | 否 |
| `src/ui-patch/fix_transcode_logic.py` | 无文件头注释；按名称+代码判定：缺陷修复，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/fix_tree_errors.py` | ---------- 1) 修 'NoneType' object is not subscriptable：占位子节点也以 site: 开头 ---------- / ---------- 2) 列宽 + 横向滚动条，内容不再被挤掉 -- | 标准库 | 否 |
| `src/ui-patch/fix_tree_expand.py` | 点三角展开时焦点不一定落在这一行，兜底找「已展开但没加载过」的采集点 | 标准库 | 否 |
| `src/ui-patch/fix_ui_kwargs.py` | 找到现有 ui 定义并让它接受 kwargs / 把入队内容也带上 kwargs | 标准库 | 否 |
| `src/ui-patch/fix_vendor_reset.py` | 修：do_refresh 里误把 vendor_names / vendor_systems 清空了（导致厂商列一直显示"未登记"） | 标准库 | 否 |
| `src/ui-patch/fix_vendor_scenes_fn.py` | 把 vendorScenes() 补进 server.mjs（SCENES 是 try/catch 里赋值，之前的插入点不匹配） | 标准库 | 否 |
| `src/ui-patch/fix_video_metrics.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/harden_checked_files.py` | checked_files 加固：占位行(…:loading)可能已被删除，直接访问会抛 TclError， 导致「删除勾选/下载勾选」整段静默失败。全部 try 包住并跳过占位行 | 标准库 | 否 |
| `src/ui-patch/insert_login_block.py` | 把登录态检查那一段插到正确位置（def _style 之前） | 标准库 | 否 |
| `src/ui-patch/invite_collector.py` | 无文件头注释；按名称+代码判定：脚本，对象 server.mjs、db.mjs，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/invite_serverless.py` | ---------- 1) db.mjs：sites 增加 invite 列 ---------- / ---------- 2) server.mjs ---------- | 标准库 | 否 |
| `src/ui-patch/invite_tab_local.py` | 用本地映射重写「邀请码」设置页（原来的页会调服务器 /api/invites） | 标准库 | 否 |
| `src/ui-patch/invite_viewer_local.py` | 本地配置：{"ZJMEIYI": "湛江盛宴科技有限公司"} | 标准库 | 否 |
| `src/ui-patch/login_banner.py` | 登录态失效时不要弹模态框（打扰），改成右侧红色提示 + 按钮；建草稿时才拦 | 标准库 | 否 |
| `src/ui-patch/merge_site_into_task1.py` | EgoOps 任务映射改为： 任务1 = 门头照/全景照片/全景视频 + 第一个区域的全套素材 任务2..N = 各区域自己的素材（不再带门头/全景） 平台上限：单个任务照片 ≤8、视频 ≤3，合并后超了会截断并打日志 | 标准库 | 否 |
| `src/ui-patch/merge_tree.py` | ---------- 1) 布局：左右两表合并成一个树 ---------- | 标准库 | 否 |
| `src/ui-patch/merge_tree_cleanup.py` | 1) __init__ 增加容器 / 2) 删掉旧的站点选择/文件列表方法块（on_site_select ... selected_file） | 标准库 | 否 |
| `src/ui-patch/merge_tree_cleanup2.py` | 1) 删掉旧的「勾选框」整段（含重复的 on_site_click / delete_* / download_checked_sites / on_file_click 等） / 2) selftest 用 tree | 标准库 | 否 |
| `src/ui-patch/patch_addr_column.py` | 1) 采集点列表加「地址」列，并重排列宽 / 2) 填充时给地址赋值 | 标准库 | 否 |
| `src/ui-patch/patch_addr_fix.py` | 直辖市 / 省掉市名：直接在这个省的所有区县里找 | 标准库 | 否 |
| `src/ui-patch/patch_addr_viewer.py` | ---------- 1) 查看器草稿显示拆解后的地址 ---------- / 草稿 HTML：地址后面加拆解提示 | 本地模块: address_parse | 否 |
| `src/ui-patch/patch_api_draft.py` | 无文件头注释；按名称+代码判定：代码补丁，调用 /api/v1/task-sets/allocate-draft，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/patch_auth_reuse.py` | 把保存的 localStorage / sessionStorage 在页面加载前写回去 | 标准库 | 否 |
| `src/ui-patch/patch_autorefresh.py` | 用专用浏览器配置静默完成 SSO 登录并读取新令牌 | 标准库 | 否 |
| `src/ui-patch/patch_browser_login.py` | 登录后从专用配置的 Session Storage 里读 oidc 令牌（无需 Cookie 数据库） | 标准库 | 否 |
| `src/ui-patch/patch_check_cli.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_crashlog.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_demo.py` | 弹层（下拉选项）渲染在 dialog 之外，必须用 page 级定位 | 标准库 | 否 |
| `src/ui-patch/patch_demo2.py` | Escape 会关掉弹窗 —— 去掉 / 打开弹窗的判断改成更稳的写法，并在关闭时重开 | 标准库 | 否 |
| `src/ui-patch/patch_draft.py` | 1) 按钮：生成草稿 / 2) 草稿逻辑 | 标准库 | 否 |
| `src/ui-patch/patch_fill_button.py` | 1) 底部第三行：申请采集点（自动填表） / 2) 填表方法 | 标准库 | 否 |
| `src/ui-patch/patch_fill_fields.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/patch_fill_fields2.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/patch_gui_creds.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_hidden.py` | main(): --hidden 时隐藏控制台窗口（供定时任务静默运行） | 标准库 | 否 |
| `src/ui-patch/patch_hideconsole.py` | GUI 模式下隐藏控制台窗口（打包为 console 版时用） | 标准库 | 否 |
| `src/ui-patch/patch_identity.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_ingest.py` | 全量扫描，统计每个 (task_id, 执行者) 的最新入库时间 created_at | 标准库 | 否 |
| `src/ui-patch/patch_login.py` | 从粘贴内容中提取 access_token：支持纯 JWT、Authorization 头、整段 cURL | 标准库 | 否 |
| `src/ui-patch/patch_login_dialog.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_msg.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_replace.py` | const exists = db.prepare('SELECT * FROM sites WHERE site_key = ?').get(key); if (exists) return send(res, 200, { site:  | 标准库 | 否 |
| `src/ui-patch/patch_task_area.py` | const tname = String(t && t.name \|\| '').trim() \|\| `任务${i + 1}`; db.prepare('INSERT INTO tasks (id, site_id, idx, name, n | 标准库 | 否 |
| `src/ui-patch/patch_title.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 egoops_gui.py，关键调用 `s = io.open(p, encoding="utf-8").read()` | 标准库 | 否 |
| `src/ui-patch/patch_transcode_hook.py` | 1) 顶部加转码工具引入 / 2) complete 后异步触发转码 | 标准库 | 否 |
| `src/ui-patch/patch_viewer_checks.py` | 1) 采集点列表加勾选列 / 2) 底部两行 | 标准库 | 否 |
| `src/ui-patch/patch_viewer_delete.py` | 1) 底部改为三行：文件操作 / 采集点操作 / 其他 | 标准库 | 否 |
| `src/ui-patch/patch_viewer_layout.py` | 1) 底部按钮条先占位，避免被上面的列表挤掉 / 2) 预览区不要太高，给按钮留空间 | 标准库 | 否 |
| `src/ui-patch/patch_wizard.py` | 返回 (ok, 说明) | 标准库 | 是（3 处） |
| `src/ui-patch/polish_all.py` | 整体收尾打磨： 1) 版本号进标题与状态栏（v16） 2) 删除采集点：逐个进度 + 最终汇总 + 一定刷新 3) 长任务结束时一定清掉「正在…」文字（异常也清） | 标准库 | 否 |
| `src/ui-patch/polish_ui3.py` | 收尾：右栏加宽、表头/列宽、登录提示缩短，避免文字被切 | 标准库 | 否 |
| `src/ui-patch/polish_viewer.py` | 1) 菜单里的「刷新 EgoOps 登录态」直接执行，不再只是打开设置 / 2) 双击采集点行 = 展开/收起 | 标准库 | 否 |
| `src/ui-patch/rebuild_body.py` | 无文件头注释；按名称+代码判定：重建数据，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/redesign_viewer.py` | ---------- 顶部工具条 ---------- | 标准库 | 否 |
| `src/ui-patch/redesign_viewer2.py` | 查看器界面重做：顶部品牌条 + 四步引导 + 右侧说明面板 + 底部主操作 | 标准库 | 否 |
| `src/ui-patch/redesign_viewer3.py` | 界面二轮重做：换成现代 ttk 主题（sv-ttk），布局简化成「列表 + 大按钮面板」。 要点： · 主题：sv-ttk light（Windows 11 风格），失败自动回退 · 去掉花哨的四步卡片，改成一条状态条 + 一个大按钮（当前 | sv_ttk | 否 |
| `src/ui-patch/remove_name_field.py` | 无文件头注释；按名称+代码判定：移除，对象 viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/remove_transcode_hook.py` | 去掉转码钩子（服务器只存不转），避免小机器被 CPU 打满 | 标准库 | 否 |
| `src/ui-patch/server_apk_route.py` | 服务器：/api/app/version 版本信息 + /apk/latest.apk 下载（支持断点） | 标准库 | 否 |
| `src/ui-patch/server_orphan_files.py` | 服务器：把「没有归属任务」的历史文件也显示出来（挂在「未归类」任务里）。 原因：老数据的 files.task_id 是空的，siteView 只按 task_id 分组， 这些文件在查看器里就永远看不到，于是勾采集点显示「没有文件」 | 标准库 | 否 |
| `src/ui-patch/server_vendor_names.py` | 服务器：/api/vendor-names 返回邀请码 → 厂家名（查看器显示用，公开） | 标准库 | 否 |
| `src/ui-patch/server_vendor_own_scenes.py` | 服务器：每个厂商可以有自己的分类表 /opt/egoops/relay/vendor_scenes/<CODE>.json | 标准库 | 否 |
| `src/ui-patch/set_scene.py` | 在当前打开的弹窗里，把采集场景分类选上（餐饮 / 餐厅） | playwright | 否 |
| `src/ui-patch/set_vendor_scenes.py` | 按邀请码给厂商分配可见的大类（写 relay/vendor_scenes.json，服务器和 App 都读它） | 标准库 | 否 |
| `src/ui-patch/shot_settings.py` | 打开设置窗口并截图，验证底部按钮和三个页签 | PIL；本地模块: app | 否 |
| `src/ui-patch/shot_sop_rows.py` | 打开指定草稿的任务详情，截图看 SOP 是不是一行一条 | playwright | 否 |
| `src/ui-patch/shot_tree.py` | 连上服务器、展开第一个采集点，截整窗，检查列对齐 | PIL；本地模块: app | 否 |
| `src/ui-patch/shot_viewer.py` | 启动查看器 → 置前 → 截屏，用于展示界面 | PIL | 否 |
| `src/ui-patch/show_draft.py` | 用保存的登录态打开 EgoOps，定位到指定草稿并截图（只读，不提交） | playwright | 否 |
| `src/ui-patch/slim_toolbar.py` | 顶部「设置」按钮去掉（菜单里已有），减少重复 | 标准库 | 否 |
| `src/ui-patch/slim_viewer_ui.py` | 兼容旧代码引用的控件（不再显示，功能移到菜单） | 标准库 | 否 |
| `src/ui-patch/snap_state.py` | 无文件头注释；按名称+代码判定：状态快照，关键调用 `b = p.chromium.connect_over_cdp(CDP)` | playwright | 否 |
| `src/ui-patch/storage_tools.py` | 服务器加「存储体检 + 清理」接口；查看器加菜单入口 | 标准库 | 否 |
| `src/ui-patch/task_level_checks.py` | 删除/下载支持「勾任务行」： 树上的任务行 iid 形如 site:<id>:task:<taskId>。 勾了任务但没展开时，也能按任务去服务器取文件 | 标准库 | 否 |
| `src/ui-patch/test_checkbox.py` | 验证勾选级联：勾采集点 → 下级全勾；取消一个文件 → 采集点自动取消 | 本地模块: app | 否 |
| `src/ui-patch/test_download_checked.py` | 模拟点一次「下载勾选」，看到底卡在哪（不弹目录框，直接注入目标目录） | 本地模块: app | 否 |
| `src/ui-patch/tune_cols2.py` | 无文件头注释；按名称+代码判定：参数微调，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/tune_layout.py` | 无文件头注释；按名称+代码判定：参数微调，对象 app.py、viewer，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/ui-patch/vendor_scenes_server.py` | 服务器：/api/scenes?vendor=CODE 按厂商返回可见大类 | 标准库 | 否 |
| `src/ui-patch/vendor_systems.py` | 服务器：厂商 → 提交系统（美团 EgoOps / 其它系统） | 标准库 | 否 |
| `src/ui-patch/viewer_search_status.py` | 查看器：搜索框 + 日期筛选 + 草稿状态回查 | 标准库 | 否 |
| `src/ui-patch/viewer_vendor_gate.py` | 查看器：只有美团（KWQZB）走 EgoOps；其它厂商的提交流程没接入，按钮直接拦住 | 标准库 | 否 |
| `src/ui-patch/viewer_vendor_names.py` | 查看器：厂商名从服务器拿（邀请码 → 厂家），不再要求本地配映射 | 标准库 | 否 |
| `src/ui-patch/vision_taskname.py` | 1) 提示词：连任务名称也由画面决定，SOP 一行一条 / 2) 返回值带上 name | 标准库 | 否 |
| `src/ui-patch/wire_batch_qc_export.py` | ---------- 1) 按钮 ---------- / ---------- 2) 方法 ---------- | 标准库 | 否 |
| `src/ui-patch/wire_draft_tracking.py` | ---------- 1) 导入 extras ---------- / ---------- 2) 表格加 EgoOps 状态列 ---------- | 标准库 | 否 |
| `src/ui-patch/wire_login_refresh.py` | 设置-服务器页加「刷新 EgoOps 登录态」 | 标准库 | 否 |
| `src/ui-patch/wire_oneclick.py` | 一条龙：建草稿 + 填字段 + 转码上传素材 + 写 SOP，不提交审核 | 标准库 | 否 |
| `src/ui-patch/wire_tls_viewer.py` | 服务器用的是自签证书，客户端固定校验这张证书（不信任其它任何 CA） | 标准库 | 是（4 处） |
| `src/ui-patch/wire_transcode_pc.py` | ---------- 1) transcode_pc: 换成国内镜像（27MB.gz，比 GitHub 快很多） ---------- | 标准库 | 否 |
| `src/ui-patch/wire_vendor_filter.py` | 1) 刷新时按厂商过滤 / 2) 连上之后填充厂商下拉 | 标准库 | 否 |
| `src/ui-patch/wire_vision_draft.py` | 1) 导入视觉生成 / 2) 把「生成内容」挪到素材下载之后，并优先用素材 | 标准库 | 否 |

## deploy（22）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/deploy/01-install-node.sh` | 无文件头注释；按名称+代码判定：脚本 | bash + curl、node | 否 |
| `src/deploy/02-check-net.sh` | 无文件头注释；按名称+代码判定：脚本，调用 /api/v1/users/me | bash + curl | 否 |
| `src/deploy/03-install-relay.sh` | 无文件头注释；按名称+代码判定：脚本，对象 server.mjs | bash + curl、node、systemctl | 否 |
| `src/deploy/04-nginx-relay.py` | 在 nginx 默认 server 块里加 /relay/ 反代到本机 18090（幂等、带备份） | 标准库 | 否 |
| `src/deploy/05-harden.sh` | 1) 备份脚本试跑 / 2) 每日 03:10 备份 | bash + crontab、curl、nginx、node、systemctl | 否 |
| `src/deploy/06-switch-to-collect.sh` | 无文件头注释；按名称+代码判定：脚本 | bash + curl、nginx、systemctl | 否 |
| `src/deploy/07-install-ffmpeg.sh` | 无文件头注释；按名称+代码判定：脚本 | bash + curl、ffmpeg | 否 |
| `src/deploy/08-https-prep.sh` | 1) 装 acme.sh（纯 shell，不依赖 yum 源） / 2) 准备 webroot | bash + acme.sh、curl、nginx | 否 |
| `src/deploy/09-https-issue.sh` | 用 nip.io 域名给纯 IP 的服务器申请真证书（浏览器可信任） / 1) 加 acme 校验路径（80 端口） | bash + acme.sh、curl、nginx、systemctl | 是（1 处） |
| `src/deploy/10-https-selfsigned.sh` | 自签证书（IP SAN，CA:TRUE 便于 Android 信任），开启 443，保留 80 | bash + curl、nginx、openssl、systemctl | 是（1 处） |
| `src/deploy/config.prod.example.json` | 无文件头注释；按名称+代码判定：脚本 | bash | 是（1 处） |
| `src/deploy/deploy_v2.sh` | 规范化备份名 / 群白名单注释更新（CHAT_ID 已不再使用；CHAT_IDS 留空=任意群） | bash + systemctl | 否 |
| `src/deploy/deploy_v3.sh` | 无文件头注释；按名称+代码判定：脚本，关键调用 `s = open(p, encoding='utf-8').read()` | bash + python3、systemctl | 是（1 处） |
| `src/deploy/deploy_v4.sh` | 无文件头注释；按名称+代码判定：脚本，关键调用 `s = open(p, encoding='utf-8').read()` | bash + python3、systemctl | 否 |
| `src/deploy/deploy_v5.sh` | 无文件头注释；按名称+代码判定：脚本，关键调用 `s = open(p, encoding='utf-8').read()` | bash + python3、systemctl | 否 |
| `src/deploy/deploy_v6.sh` | 无文件头注释；按名称+代码判定：脚本，关键调用 `s = open(p, encoding='utf-8').read()` | bash + python3、systemctl | 否 |
| `src/deploy/deploy_v7.sh` | 无文件头注释；按名称+代码判定：脚本，关键调用 `s = open(p, encoding='utf-8').read()` | bash + python3、systemctl | 否 |
| `src/deploy/probe-ports.js` | 无文件头注释；按名称+代码判定：脚本 | http | 否 |
| `src/deploy/rescue_server.py` | 服务器卡住时，用更长的超时重连并清理转码进程 | paramiko | 是（2 处） |
| `src/deploy/setup_ssh_key.py` | 生成 SSH 密钥并装到服务器，之后不再用密码登录 | paramiko | 是（2 处） |
| `src/deploy/ssh_exec.py` | Minimal non-interactive SSH command runner (password auth). Usage: python ssh_exec.py "<command>" # run command python s | paramiko | 是（2 处） |
| `src/deploy/switch_ssh_key.py` | 根目录再放一份便于直接调用的说明 | 标准库 | 是（2 处） |

## bot（5）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/bot/check_bot_access.js` | 无文件头注释；按名称+代码判定：只读核查，关键调用 `const L = '/usr/local/bin/lark-cli';` | node:child_process；命令: lark-cli、node | 是（1 处） |
| `src/bot/health_bot.sh` | 无文件头注释；按名称+代码判定：脚本 | bash + systemctl | 否 |
| `src/bot/probe_bot.sh` | 无文件头注释；按名称+代码判定：接口探测 | bash + jq | 否 |
| `src/bot/probe_bot2.sh` | 无文件头注释；按名称+代码判定：接口探测 | bash | 否 |
| `src/bot/watch_bot.sh` | 无文件头注释；按名称+代码判定：脚本 | bash + systemctl | 否 |

## android（102）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/android/add_anticode.py` | 加一个「我们自己的防伪码」：素材文件的 SHA1 前 12 位，烧在水印角落。 这个码可以拿原文件重算校验，是真的防伪，不是抄别人的 | 标准库 | 否 |
| `src/android/add_area_pano.py` | 每个区域加一张「全景照片」，并全局提示用广角拍 | 标准库 | 否 |
| `src/android/add_crash_dialog.py` | 1) askTask 点击全程 try/catch，异常只提示不闪退 2) 启动时如果上次崩溃了，把崩溃堆栈弹出来（方便截图发我） | 标准库 | 否 |
| `src/android/add_crash_dialog2.py` | 加：启动时显示上次崩溃；askTask 点击整体 try/catch | 标准库 | 否 |
| `src/android/add_guides.py` | ---------- 1) 每个拍摄项的要点提示 ---------- / 拍摄页：加「拍摄要点」按钮（放在重拍/相册按钮同一行附近） | 标准库 | 否 |
| `src/android/add_invites_android.py` | ---------------- Store：记住厂商 ---------------- / ---------------- MainActivity ---------------- | 标准库 | 否 |
| `src/android/add_map_inset.py` | 把地图小图接进照片/视频水印： · 定位拿到后抓一张高德静态地图，缓存成本地文件 · 照片烧水印时贴右上角 · 视频 overlay 也贴（Uploader 读缓存文件） | 标准库 | 否 |
| `src/android/add_photo_watermark.py` | 照片加水印（地址 + 日期 + 时间 + 门店 + 采集员），样式接近「打卡水印相机」。 视频目前无法烧录（系统相机录的，App 拿不到画面），先做照片；视频另议 | 标准库 | 否 |
| `src/android/add_quality_gate.py` | 1) 拍完先质检，不合格就提示重拍 | 标准库 | 否 |
| `src/android/add_resume_thumbs.py` | ---------- 1) 上传完成后：留缩略图，删原文件（省空间） ---------- | 标准库 | 否 |
| `src/android/add_retry_resume.py` | ---------- 1) Uploader：单个文件失败重试（指数退避） ---------- / 在 run() 里换调用 | 标准库 | 否 |
| `src/android/add_shield.py` | 无文件头注释；按名称+代码判定：新增功能/字段，对象 WatermarkVideo.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/add_showarea_method.py` | 补上 showAreaForTask1 方法体（上一步因为字符串已存在被跳过） | 标准库 | 否 |
| `src/android/add_task_patch.py` | 1) 服务器：加 PATCH /api/sites/:id/tasks/:taskId（改任务名/区域） 2) App：填完区域后调用 syncTaskNames() | 标准库 | 否 |
| `src/android/add_upload_service.py` | MainActivity：上传开始时起前台服务，结束时停掉 | 标准库 | 否 |
| `src/android/add_variant_param.py` | build.ps1 增加 -Variant：生成换名换包的独立版本（例如「采集水印相机」） | 标准库 | 否 |
| `src/android/add_vendor_android_ui.py` | 1) 声明 tvVendor / 2) 开始页顶部加厂商行（放在内容最上面） | 标准库 | 否 |
| `src/android/add_version_label.py` | 1) 首页底部显示当前版本，方便确认装没装上 2) 选「以后再说」记住这个版本，同一版本不再反复弹 | 标准库 | 否 |
| `src/android/allow_cleartext.py` | 放行明文 http（作为 https 失败后的兜底），并把 https 的原始错误带出来 | 标准库 | 是（1 处） |
| `src/android/android_finish_check.py` | 兜底：拍完点「全部拍完」时，如果任务1 还没填区域/动作，先让人补填 | 标准库 | 否 |
| `src/android/android_merge_task1.py` | 安卓端也按同一规则：第一个区域并进「任务1」—— 任务1 = 门头照 + 全景照片 + 全景视频 + 该区域的对角2/任务照2/任务视频2 后面新增的区域才各自单独成任务 | 标准库 | 否 |
| `src/android/android_task1_9items.py` | 任务1 合成 9 项：门头照/全景照片/全景视频 + 该区域对角2/任务照2/任务视频2。 实现要点： · 新增任务类型 task1，shots 共 9 项 · 拍到第 3 项（三项全景）拍完时，自动弹「填区域和动作」，写回同一个任务 ·  | 标准库 | 否 |
| `src/android/app_update.py` | App：检查更新 + 下载 + 调系统安装器 | 标准库 | 否 |
| `src/android/app_vendor_scenes.py` | App：场景分类按邀请码从服务器取（失败退回内置全量） | 标准库 | 否 |
| `src/android/auto_area_prompt.py` | 流程：门头照+全景照片+全景视频拍完 → 自动弹出「填区域名称 + 区域动作」→ 再拍该区域 6 项 | 标准库 | 否 |
| `src/android/auto_grab_gallery.py` | 自动取回水印相机刚拍的文件： 1) 打开水印相机时记下时间戳 2) 回到 App 后，查询 MediaStore 里比该时间戳更新的最新照片/视频 3) 找到就直接导入（无需用户手点相册）；找不到才退回相册选择 4) 补上读取媒体权限 | 标准库 | 否 |
| `src/android/auto_load_scenes.py` | 邀请码改成自动加载分类：输入停顿 0.8 秒自动拉，去掉那个按钮 | 标准库 | 否 |
| `src/android/build_nocapture.py` | 新增「不拍摄收集」版本： · 构建开关 -NoCapture 生成独立包（com.egoops.collect.nocap，名称「不拍摄收集」） · 该版本：不能拍照/录像，只能从相册选；且不给素材加水印（素材自带水印） · 不自动更新（避 | 标准库 | 否 |
| `src/android/build_version_sync.py` | build.ps1 里自动把 AndroidManifest 的版本号写进 BuildConfigVersion.java | 标准库 | 否 |
| `src/android/bump61.py` | 无文件头注释；按名称+代码判定：版本号递增，对象 AndroidManifest.xml、build.ps1，关键调用 `m = io.open('android/AndroidManifest.xml', encoding='utf-8')` | 标准库 | 否 |
| `src/android/bump72.py` | 无文件头注释；按名称+代码判定：版本号递增，对象 AndroidManifest.xml、build.ps1，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/bump73.py` | 无文件头注释；按名称+代码判定：版本号递增，对象 AndroidManifest.xml、build.ps1，关键调用 `m = io.open('android/AndroidManifest.xml', encoding='utf-8')` | 标准库 | 否 |
| `src/android/bump74.py` | manifest / build.ps1：版本参数 + 输出名 | 标准库 | 否 |
| `src/android/call_watermark_app.py` | 「不拍摄收集」版加一键调用水印相机： · 扫描已安装应用里名字带「水印」的（今日水印相机等） · 点按钮直接打开它；回到本 App 时自动弹出相册选择 · 找不到就提示去应用商店装 | 标准库 | 否 |
| `src/android/dedup_methods.py` | 删掉重复的旧 stampWatermark（保留新版）和重复的 showAreaForTask1 | 标准库 | 否 |
| `src/android/dedupe2.py` | 去掉重复方法：每个方法保留一个（优先保留靠后的新版本 useLocation/startGps）， 然后重新编译 | 标准库 | 否 |
| `src/android/dynamic_time.py` | 水印的时间改成「素材拍摄那一刻」： · 照片/视频在拍完落盘时记录 capturedAt · 水印按 capturedAt 画时间（不再用「加水印那一刻」） · 视频是整段恒定时间（同真实水印相机：显示开拍时间） | 标准库 | 否 |
| `src/android/enhance_nocap.py` | 增强「不拍摄收集」版： 1) 批量导入：一次选多张/多段，按顺序填满当前区域剩下的项 2) 自动取回增强：严格时间窗找不到时，放宽到 30 分钟 + 文件名前缀 3) 拍摄页显示本机使用的拍摄 App 名称 | 标准库 | 否 |
| `src/android/finish_anticode.py` | 补完防伪码接线（MainActivity + Uploader），锚点用真实文本 | 标准库 | 否 |
| `src/android/fix_asktask_npe.py` | 修「再拍一个区域/任务」闪退：presetArea 为空指针，以及 renderShot 的越界防护 | 标准库 | 否 |
| `src/android/fix_backpage.py` | 记一个当前页号，返回键判断用 | 标准库 | 否 |
| `src/android/fix_camera_perm.py` | 修「某项只能从相册上传、拍照没反应」： 1) 相机/录像 Intent 失败时自动退回相册选择，并提示原因 2) 相机权限被永久拒绝时，弹窗引导去设置开启 | 标准库 | 否 |
| `src/android/fix_capture_call.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 MainActivity.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/fix_collector_ref.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 MainActivity.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/fix_columns_and_method.py` | 修两处： 1) 表格列错位：fill_sites 还在按旧列（8 列）塞数据，新表只有 6 列 2) 补上 App 里漏掉的 syncTaskNamesAsync 方法 | 标准库 | 否 |
| `src/android/fix_crash_lambda.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 MainActivity.java，关键调用 `s = io.open(P, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/fix_galleryonly.py` | 在按钮前提前声明 / 后面那处重复声明去掉（变成直接使用） | 标准库 | 否 |
| `src/android/fix_gps_accuracy.py` | 定位准确性修正： 1) WGS84 → GCJ02 再查地图/逆地理（原来直接用 WGS84，红点会偏 100~500 米） 2) 地址改用高德逆地理（国内更准，且与地图一致） 3) 尽量等一次「新鲜定位」，并记录精度 | 标准库 | 否 |
| `src/android/fix_outapk.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 build.ps1，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/fix_rename_pkg.py` | 改用 aapt2 的 --rename-manifest-package： 清单里保持 com.egoops.collect（R 类不变），只把安装包名改成 .nocap | 标准库 | 否 |
| `src/android/fix_rpackage.py` | 不拍摄版：清单包名变了，R 类默认也会跟着变，导致 Java 里 R 找不到。 用 aapt2 --custom-package 把 R 固定回 com.egoops.collect | 标准库 | 否 |
| `src/android/fix_scene_leftover.py` | 删掉 refreshSceneSpinner 之后遗留的残段（626-640 行） | 标准库 | 否 |
| `src/android/fix_scenes_addr.py` | 1) 网络拉不到场景时，用 APK 内置的 scenes.json 兜底 | 标准库 | 否 |
| `src/android/fix_start_restore.py` | 启动时只在「真的没拍完/没传完」时才恢复上次内容；已完成的采集点自动清空，从空白开始 | 标准库 | 否 |
| `src/android/fix_task_name_check.py` | 无文件头注释；按名称+代码判定：缺陷修复，对象 MainActivity.java，关键调用 `s = io.open(P, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/fix_tip_scope.py` | 把提示条挂到 card 里（bottom 不在这个作用域） / 在按钮加到 card 之后插入提示条 | 标准库 | 否 |
| `src/android/fix_update_size_check.py` | 修下载校验：按服务器给的大小比对，而不是写死 100KB（APK 才 95KB，被误判成不完整） | 标准库 | 否 |
| `src/android/fix_vendor_switch.py` | 1) 服务器：厂商自己的表也要按 vendor_scenes.json 里的大类过滤 2) App：换了邀请码立刻能刷新分类（按钮 + 开始拍摄时自动检测） | 标准库 | 否 |
| `src/android/hide_keyboard.py` | 切到拍摄页时收键盘；顺带把设置里的服务器地址显示成当前实际值 | 标准库 | 否 |
| `src/android/https_fallback.py` | https 连不上时自动退回 http，并把真实错误显示出来，方便定位 | 标准库 | 否 |
| `src/android/insert_autograb.py` | 无文件头注释；按名称+代码判定：插入代码块，对象 MainActivity.java，关键调用 `t = io.open(P, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/insert_splitaddr2.py` | 无文件头注释；按名称+代码判定：插入代码块，对象 WatermarkVideo.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/invite_android_field.py` | Model.Site 加 invite 字段 / MainActivity：邀请码输入框 + 校验 + 写入 site | 标准库 | 否 |
| `src/android/invite_android_field2.py` | 1) 声明字段 / 2) 邀请码输入框（放在厂商提示行之后） | 标准库 | 否 |
| `src/android/invite_android_local.py` | 1) 校验逻辑改成纯本地：不连服务器，只记下来 / 2) 顶部那行改成显示邀请码 | 标准库 | 否 |
| `src/android/invite_case.py` | ---------------- App：输入框不限大小写，提示写清楚 ---------------- / 输入时允许字母数字和 - _（不限制大小写） | 标准库 | 否 |
| `src/android/java_outline.py` | Java 端也加四向描边（浅色背景上更清楚），与预览一致 | 标准库 | 否 |
| `src/android/java_watermark_v2.py` | 把预览图里的几何参数原样搬进 Java（WatermarkVideo.drawStamp） | 标准库 | 否 |
| `src/android/java_watermark_v3.py` | 按最终实测参数重写 Java drawStamp（渐变时间块、数字描边、轻字重） | 标准库 | 否 |
| `src/android/mapkey_setting.py` | 设置里加「地图 Key」输入框，方便换成 Web服务 类型的 Key | 标准库 | 否 |
| `src/android/nocap_code.py` | 让「不拍摄收集」版在代码里生效： · 隐藏拍照/录像按钮，只保留「从相册选」 · 不烧水印（素材自带水印） · 不检查更新 | 标准库 | 否 |
| `src/android/offline_scenes.py` | 1) 场景分类完全本地：不再请求服务器 | 标准库 | 否 |
| `src/android/patch_addr_picker.py` | 1) 字段：地址改成三级下拉 + 街道 / 2) UI：替换地址输入块 | 标准库 | 否 |
| `src/android/patch_address.py` | 1) 字段声明 / 2) beginShooting 校验并保存地址 | 标准库 | 否 |
| `src/android/patch_addtask.py` | 1) addTask 改成先填「区域 + 任务」 | 标准库 | 否 |
| `src/android/patch_crash_fix.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 MainActivity.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/patch_samearea.py` | 1) addTask -> askTask(预设区域) | 标准库 | 否 |
| `src/android/patch_task.py` | 无文件头注释；按名称+代码判定：代码补丁，对象 MainActivity.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/peek_uploader.py` | 无文件头注释；按名称+代码判定：脚本，对象 Uploader.java，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/persist_wm_address.py` | 把水印用的真实地址存进 site.wmAddress，并随队列持久化 | 标准库 | 否 |
| `src/android/polish_android.py` | 1) 启动时把需要的权限一次性要齐（含 Android 13 的通知权限，否则上传进度看不到） | 标准库 | 否 |
| `src/android/precise_mapping.py` | 按「每张照片精确对应到项」改： 1) 去掉批量导入按钮（按顺序塞容易错位） 2) 拍好的项显示缩略图 + 文件名，肉眼可核对是哪张 | 标准库 | 否 |
| `src/android/publish_apk.py` | 把构建好的 APK 发布到服务器：上传文件 + 写版本信息。 用法： python tools/publish_apk.py android/egoops-collect-v39.apk "修复场景分类" | paramiko | 是（3 处） |
| `src/android/real_gps_watermark.py` | 水印改成真实定位： · 加定位权限，启动时取一次 GPS/网络定位，反查成地址 · 水印里只放「打卡时间 + 真实地址 + 日期」，不再放门店名/采集员 · 定位不可用时退回自填地址，并标注「自填」 | 标准库 | 否 |
| `src/android/record_captured_at.py` | 记录拍摄时刻，并让「照片时间」用真正拍摄时间（文件生成那一刻）， 同时把水印里的定位/时间都改成拍摄时快照，避免上传时再取 | 标准库 | 否 |
| `src/android/replace_uselocation.py` | 用「方法体大括号配平」精确替换 useLocation，避免切片顺序错误导致整块重复 | 标准库 | 否 |
| `src/android/restore_begin.py` | 补回被误删的 beginShooting（含邀请码、省市区、面积、场景校验） | 标准库 | 否 |
| `src/android/restore_missing3.py` | 补回 beginShooting / firstIncompleteTask / installCrashReporter | 标准库 | 否 |
| `src/android/restore_splitaddr.py` | 无文件头注释；按名称+代码判定：恢复被删代码，对象 AndroidManifest.xml、build.ps1，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/android/restore_ui.py` | 重建被误删的 UI 构建方法（buildUi / 四个页面 / 工具方法），并保留新功能： 邀请码输入、厂商提示行、省市区两行布局、拍摄要点、继续上次采集点 | 标准库 | 否 |
| `src/android/set_map_key.py` | 无文件头注释；按名称+代码判定：写入配置，对象 AndroidManifest.xml、build.ps1，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 是（2 处） |
| `src/android/shots_restructure.py` | 拍摄项调整（按用户要求）： 任务1（采集点级）：门头照 + 全景照片 + 全景视频 后续区域： 对角照片 x2 + 任务照片 x2 + 任务视频 x2（6 项，不再拍门头/全景） | 标准库 | 否 |
| `src/android/simplify_settings.py` | 按「给中年人用」的原则简化： 设置里只留服务器地址，地图 Key 不做成用户要填的东西； Key 由开发方编译进 App（MapSnap.DEFAULT_KEY），用户永远不需要碰 | 标准库 | 否 |
| `src/android/swipe_anim.py` | 三个改动： 1) 切换项时卡片滑入动画（左/右方向区分） 2) 进度点区分「当前位置」和「已完成」，标题带上项名 3) 全景照片只保留「从相册选」，不显示水印相机按钮 | 标准库 | 否 |
| `src/android/swipe_prev.py` | 拍摄页支持左右滑动切换项： · 右滑 → 上一项，左滑 → 下一项 · 同时在标题右侧加「← 上一项」文字按钮（中年人不一定会滑，给个可见入口） | 标准库 | 否 |
| `src/android/sync_task_names.py` | 修：区域/动作填完后立刻把任务名和区域同步到服务器。 原因：拍完第 3 项就触发上传，上传前会把当时的任务名（"任务1"、区域空）建到服务器； 之后弹窗填的区域和动作只改了本地，服务器没更新，所以后台数据里看不到 | 标准库 | 否 |
| `src/android/two_step_scene.py` | 场景分类：必须先选大类，二级才出现具体场景；二级只显示场景名 | 标准库 | 否 |
| `src/android/unify_watermark_style.py` | 把预览好的水印样式落到 Java：WatermarkVideo.drawStamp() 统一画， 照片和视频都用它，保证两种素材一模一样 | 标准库 | 否 |
| `src/android/wire_tls_android.py` | 1) network security config / 2) Manifest 引用 | 标准库 | 是（4 处） |
| `src/android/wire_video_watermark.py` | 视频水印接线： 1) WatermarkVideo 增加静态方法 makeOverlay()（生成透明水印图层） 2) Uploader 上传视频前先烧水印，失败就用原文件 3) App 的「从相册选」按钮文案改成明确的水印相机提示 | 标准库 | 否 |
| `src/android/wire_video_wm2.py` | 接线视频水印（用实际存在的代码片段） | 标准库 | 否 |
| `src/android/wm_launch_v2.py` | 水印相机跳转更可靠： 1) 先按已知包名找（今日水印相机等常见包名） 2) 再按名字含「水印 / Watermark」找 3) 还找不到就列出手机里所有相机类 App 让用户点一次，记住选择 | 标准库 | 否 |

## lark（6）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/lark/lark_probe.py` | 无文件头注释；按名称+代码判定：飞书 Bitable 读取，关键调用 `LARK = r"C:\Users\Administrator\AppData\Roaming\npm\node_mod` | 标准库 | 是（1 处） |
| `src/lark/lark_read.py` | 先看字段 | 标准库 | 是（1 处） |
| `src/lark/lark_read2.py` | 无文件头注释；按名称+代码判定：飞书 Bitable 读取，关键调用 `CLI = r"C:\Users\Administrator\AppData\Roaming\npm\node_modu` | 标准库 | 是（1 处） |
| `src/lark/patch_feishu.py` | 直接调用飞书 OpenAPI，只需 App ID + App Secret，便于换机便携使用 | 标准库 | 否 |
| `src/lark/patch_feishu_sync.py` | 便携模式：直连飞书 OpenAPI，不需要 lark-cli | 标准库 | 否 |
| `src/lark/sync_lark_vendors.py` | 从飞书多维表格同步「厂家 → 邀请码 → 大类」到服务器。 表：https://ncnjcck15agu.feishu.cn/base/C4PKbGLoUafQbEshhDccIZjJnUb?table=tbln9OE8dCkeBOrE 表 | 标准库 | 是（1 处） |

## misc（25）

| 脚本 | 用途（一句话） | 依赖 | 含密钥 |
| --- | --- | --- | --- |
| `src/misc/app2_polish.py` | 自动选中第一个采集点，省一次点击 | 标准库 | 否 |
| `src/misc/calib_thresholds.py` | 按真实数据校准：正常照片 blur 400~630、亮度 120~146 | 标准库 | 否 |
| `src/misc/calibrate_qc.py` | 下载真实照片，看看清晰度/亮度分布，用来校准阈值 | 本地模块: extras | 是（1 处） |
| `src/misc/measure_mine.py` | 把我画的水印缩到和参考图同尺寸，逐项量尺寸，和参考图对比，输出差异表 | PIL、numpy | 否 |
| `src/misc/measure_ref.py` | 量一下参考图里各个元素的位置和颜色，照着复刻 | PIL、numpy | 否 |
| `src/misc/preview_final.py` | 和 App 里 Java 完全一致的参数，出当前水印效果（含防伪码；地图可选） | PIL | 否 |
| `src/misc/preview_with_map.py` | 出带地图的最终效果图（用刚拿到的真实高德地图） | PIL；本地模块: preview_final | 是（1 处） |
| `src/misc/setup_glm.py` | ---------- 1) 把 key 写进查看器配置 ---------- / ---------- 2) 改 prompt：SOP 要具体、动作化 ---------- | 标准库 | 否 |
| `src/misc/shrink_watermark.py` | 把水印缩小一档：F 50 → 42（所有元素等比缩），并生成单张效果图 | PIL、types | 否 |
| `src/misc/size38.py` | 按你选的 F=38，并把单行宽度限制在 0.74W，长地址仍然断成两行（和参考图一致） | PIL、types | 否 |
| `src/misc/tune7.py` | 无文件头注释；按名称+代码判定：参数微调，关键调用 `s = io.open(p, encoding='utf-8').read()` | 标准库 | 否 |
| `src/misc/tune7b.py` | 最后一轮：时间块加渐变+数字描边，地址字重调轻，徽章加细边 | 标准库 | 否 |
| `src/misc/tune7c.py` | 再做一轮模仿：微调圆角/描边，并把我的水印叠到参考图上做 50% 混合，看是否重合 | 标准库 | 否 |
| `src/misc/tune7d.py` | 白墙/浅色场景下也要看清：加深描边阴影；再出一张竖版示例 | 标准库 | 否 |
| `src/misc/tune_break.py` | best, best_score = None, 10 ** 9 for i, ch in enumerate(text): if ch not in "区街道路号镇乡村巷弄段": continue a, b = text[:i + 1], | 标准库 | 否 |
| `src/misc/watermark_on_real_photo.py` | 拿真实采集照片，按 v61 的参数把水印画上去，出前后对比图 | PIL；本地模块: tls、watermark_preview7 | 是（1 处） |
| `src/misc/watermark_on_real_photo2.py` | 用 Api 登录 token 下载一张真实照片，然后画水印做对比图 | PIL；本地模块: api、tls、watermark_preview7 | 是（1 处） |
| `src/misc/watermark_preview.py` | 按「今日水印相机」的样式重画水印，并生成一张预览图对比。 样式： [打卡] [15:32] ← 黄底黑字标签 + 深底白字时间 ▌地址第一行 ▌地址第二行 ▌2026.11.24 星期二 ✓ 采集水印已验证 \| 时间地点真实 | PIL | 否 |
| `src/misc/watermark_preview2.py` | 水印预览 v2：地址两行均衡断行、去掉缺字形的 ✓、间距更接近参考图 | PIL | 否 |
| `src/misc/watermark_preview3.py` | 按参考图继续贴近：并排对比 + 更接近的细节。 细节调整： · 时间块：深色半透明 + 细白边 + 阴影，圆角更小 · 打卡块：黄底黑字，字重更粗，垂直居中 · 底部：画一个盾形勾图标（矢量，不依赖字体） · 整体边距/字号/行距按参考图比 | PIL | 否 |
| `src/misc/watermark_preview4.py` | 水印再贴近参考图（第三版）：时间块改钢蓝、字号/断行/图标按参考图对齐 | PIL | 否 |
| `src/misc/watermark_preview5.py` | 按参考图实测比例复刻水印（单位 u = 宽度/1080）。 实测（344 宽裁剪图，地址字高 14px 记为 F）： 时间字号 1.57F 日期字号 1.0F 底部小字 0.86F 徽章高 2.36F 行距 1.43F 各段间距 0.93F | PIL | 否 |
| `src/misc/watermark_preview6.py` | 水印贴近参考图（第四版）：加宽断行位置、徽章配色/描边、字重加粗、盾形图标 | PIL | 否 |
| `src/misc/watermark_preview7.py` | 按实测比例重排（第五版）： 参考图 344 宽量得：地址字高 14px、徽章高 32px、行距 20px、日期偏移 26px、底部偏移 26px 折算成 F（地址字号）= 50u 时的比例 | PIL | 否 |
| `src/misc/watermark_sizes.py` | 缩小水印：按 F 值给出三档效果，选定后写进 App | PIL、types；本地模块: watermark_preview7 | 否 |
