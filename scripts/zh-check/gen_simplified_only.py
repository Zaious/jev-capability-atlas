#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從 OpenCC 的繁簡字典推導「只有簡體才有的字」，寫成 simplified_only.txt。
Derive the set of Simplified-only characters from OpenCC's dictionaries and write
simplified_only.txt. Only needed to regenerate the list; check_zh.py reads the
committed file and needs nothing beyond the standard library.

  pip install opencc-python-reimplemented
  python scripts/zh-check/gen_simplified_only.py

判定規則 / rule: a character c is Simplified-only when
  - OpenCC's S->T table (STCharacters.txt) maps c to traditional forms that do NOT
    include c itself (so 里→裡/里, 台→臺/台, 后→後/后 stay allowed), and
  - c is not itself a traditional form (not a key of TSCharacters.txt), and
  - c is not a Taiwan- or Hong Kong-standard form (not a value in TWVariants.txt or
    HKVariants.txt). OpenCC's base "traditional" is old-style (群→羣, 床→牀, 峰→峯);
    without this, everyday Taiwanese characters get flagged.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    table = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        key, vals = line.split("\t", 1)
        table[key] = vals.split()
    return table


def main():
    import opencc
    d = os.path.join(os.path.dirname(opencc.__file__), "dictionary")
    st = load(os.path.join(d, "STCharacters.txt"))
    ts = load(os.path.join(d, "TSCharacters.txt"))
    regional = set()
    for name in ("TWVariants.txt", "HKVariants.txt"):
        for vals in load(os.path.join(d, name)).values():
            regional.update(v for v in vals if len(v) == 1)
    only = sorted(c for c, trad in st.items()
                  if len(c) == 1 and c not in trad and c not in ts and c not in regional)
    out = os.path.join(HERE, "simplified_only.txt")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Simplified-only characters, derived from OpenCC STCharacters/TSCharacters\n")
        f.write("# by scripts/zh-check/gen_simplified_only.py. Regenerate rather than hand-edit.\n")
        for i in range(0, len(only), 50):
            f.write("".join(only[i:i + 50]) + "\n")
    print(f"{len(only)} characters -> {out}")


if __name__ == "__main__":
    main()
