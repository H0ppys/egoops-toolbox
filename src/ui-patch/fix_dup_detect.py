import io

p = 'viewer/extras.py'
s = io.open(p, encoding='utf-8').read()

# 重复检测：只在同一任务内比较，且收紧到 3 位距离
s = s.replace('''            photos.append((f, m["hash"]))''',
              '''            photos.append((f, m["hash"], f.get("task_id") or ""))''')

s = s.replace('''    # 重复图（指纹距离 <= 5）
    for i in range(len(photos)):
        for j in range(i + 1, len(photos)):
            if hamming(photos[i][1], photos[j][1]) <= 5:
                issues.append({"file": photos[j][0], "kind": "疑似重复",
                               "reason": "与 %s 几乎相同" % photos[i][0].get("filename", ""), "level": "warn"})''',
'''    # 重复图：只比同一个任务里的照片，距离 <= 3 才算（同场景不同角度不算）
    for i in range(len(photos)):
        for j in range(i + 1, len(photos)):
            fi, hi, ti = photos[i]
            fj, hj, tj = photos[j]
            if ti != tj:
                continue
            if fi.get("id") == fj.get("id"):
                continue
            if ti and hamming(hi, hj) <= 3:
                issues.append({"file": fj, "kind": "疑似重复",
                               "reason": "与 %s 几乎相同（同一任务内）" % fi.get("filename", ""),
                               "level": "warn"})''')

io.open(p, 'w', encoding='utf-8').write(s)
print('重复检测收紧')
