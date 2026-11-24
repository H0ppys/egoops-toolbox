#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把仓库内硬编码的 Ark API Key 换成占位符（幂等）。用法：python redact_ark_key.py"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLACEHOLDER = "<FILL_ARK_API_KEY>"


def main() -> int:
    pat = re.compile(r"ark-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-[0-9a-f]{5}")
    changed = 0
    for f in ROOT.rglob("*"):
        if not f.is_file() or ".git" in f.parts:
            continue
        if f.suffix.lower() not in {".py", ".md", ".json", ".sh", ".ps1", ".txt"}:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        if not pat.search(text):
            continue
        new = pat.sub(PLACEHOLDER, text)
        if "os.environ.get(\"ARK_API_KEY\"" not in new:
            new = re.sub(
                r'^([ \t]*KEY[ \t]*=[ \t]*)"' + re.escape(PLACEHOLDER) + r'"',
                r'\1os.environ.get("ARK_API_KEY", "' + PLACEHOLDER + '")',
                new,
                flags=re.M,
            )
            if "os.environ.get(\"ARK_API_KEY\"" in new and not re.search(r"^import os\b", new, re.M):
                lines = new.splitlines(keepends=True)
                idx = 0
                for i, ln in enumerate(lines):
                    if ln.startswith("import ") or ln.startswith("from "):
                        idx = i
                        break
                lines.insert(idx, "import os\n")
                new = "".join(lines)
        f.write_text(new, encoding="utf-8")
        print(f"redacted: {f.relative_to(ROOT)}")
        changed += 1
    print(f"total {changed} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
