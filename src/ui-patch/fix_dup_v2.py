import io

p = 'viewer/extras.py'
s = io.open(p, encoding='utf-8').read()

# 1) 指纹从 8x8 升级到 16x16（256 位），更能区分相似但不相同的照片
s = s.replace('''        small = Image.open(path).convert("L").resize((9, 8))
        a = np.asarray(small, dtype=np.int16)
        bits = "".join("1" if a[y][x] > a[y][x + 1] else "0" for y in range(8) for x in range(8))
        return {"blur": blur, "bright": bright, "hash": bits}''',
'''        small = Image.open(path).convert("L").resize((17, 16))
        a = np.asarray(small, dtype=np.int16)
        bits = "".join("1" if a[y][x] > a[y][x + 1] else "0" for y in range(16) for x in range(16))
        return {"blur": blur, "bright": bright, "hash": bits}''')

# 2) 比较时带上清晰度差异：清晰度差太多的不算重复（避免"模糊版 vs 原图"误报）
s = s.replace('''            if ti and hamming(hi, hj) <= 3:''',
'''            bi = max(fi.get("_blur", 0), 0)
            bj = max(fj.get("_blur", 0), 0)
            if ti and hamming(hi, hj) <= 6 and abs(bi - bj) <= max(40, 0.3 * max(bi, bj)):''')

# 把 blur 记到文件上，供比较用
s = s.replace('''            photos.append((f, m["hash"], f.get("task_id") or ""))''',
'''            f["_blur"] = m["blur"]
            photos.append((f, m["hash"], f.get("task_id") or ""))''')

io.open(p, 'w', encoding='utf-8').write(s)
print('指纹升级 + 清晰度差异过滤')
