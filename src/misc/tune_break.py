import io

p = 'tools/watermark_preview6.py'
s = io.open(p, encoding='utf-8').read()

old = """    best, best_score = None, 10 ** 9
    for i, ch in enumerate(text):
        if ch not in "区街道路号镇乡村巷弄段":
            continue
        a, b = text[:i + 1], text[i + 1:]
        if not a or not b or not fits(a) or not fits(b):
            continue
        sc = abs(len(a) - len(b))
        if sc < best_score:
            best_score, best = sc, [a, b]"""

new = """    best = None
    for i, ch in enumerate(text):
        if ch not in "区街道路号镇乡村巷弄段":
            continue
        a, b = text[:i + 1], text[i + 1:]
        if not a or not b or not fits(a) or not fits(b):
            continue
        best = [a, b]          # 取最靠右的可行断点：第一行尽量排满"""

assert old in s, 'pattern not found'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('断行：改成第一行排满')
