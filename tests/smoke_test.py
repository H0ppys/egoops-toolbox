# -*- coding: utf-8 -*-
"""egoops-toolbox 冒烟测试：目录完整性 + UTF-8 可读 + 无明文密钥残留 + py 可编译。

用法：python tests/smoke_test.py [--fast]
"""
import os, re, sys, py_compile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
EXPECT = {"api-probe": 85, "table-schema": 11, "data-backfill": 12, "ui-patch": 139,
          "deploy": 22, "bot": 5, "android": 102, "lark": 6, "misc": 25}
BAD = [r"eyJ[A-Za-z0-9_-]{20,}", r"(?<!\d)1[3-9]\d{9}(?!\d)",
       r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b",
       r"(?i)bearer\s+[A-Za-z0-9._-]{20,}", r"ou_[A-Za-z0-9]{20,}"]

def main():
    fast = "--fast" in sys.argv
    fails = []
    total = 0
    for cat, n in sorted(EXPECT.items()):
        d = os.path.join(SRC, cat)
        if not os.path.isdir(d):
            fails.append("缺少目录 src/%s" % cat)
            continue
        files = [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
        scripts = [f for f in files if f != "README.md"]
        total += len(scripts)
        if len(scripts) != n:
            fails.append("src/%s 脚本数 %d != 期望 %d" % (cat, len(scripts), n))
    checked, compiled = 0, 0
    for cat in sorted(EXPECT):
        d = os.path.join(SRC, cat)
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if not os.path.isfile(p) or f == "README.md":
                continue
            checked += 1
            text = open(p, encoding="utf-8", errors="strict").read()
            for pat in BAD:
                if re.search(pat, text):
                    fails.append("疑似密钥残留: src/%s/%s (/%s/)" % (cat, f, pat))
            if f.endswith(".py") and not fast:
                try:
                    compile(text, p, "exec")   # 等价 py_compile 的语法编译，不落 .pyc
                    compiled += 1
                except SyntaxError as e:
                    fails.append("编译失败: src/%s/%s -> %s" % (cat, f, e))
    print("脚本总数 %d（期望 407）；UTF-8 读取 %d；py_compile %d" % (total, checked, compiled))
    if fails:
        print("FAIL %d 项：" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 目录/数量/UTF-8/密钥扫描%s" % ("" if fast else "/编译") + " 全部通过")
    return 0

if __name__ == "__main__":
    sys.exit(main())
