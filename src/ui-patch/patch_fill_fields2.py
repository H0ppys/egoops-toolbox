import io

p = 'viewer/fill_egoops.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace(
    "def run_fill(site, on_log=None, headless=False, dump=False, wait_seconds=900, profile=None):",
    'def run_fill(site, fields=None, on_log=None, headless=False, dump=False, wait_seconds=900, profile=None):\n'
    '    fields = set(fields or ["name", "address", "area", "scene", "note"])')

old = '''            filled = []
            if site.get("name") and _fill_by_label(pg, ["采集点名称", "名称", "门店名称"], site["name"], log, "名称"):
                filled.append("名称")
            if site.get("address") and _fill_by_label(pg, ["现场地址", "地址", "详细地址"], site["address"], log, "地址"):
                filled.append("地址")
            if site.get("area") and _fill_by_label(pg, ["面积", "场地面积"], site["area"], log, "面积"):
                filled.append("面积")
            if site.get("scene_label"):'''

new = '''            filled = []
            skipped = []
            if "name" in fields:
                if site.get("name") and _fill_by_label(pg, ["采集点名称", "名称", "门店名称"], site["name"], log, "名称"):
                    filled.append("名称")
                else:
                    skipped.append("名称")
            else:
                skipped.append("名称")
            if "address" in fields:
                if site.get("address") and _fill_by_label(pg, ["现场地址", "地址", "详细地址"], site["address"], log, "地址"):
                    filled.append("地址")
                else:
                    skipped.append("地址")
            else:
                skipped.append("地址")
            if "area" in fields:
                if site.get("area") and _fill_by_label(pg, ["面积", "场地面积"], site["area"], log, "面积"):
                    filled.append("面积")
                else:
                    skipped.append("面积")
            else:
                skipped.append("面积")
            if "note" in fields:
                if site.get("note") and _fill_by_label(pg, ["采集点描述", "描述", "备注"], site["note"], log, "描述"):
                    filled.append("描述")
                else:
                    skipped.append("描述")
            else:
                skipped.append("描述")
            if "scene" not in fields:
                skipped.append("场景")
            if site.get("scene_label") and "scene" in fields:'''

assert old in s
s = s.replace(old, new)

s = s.replace(
    '            log("已填写：%s" % ("、".join(filled) if filled else "（没匹配到输入框，见上面的控件清单）"))',
    '            log("已填写：%s" % ("、".join(filled) if filled else "（没匹配到输入框，见上面的控件清单）"))\n'
    '            log("跳过：%s" % ("、".join(skipped) if skipped else "无"))')

io.open(p, 'w', encoding='utf-8').write(s)
print('fill_egoops patched')
