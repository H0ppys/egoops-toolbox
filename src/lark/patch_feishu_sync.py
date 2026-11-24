import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

old = '''    lark_bin = resolve_lark(cfg)
    if not lark_bin:
        raise RuntimeError("找不到 lark-cli，请在配置里填写 larkBin")
    as_id = cfg.get("asIdentity", "bot")

    step(60, "读取表内旧数据…")
    old = list_record_ids(lark_bin, cfg["baseToken"], cfg["tableId"], as_id)
    log(f"表内旧记录 {len(old)} 条")

    step(70, "清空旧数据…")
    cleared = delete_records(lark_bin, cfg["baseToken"], cfg["tableId"], old, as_id, log) if old else 0
    log(f"已清空 {cleared} 条")

    step(85, f"写入 {len(rows)} 行…")
    j, out, err = batch_create(lark_bin, cfg["baseToken"], cfg["tableId"], rows, as_id)
    if not (j and j.get("ok")):
        msg = json.dumps(j.get("error"), ensure_ascii=False) if j else (err or out)
        raise RuntimeError(f"写入失败：{msg[:300]}")
    written = len(j.get("data", {}).get("record_id_list") or rows)'''

new = '''    app_id = (cfg.get("feishuAppId") or "").strip()
    app_secret = (cfg.get("feishuAppSecret") or "").strip()

    if app_id and app_secret:
        # 便携模式：直连飞书 OpenAPI，不需要 lark-cli
        log("写入方式：飞书开放接口（App ID/Secret）")
        fs = Feishu(app_id, app_secret, cfg["baseToken"], cfg["tableId"])

        step(60, "读取表内旧数据…")
        old = fs.list_ids()
        log(f"表内旧记录 {len(old)} 条")

        step(70, "清空旧数据…")
        cleared = fs.batch_delete(old) if old else 0
        log(f"已清空 {cleared} 条")

        step(85, f"写入 {len(rows)} 行…")
        written = fs.batch_create([to_feishu_fields(r) for r in rows])
        log(f"已写入 {written} 行")
    else:
        # 兼容模式：调用本机 lark-cli
        lark_bin = resolve_lark(cfg)
        if not lark_bin:
            raise RuntimeError("既没有配置 App ID/Secret，也找不到 lark-cli")
        as_id = cfg.get("asIdentity", "bot")
        log(f"写入方式：lark-cli（--as {as_id}）")

        step(60, "读取表内旧数据…")
        old = list_record_ids(lark_bin, cfg["baseToken"], cfg["tableId"], as_id)
        log(f"表内旧记录 {len(old)} 条")

        step(70, "清空旧数据…")
        cleared = delete_records(lark_bin, cfg["baseToken"], cfg["tableId"], old, as_id, log) if old else 0
        log(f"已清空 {cleared} 条")

        step(85, f"写入 {len(rows)} 行…")
        j, out, err = batch_create(lark_bin, cfg["baseToken"], cfg["tableId"], rows, as_id)
        if not (j and j.get("ok")):
            msg = json.dumps(j.get("error"), ensure_ascii=False) if j else (err or out)
            raise RuntimeError(f"写入失败：{msg[:300]}")
        written = len(j.get("data", {}).get("record_id_list") or rows)'''

if old not in s:
    raise SystemExit("目标代码块未找到")
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("patched sync")
