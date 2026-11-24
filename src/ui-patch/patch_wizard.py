import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

# ---------- 环境自检函数 ----------
checks = '''
# ---------------------------------------------------------------- 环境自检
DEVELOPER_CONSOLE = "https://open.feishu.cn/app/<FILL_ME>/baseinfo"


def check_egoops(cfg):
    """返回 (ok, 说明)。"""
    tf = os.path.join(APP_DIR, "egoops_token.json")
    tok = load_token(tf)
    if tok and tok.get("exp") and tok["exp"] - time.time() > 600:
        left = (tok["exp"] - time.time()) / 3600
        return True, f"已登录：{tok['payload'].get('name', '?')}（剩 {left:.1f} 小时）"
    if tok and tok.get("exp"):
        return False, f"登录已过期（{datetime.fromtimestamp(tok['exp']):%m-%d %H:%M}），请重新登录"
    return False, "未登录"


def check_feishu(cfg):
    """返回 (ok, 说明, 方式)。"""
    app_id = (cfg.get("feishuAppId") or "").strip()
    secret = (cfg.get("feishuAppSecret") or "").strip()
    if app_id and secret:
        try:
            fs = Feishu(app_id, secret, cfg["baseToken"], cfg["tableId"])
            fs.token()
            n = len(fs.list_ids())
            return True, f"应用凭证有效（App ID {app_id}），表内现有 {n} 行", "openapi"
        except Exception as e:
            return False, f"应用凭证验证失败：{e}", "openapi"

    lark_bin = resolve_lark(cfg)
    if not lark_bin:
        return False, "未填 App ID/Secret，且本机没有 lark-cli", "none"
    j, out, err = run_lark(lark_bin, ["auth", "status", "--json"], as_identity=None)
    if not j:
        return False, f"lark-cli 调用失败：{(err or out)[:120]}", "lark"
    app = j.get("appId")
    bot = (j.get("identities") or {}).get("bot") or {}
    if not app:
        return False, "lark-cli 尚未配置应用", "lark"
    if not bot.get("available"):
        return False, f"lark-cli 已配置应用 {app}，但应用身份不可用", "lark"
    if app != "<FILL_ME>":
        return False, f"lark-cli 绑定的是另一个应用（{app}），它没有这张表的权限", "lark"
    return True, f"lark-cli 可用（应用 {app}，bot 身份就绪）", "lark"


'''
s = s.replace("\n# ---------------------------------------------------------------- 组表", checks + "\n# ---------------------------------------------------------------- 组表", 1)

# ---------- GUI：首次配置向导按钮 ----------
old_btn = '''    ttk.Button(btns, text="登录 / 更新令牌", command=do_login).pack(side="left", padx=(0, 8))'''
new_btn = '''    ttk.Button(btns, text="首次配置 / 自检", command=lambda: do_setup()).pack(side="left", padx=(0, 8))
    ttk.Button(btns, text="登录 / 更新令牌", command=do_login).pack(side="left", padx=(0, 8))'''
if old_btn not in s:
    raise SystemExit("按钮锚点未找到")
s = s.replace(old_btn, new_btn)

# ---------- GUI：向导实现 ----------
setup_impl = '''
    def do_setup():
        win = tk.Toplevel(root)
        win.title("首次配置 / 环境自检")
        win.geometry("780x560")

        txt = scrolledtext.ScrolledText(win, height=20, font=("Consolas", 9))
        txt.pack(fill="both", expand=True, padx=10, pady=8)

        def w(line=""):
            txt.insert("end", line + "\\n")
            txt.see("end")

        def run_checks():
            txt.delete("1.0", "end")
            cfg2 = dict(cfg)
            cfg2["baseToken"] = v_base.get().strip()
            cfg2["tableId"] = v_table.get().strip()
            cfg2["feishuAppId"] = v_appid.get().strip()
            cfg2["feishuAppSecret"] = v_secret.get().strip()
            save_cfg(cfg2)

            w("=" * 60)
            ok1, msg1 = check_egoops(cfg2)
            w(f"[1] egoops 登录：{'✔' if ok1 else '✘'} {msg1}")

            ok2, msg2, how = check_feishu(cfg2)
            w(f"[2] 飞书写入：{'✔' if ok2 else '✘'} {msg2}")

            if ok1 and ok2:
                w("")
                w("全部就绪：点「开始刷新（自动覆盖）」即可，或直接依赖定时任务。")
            else:
                w("")
                if not ok1:
                    w("→ 点顶部「登录 / 更新令牌」完成 egoops 登录")
                if not ok2:
                    w("→ 方式 A（推荐，免登录）：在开发者后台复制 App ID / App Secret，填到主窗口后点本按钮重测")
                    w("   " + DEVELOPER_CONSOLE)
                    w("→ 方式 B：确认本机 lark-cli 已配置同一个应用 " + "<FILL_ME>")

        def do_refresh_egoops():
            try:
                proc = launch_browser(headless=False)
            except Exception as e:
                w(f"启动浏览器失败：{e}")
                return
            w("已打开 egoops 登录窗口；登录完成后关闭该窗口，再点『重新检测』")
            w("（也可在主窗口点「登录 / 更新令牌 → ② 读取令牌」）")

        def open_console():
            try:
                os.startfile(DEVELOPER_CONSOLE)
            except Exception:
                pass

        def open_egoops():
            try:
                os.startfile(EGOOPS_URL)
            except Exception:
                pass

        bar = ttk.Frame(win)
        bar.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bar, text="重新检测", command=run_checks).pack(side="left")
        ttk.Button(bar, text="打开 egoops 登录", command=do_refresh_egoops).pack(side="left", padx=8)
        ttk.Button(bar, text="打开开发者后台", command=open_console).pack(side="left")
        ttk.Button(bar, text="关闭", command=win.destroy).pack(side="right")

        w("本工具写入飞书使用的是【应用身份】，换电脑不需要扫描登录飞书；")
        w("只需要保证工具能拿到应用凭证（App ID / App Secret）或本机已配置同应用的 lark-cli。")
        w("")
        run_checks()

'''
anchor = "    ttk.Button(btns, text=\"开始刷新（自动覆盖）\", command=do_refresh).pack(side=\"left\")"
if anchor not in s:
    raise SystemExit("主按钮锚点未找到")
s = s.replace(anchor, setup_impl + anchor)

io.open(p, "w", encoding="utf-8").write(s)
print("patched wizard")
