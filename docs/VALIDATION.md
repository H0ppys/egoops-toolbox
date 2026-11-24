# 验证结果（VALIDATION）

全部命令在 `egoops-toolbox` 仓库根目录执行，环境：Windows Server（Python 3.15.2 / Node v26.13.1 / 无 bash）。
下面是**未经修改的真实输出**。

## 结论

| 项目 | 结果 |
| --- | --- |
| Python 语法（compileall + 逐文件 py_compile） | 341 / 341 通过，0 失败 |
| Node 语法（node --check .js/.mjs） | 26 / 26 通过，0 失败 |
| Shell / PowerShell（无 bash → 引号与括号状态机静态检查） | 39 / 39 通过，0 需复核 |
| 密钥残留扫描（JWT / 手机号 / 内网 IP / Bearer / open_id / base token） | 6 类规则全部 0 命中 |
| 冒烟测试 tests/smoke_test.py | PASS |

## 原始输出

```
$ python -m compileall -q src
（无输出 = 全部通过）
[exit code: 0]   py 文件数: 341（compileall 生成的 7 个 __pycache__ 已清理）

$ python -m py_compile <每个文件>   （cfile 指向临时目录）
通过 341 / 341；失败 0

$ node --check <每个 .js/.mjs>   （node v26.13.1）
通过 26 / 26；失败 0
  src/api-probe/check_videos.mjs                       OK
  src/api-probe/dl_media.mjs                           OK
  src/api-probe/download.mjs                           OK
  src/api-probe/e2e-test.mjs                           OK
  src/api-probe/egoops_dl.mjs                          OK
  src/api-probe/egoops_probe_sites.mjs                 OK
  src/api-probe/egoops_probe_tasks.mjs                 OK
  src/api-probe/export_named.mjs                       OK
  src/api-probe/export_site.mjs                        OK
  src/api-probe/fetch-scenes.mjs                       OK
  src/api-probe/fetch_pca.mjs                          OK
  src/api-probe/inspect2.js                            OK
  src/api-probe/members.js                             OK
  src/api-probe/scan_bases.js                          OK
  src/api-probe/seed.mjs                               OK
  src/api-probe/sim_chunk.mjs                          OK
  src/api-probe/sim_upload.mjs                         OK
  src/api-probe/test-upload.mjs                        OK
  src/api-probe/test_cdp.js                            OK
  src/api-probe/verify-prod-e2e.mjs                    OK
  src/api-probe/verify-prod.mjs                        OK
  src/api-probe/verify_agg.js                          OK
  src/bot/check_bot_access.js                          OK
  src/deploy/probe-ports.js                            OK
  src/table-schema/inspect_capacity.js                 OK
  src/table-schema/inspect_tables.js                   OK

$ python .tmp/toolbox/shcheck.py   （Windows 无 bash，改用引号/括号状态机静态检查）
shell/ps1 静态检查: sh=38 ps1=1 通过=39 需人工复核=0
[exit code: 0]

$ 密钥残留扫描（src 下全部 416 个文件）
  JWT                0 命中
  手机号                0 命中
  内网 IP              0 命中
  Bearer 令牌          0 命中
  open_id            0 命中
  飞书 base token 形态   0 命中

$ python tests/smoke_test.py
脚本总数 407（期望 407）；UTF-8 读取 407；py_compile 341
PASS: 目录/数量/UTF-8/密钥扫描/编译 全部通过
[exit code: 0]

$ 体积
src 文件数 416；仓库总大小 1768.8 KB（不含 .git）
```

## 说明

1. **没有 bash**：本机是 Windows，`bash -n` 不可用。改用 Python 状态机逐个检查 .sh/.ps1 的引号配平与 `()[]{}` 配平（先剔除注释与 heredoc 正文），39 个文件全部通过；`src/deploy/04-nginx-relay.py` 由 Python 校验覆盖。
2. **compileall 的副产物**：`python -m compileall -q src` 会在 src 下生成 `__pycache__`，脚本取完结果后立即删除（`.gitignore` 亦已排除）。
3. **逐文件 py_compile** 的 `cfile` 指向工作区内临时目录，落盘产物不留在仓库。
4. **node --check** 对 `.mjs` 同样有效（按扩展名走 ESM 解析）。
5. 脱敏只替换值、保留行结构，因此语法校验结论与原文一致；`src/ui-patch/shot_viewer.py`、`src/ui-patch/test_download_checked.py` 原文带 UTF-8 BOM，入库时去掉 BOM（否则 `compile()` 会报 U+FEFF）。
