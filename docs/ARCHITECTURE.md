# 架构与数据流（ARCHITECTURE）

这套脚本服务于同一条链路，按「谁跟谁说话」分成四层：

```
安卓采集 App (com.egoops.collect)
        │  ① 拍照/录像 + 水印 → 上传
        ▼
relay 中继服务 (node server.mjs, :18090, nginx /relay/)
        │  SQLite relay.db：sites / tasks / files / invite
        ├─② 草稿写入 ─────────────► EgoOps 开放接口 (api/v1/task-sets …)
        ├─③ 日报/统计读写 ────────► 飞书 Bitable (lark-cli base +record-list)
        └─④ 看图/AI 生成 SOP ─────► Ark / GLM 视觉模型
        ▲
        │  ⑤ 查看器（Tkinter app.py）：采集点树、质检、导出、建草稿
        └───────────── 运维脚本群（本仓）
```

| 层 | 代表组件 | 本仓对应分类 |
| --- | --- | --- |
| 采集端 | `MainActivity.java` / `WatermarkVideo.java` / `Uploader.java`，`build.ps1` | `src/android/` |
| 中继服务 | `server.mjs`、`db.mjs`、`api.py`、`backup.mjs` | `src/ui-patch/`（后端补丁）、`src/table-schema/` |
| 数据面 | `relay.db`、`data/`、场景表 `scenes.json` / `vendor_scenes.json` | `src/data-backfill/` |
| 外部系统 | EgoOps RPC、飞书 Bitable、Ark/GLM | `src/api-probe/`、`src/lark/` |
| 运维 | systemd/nginx/acme.sh/备份/cron | `src/deploy/`、`src/bot/` |

## 脚本形态（四类）

1. **探针**：只读，打印响应结构或统计（`probe_*`、`inspect_*`、`check_*`、`diag_*`）。
2. **补丁**：`open(target)→字符串锚点替换→写回`，多数会先备份 `*.bak`。识别目标文件看脚本里的 `P = r"...MainActivity.java"` 之类的常量。
3. **搬运/回填**：读 Excel/ndjson/接口，写 SQLite 或飞书表。
4. **部署**：按序号执行的幂等 shell；每步都带健康检查输出。

## 重要约定

- 补丁脚本靠**字符串锚点**匹配，源码一改就会 `锚点未找到`，属预期行为。
- 所有脚本里的目标地址/令牌都是 `<FILL_ME>`，运行前必须注入。
- `deploy/` 的 01–10 有严格顺序，见 [DEPLOY.md](DEPLOY.md)。
