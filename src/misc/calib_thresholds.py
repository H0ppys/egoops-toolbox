import io

p = 'viewer/extras.py'
s = io.open(p, encoding='utf-8').read()

# 按真实数据校准：正常照片 blur 400~630、亮度 120~146
s = s.replace('''            if m["blur"] < 40:
                issues.append({"file": f, "kind": "模糊", "reason": "清晰度 %.0f（<40）" % m["blur"], "level": "error"})
            elif m["blur"] < 90:
                issues.append({"file": f, "kind": "偏糊", "reason": "清晰度 %.0f（<90）" % m["blur"], "level": "warn"})
            if m["bright"] < 45:
                issues.append({"file": f, "kind": "过暗", "reason": "亮度 %.0f（<45）" % m["bright"], "level": "error"})
            elif m["bright"] > 220:''', '''            if m["blur"] < 80:
                issues.append({"file": f, "kind": "模糊", "reason": "清晰度 %.0f（<80）" % m["blur"], "level": "error"})
            elif m["blur"] < 180:
                issues.append({"file": f, "kind": "偏糊", "reason": "清晰度 %.0f（<180）" % m["blur"], "level": "warn"})
            if m["bright"] < 50:
                issues.append({"file": f, "kind": "过暗", "reason": "亮度 %.0f（<50）" % m["bright"], "level": "error"})
            elif m["bright"] > 220:''')

io.open(p, 'w', encoding='utf-8').write(s)
print('阈值已校准')
