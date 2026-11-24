import io
import re

p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

# 把在 except 里创建、随后在 lambda 里引用 e 的写法，改成绑定默认参数
fixes = [
    ('''            except Exception as e:
                    self.ui(lambda: login_state.config(text="✗ 失败：%s" % e, foreground="#b3261e"))''',
     '''            except Exception as e:
                    self.ui(lambda err=str(e): login_state.config(text="✗ 失败：" + err, foreground="#b3261e"))'''),
    ('''                    self.ui(lambda: login_state.config(
                        text=("✓ " if ok else "✗ ") + info,
                        foreground="#1f7a3d" if ok else "#b3261e"))''',
     '''                    self.ui(lambda i=info, s=ok: login_state.config(
                        text=("✓ " if s else "✗ ") + i,
                        foreground="#1f7a3d" if s else "#b3261e"))'''),
]

for old, new in fixes:
    if old in s:
        s = s.replace(old, new)
        print("修了一处:", old.strip().splitlines()[-1][:50])
    else:
        print("没找到（可能格式不同）:", old.strip().splitlines()[-1][:50])

# 通用兜底：把所有 "lambda: ... % e" 和 "lambda: ... , e)" 形式改为默认参数绑定
def bind_default(m):
    body = m.group(1)
    return "lambda _e=%s: %s" % ("e", body.replace("e", "_e"))

s = re.sub(r"lambda: ([^\n]*% e[^\n]*)", bind_default, s)
s = re.sub(r"lambda: ([^\n]*\be\b[^\n]*)\)", lambda m: "lambda _e=e: " + m.group(1).replace("e", "_e") + ")", s)

io.open(p, 'w', encoding='utf-8').write(s)
print("完成")
