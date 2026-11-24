import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

s = s.replace('''        raise RuntimeError(
            "无法获取 egoops 登录态。请用 Edge 打开 https://egoops.meituan.com/recordings "
            "（确保已登录）后重试；打开后 1 分钟内读取成功率最高。")''',
'''        raise RuntimeError(
            "登录已失效。请点「登录 / 更新令牌」：① 打开 egoops 并确认已登录 ② F12 → Network → "
            "任意 /api/v1 请求 → Copy as cURL ③ 粘贴保存。也可命令行：--set-token \\"<cURL 或 token>\\"")''')

s = s.replace('''        raise RuntimeError(f"登录态已过期（{datetime.fromtimestamp(tok['exp']):%Y-%m-%d %H:%M}），请在 Edge 刷新 egoops 页面")''',
'''        raise RuntimeError(
            f"登录态已过期（{datetime.fromtimestamp(tok['exp']):%Y-%m-%d %H:%M}）。"
            "请点「登录 / 更新令牌」重新粘贴 cURL；命令行：--set-token \\"<cURL>\\"")''')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
