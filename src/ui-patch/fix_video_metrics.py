import io

p = 'viewer/extras.py'
s = io.open(p, encoding='utf-8').read()

old = '''        dur = 0.0
        w = h = 0
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("Duration:"):
                part = line.split("Duration:")[1].split(",")[0].strip()
                hh, mm, ss = part.split(":")
                dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
            if "Video:" in line and "x" in line:
                for tok in line.split(",")[0].split():
                    if "x" in tok and tok.split("x")[0].isdigit():
                        try:
                            w, h = [int(x) for x in tok.split("x")[:2]]
                        except Exception:
                            pass
                        break
        return {"duration": dur, "width": w, "height": h}'''
new = '''        import re as _re
        dur = 0.0
        w = h = 0
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("Duration:"):
                part = line.split("Duration:")[1].split(",")[0].strip()
                try:
                    hh, mm, ss = part.split(":")
                    dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
                except Exception:
                    pass
            if line.startswith("Stream") and "Video:" in line:
                m = _re.search(r"(\\d{2,5})x(\\d{2,5})", line)   # 只认 1280x720 这种，避开 0x31637668
                if m:
                    w, h = int(m.group(1)), int(m.group(2))
        return {"duration": dur, "width": w, "height": h}'''
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('video 解析修好')
