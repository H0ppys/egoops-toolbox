import io

# ---------- 1) 查看器草稿显示拆解后的地址 ----------
p = 'viewer/app.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace("from api import Api, ApiError, human_size",
              "from api import Api, ApiError, human_size\nfrom address_parse import parse as parse_address")

old_plain = '''                 "现场地址：%s" % (site.get("address") or "（未填）"),'''
new_plain = '''                 "现场地址：%s" % (site.get("address") or "（未填）"),
                 "  → 拆解：省=%s 市=%s 区=%s 街道=%s" % (
                     (parse_address(site.get("address") or "").get("province") or "?"),
                     (parse_address(site.get("address") or "").get("city") or "?"),
                     (parse_address(site.get("address") or "").get("district") or "?"),
                     (parse_address(site.get("address") or "").get("street") or "?")),'''
assert old_plain in s
s = s.replace(old_plain, new_plain)

# 草稿 HTML：地址后面加拆解提示
old_html = '''                ("现场地址", esc(site.get("address") or "（未填）")),'''
new_html = '''                ("现场地址", esc(site.get("address") or "（未填）")
                 + ("" if not site.get("address") else
                    " <span style='color:#6b7a90;font-size:12px'>（省 %s / 市 %s / 区 %s / 街道 %s）</span>" % (
                        esc(parse_address(site.get("address")).get("province") or "?"),
                        esc(parse_address(site.get("address")).get("city") or "?"),
                        esc(parse_address(site.get("address")).get("district") or "?"),
                        esc(parse_address(site.get("address")).get("street") or "?")))),'''
assert old_html in s
s = s.replace(old_html, new_html)

io.open(p, 'w', encoding='utf-8').write(s)
print('app.py patched')

# ---------- 2) 自动填表：填地址级联 ----------
p2 = 'viewer/fill_egoops.py'
t = io.open(p2, encoding='utf-8').read()

anchor = 'def _fill_by_label('
helper = '''def fill_address(pg, address, log):
    """省/市/区 级联下拉 + 街道门牌号"""
    from address_parse import parse
    parts = parse(address or "")
    if not parts.get("ok"):
        log("地址拆不开（%s），需要手动选省市区：%s" % (parts.get("note"), address))
        return False
    try:
        pg.get_by_text("请选择省、市、区（县）", exact=False).first.click(timeout=6000)
        pg.wait_for_timeout(800)
        for name in (parts["province"], parts["city"], parts["district"]):
            btn = pg.get_by_role("button", name=name, exact=True)
            if not btn.count():
                log("地址级联里没找到「%s」" % name)
                return False
            btn.first.click()
            pg.wait_for_timeout(700)
        log("✓ 省市区 = %s %s %s" % (parts["province"], parts["city"], parts["district"]))
    except Exception as e:
        log("选省市区失败：%s" % e)
        return False
    try:
        street = pg.get_by_placeholder("街道、门牌号、园区或楼栋").first
        street.fill(parts["street"])
        log("✓ 街道 = %s" % parts["street"])
    except Exception as e:
        log("填街道失败：%s" % e)
    return True


'''
t = t.replace(anchor, helper + anchor, 1)

# 在填写流程里插入地址
old_fill = '''            if "address" in fields:
                if site.get("address") and _fill_by_label(pg, ["现场地址", "地址", "详细地址"], site["address"], log, "地址"):
                    filled.append("地址")
                else:
                    skipped.append("地址")
            else:
                skipped.append("地址")'''
new_fill = '''            if "address" in fields:
                if site.get("address") and fill_address(pg, site["address"], log):
                    filled.append("地址")
                else:
                    skipped.append("地址")
            else:
                skipped.append("地址")'''
assert old_fill in t
t = t.replace(old_fill, new_fill)

io.open(p2, 'w', encoding='utf-8').write(t)
print('fill_egoops.py patched')
