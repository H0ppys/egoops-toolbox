"""从飞书多维表格同步「厂家 → 邀请码 → 大类」到服务器。

表：https://ncnjcck15agu.feishu.cn/base/C4PKbGLoUafQbEshhDccIZjJnUb?table=tbln9OE8dCkeBOrE

表格需要的列（列名不区分顺序，按名字找）：
    厂家      必填
    邀请码    必填
    大类      可选，写「零售、餐饮」这样的清单；不填或不加这一列 = 这个厂家看全部大类

用法：
    python tools/sync_lark_vendors.py            # 只打印，不发布
    python tools/sync_lark_vendors.py --deploy   # 同步并发布到服务器
"""

import io
import json
import os
import subprocess
import sys

CLI = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\@larksuite\cli\bin\lark-cli.exe"
BASE = "<FILL_ME>"
TABLE = "tbln9OE8dCkeBOrE"

VENDOR_FILE = "relay/vendor_scenes.json"
NAME_FILE = "relay/vendor_names.json"


def sh(args):
    env = dict(os.environ)
    env["LARK_HOME"] = os.path.abspath(".tmp/larkhome")
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", env=env)
    if r.returncode != 0:
        raise SystemExit("lark-cli 失败：%s\n%s" % (r.returncode, (r.stderr or r.stdout)[:500]))
    return json.loads(r.stdout)


def load_scene_categories():
    d = json.load(io.open("relay/scenes.json", encoding="utf-8"))
    cats = []
    for it in d["items"]:
        if it["category"] not in cats:
            cats.append(it["category"])
    return cats, d.get("version", "")


def main():
    deploy = "--deploy" in sys.argv

    fields = sh([CLI, "base", "+field-list", "--base-token", BASE, "--table-id", TABLE])
    names = [f["name"] for f in fields["data"]["fields"]]
    print("表格列:", names)

    rows = sh([CLI, "base", "+record-list", "--base-token", BASE, "--table-id", TABLE,
               "--page-size", "200", "--format", "json"])
    matrix = rows["data"]["data"]
    header = names

    def col(*cands):
        for c in cands:
            if c in header:
                return header.index(c)
        return -1

    i_vendor = col("厂家", "厂商", "vendor", "Vendor")
    i_code = col("邀请码", "码", "code", "Code", "invite")
    i_cats = col("大类", "分类", "domain", "domains", "Domain")

    if i_vendor < 0 or i_code < 0:
        raise SystemExit("表格里必须有「厂家」和「邀请码」两列")

    cats, version = load_scene_categories()
    unknown = set()

    vendors, names_map = {}, {}
    for row in matrix:
        vendor = str(row[i_vendor] or "").strip()
        code = str(row[i_code] or "").strip().upper()
        if not vendor or not code:
            continue
        names_map[code] = vendor
        if i_cats >= 0:
            raw = str(row[i_cats] or "").replace("，", ",").replace("、", ",").replace(" ", ",")
            allow = [a.strip() for a in raw.split(",") if a.strip()]
            if allow:
                bad = [a for a in allow if a not in cats]
                unknown.update(bad)
                allow = [a for a in allow if a in cats]
                if allow:
                    vendors[code] = allow
                    continue
        # 没填大类 = 全部（不写进 vendor_scenes.json）

    print("\n场景表版本:", version)
    print("厂家数:", len(names_map), "| 配置了大类的:", len(vendors))
    for code, vendor in names_map.items():
        allow = vendors.get(code)
        print("  %-6s %-8s %s" % (code, vendor, " / ".join(allow) if allow else "（全部大类）"))
    if unknown:
        print("\n!! 表格里有场景表不存在的大类，已忽略:", " / ".join(sorted(unknown)))

    io.open(VENDOR_FILE, "w", encoding="utf-8").write(json.dumps(vendors, ensure_ascii=False, indent=1))
    io.open(NAME_FILE, "w", encoding="utf-8").write(json.dumps(names_map, ensure_ascii=False, indent=1))
    print("\n已写入", VENDOR_FILE, "和", NAME_FILE)

    if deploy:
        for local, remote in ((VENDOR_FILE, "/opt/egoops/relay/vendor_scenes.json"),
                              (NAME_FILE, "/opt/egoops/relay/vendor_names.json")):
            subprocess.run([sys.executable, "ssh_exec.py", "-u", local, remote], check=True)
        subprocess.run([sys.executable, "ssh_exec.py", "systemctl restart egoops-relay"], check=True)
        print("已发布到服务器")
    else:
        print("（加 --deploy 才会发布到服务器）")


if __name__ == "__main__":
    main()
