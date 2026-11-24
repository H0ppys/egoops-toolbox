import io

p = r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_gui.py"
s = io.open(p, encoding="utf-8").read()

s = s.replace('def existing_ids(lark_bin, base_token, table_id, log):',
              'def existing_ids(lark_bin, base_token, table_id, log, as_identity="bot"):')
s = s.replace('                    "--overwrite",\n                ])',
              '                    "--overwrite",\n                ], as_identity=as_identity)')
s = s.replace('def batch_create(lark_bin, base_token, table_id, records):',
              'def batch_create(lark_bin, base_token, table_id, records, as_identity="bot"):')
s = s.replace('            "--json", "@" + p,\n        ], timeout=300)',
              '            "--json", "@" + p,\n        ], timeout=300, as_identity=as_identity)')

s = s.replace('    have = existing_ids(lark_bin, cfg["baseToken"], cfg["tableId"], log)',
              '    as_id = cfg.get("asIdentity", "bot")\n'
              '    have = existing_ids(lark_bin, cfg["baseToken"], cfg["tableId"], log, as_identity=as_id)')
s = s.replace('        j, out, err = batch_create(lark_bin, cfg["baseToken"], cfg["tableId"], chunk)',
              '        j, out, err = batch_create(lark_bin, cfg["baseToken"], cfg["tableId"], chunk, as_identity=as_id)')

s = s.replace('    if "--full" in argv:\n        cfg["full"] = True',
              '    if "--full" in argv:\n        cfg["full"] = True\n    if "--as-user" in argv:\n        cfg["asIdentity"] = "user"')

io.open(p, "w", encoding="utf-8").write(s)
print("patched")
