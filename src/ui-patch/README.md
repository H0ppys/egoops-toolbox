# ui-patch（查看器与后端代码补丁）

本组 **139** 个脚本。数量最多的一组：用「字符串锚点替换」给 Tkinter 查看器（`app.py`/`viewer.py`）、relay 后端（`server.mjs`/`db.mjs`/`api.py`）打补丁，以及配套的截图取证与自检脚本。

## 代表脚本

- `patch_*.py`（14 个）：`egoops_gui.py` 的登录、令牌、隐藏控制台、定时器、向导
- `fix_*.py`（约 60 个）：表格列宽、勾选级联、删除/下载、TLS 固定证书、线程与崩溃
- `redesign_viewer*.py` / `slim_viewer_ui.py` / `polish_viewer.py`：界面三次重做与收尾
- `server_*.py` / `vendor_*.py` / `invite_*.py`：relay 后端的版本路由、厂商分类、邀请码接口
- `shot_*.py` / `snap_state.py` / `audit_dialogs.py`：改完自动截图或遍历对话框自检

## 运行前提

在**目标工程目录**下运行（脚本里写死了目标文件路径，已保留原路径形态）；改前请让脚本自带的 `*.bak` 生效。

## 注意

锚点匹配失败是预期（源码已变）；每个补丁脚本开头都有 `P = r"...\app.py"` 之类的目标常量。

## 清单

逐脚本用途/依赖/是否含密钥见 [../../docs/INVENTORY.md](../../docs/INVENTORY.md)；脱敏位置见 [../../docs/SECRETS.md](../../docs/SECRETS.md)。
