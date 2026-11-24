import io

p = 'viewer/address_parse.py'
s = io.open(p, encoding='utf-8').read()

old = '''            if not out["city"]:
                out["street"] = rest
            break'''
new = '''            if not out["city"]:
                # 直辖市 / 省掉市名：直接在这个省的所有区县里找
                for city in prov.get("children") or []:
                    for dist in city.get("children") or []:
                        dname = dist["name"]
                        dshort = dname.replace("区", "").replace("县", "").replace("市", "")
                        if rest.startswith(dname) or (dshort and rest.startswith(dshort)):
                            out["city"] = city["name"]
                            out["district"] = dname
                            out["street"] = rest[len(dname):] if rest.startswith(dname) else rest[len(dshort):]
                            break
                    if out["district"]:
                        break
                if not out["district"]:
                    out["street"] = rest
            break'''

assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
