#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""檢查繁體中文文字裡有沒有混進簡體字，有就 exit 1。
Check that no Simplified-only character slipped into the repo's Traditional
Chinese text; exit 1 if one did. Standard library only.

  python scripts/zh-check/check_zh.py            # 掃整個 repo / scan every tracked text file
  python scripts/zh-check/check_zh.py FILE...    # 只掃指定檔案 / scan only these files
  python scripts/zh-check/check_zh.py --selftest # 自我測試 / self-test both directions

字表 / character list: simplified_only.txt (derived from OpenCC by
gen_simplified_only.py), plus EXTRA_SUSPECTS below.
刻意保留的簡體 / intentional Simplified text (e.g. a Simplified-Chinese author's
name) goes in allowlist.txt as "path<TAB>substring".

為什麼有這支 / why this exists: the repo's first commit shipped Simplified
characters (写、际、处、没) inside Traditional text and nobody noticed for days.
It can't catch a wrong-but-real character (皮帝 for 皇帝); that needs a reader.
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 傳統字典裡是合法繁體字（「种」姓、「拮据」），但在現代台灣文字裡幾乎都是簡體滑手，
# 所以一併抓；真的要用就加進 allowlist.txt。
# Technically valid Traditional characters (the surname 种, 拮据) that in modern
# Taiwanese text are almost always a Simplified slip; flagged too, allowlist if intended.
EXTRA_SUSPECTS = "种据"

TEXT_EXT = {".md", ".yaml", ".yml", ".py", ".json", ".txt", ".toml", ".cfg", ".ini"}
TEXT_NAMES = {"NOTICE", "LICENSE"}
SKIP_PARTS = ("/runs/",)  # 收據不能手改，錯字要在 data/ 那一層就擋下 / receipts are immutable
SKIP_FILES = {"scripts/zh-check/simplified_only.txt", "scripts/zh-check/allowlist.txt"}


def load_chars():
    s = set()
    for line in open(os.path.join(HERE, "simplified_only.txt"), encoding="utf-8"):
        if not line.startswith("#"):
            s.update(line.strip())
    s.update(EXTRA_SUSPECTS)
    return s


def load_allowlist():
    allow = {}
    path = os.path.join(HERE, "allowlist.txt")
    if not os.path.exists(path):
        return allow
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].rstrip("\n").rstrip()
        if not line.strip() or "\t" not in line:
            continue
        p, sub = line.split("\t", 1)
        allow.setdefault(p.strip(), []).append(sub.strip())
    return allow


def tracked_files():
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True,
                             encoding="utf-8", check=True).stdout.splitlines()
    except Exception:
        out = []
        for d, _, fs in os.walk(ROOT):
            if "/.git" in d.replace(os.sep, "/"):
                continue
            out += [os.path.relpath(os.path.join(d, f), ROOT) for f in fs]
    return [f.replace(os.sep, "/") for f in out]


def wanted(rel):
    name = rel.rsplit("/", 1)[-1]
    if rel in SKIP_FILES or any(part in "/" + rel for part in SKIP_PARTS):
        return False
    return os.path.splitext(name)[1].lower() in TEXT_EXT or name in TEXT_NAMES


def covered(text, pos, subs):
    for sub in subs:
        start = text.find(sub)
        while start != -1:
            if start <= pos < start + len(sub):
                return True
            start = text.find(sub, start + 1)
    return False


def find_hits(text, chars, subs):
    return [(pos, ch) for pos, ch in enumerate(text) if ch in chars and not covered(text, pos, subs)]


def selftest():
    chars = load_chars()
    checks = [
        ("catches 写际处没专词", all(c in chars for c in "写际处没专词")),
        ("catches extra suspects 种据", all(c in chars for c in "种据")),
        ("leaves Taiwanese forms alone", not any(c in chars for c in "群床峰里台后裡著線皇帝康熙釘實際寫處沒專詞")),
        ("flags one hit in 這條没有", [ch for _, ch in find_hits("這條没有 data/", chars, [])] == ["没"]),
        ("clean text has no hits", find_hits("這條沒有 data/，此處是主要路徑。", chars, []) == []),
        ("allowlist covers the listed substring", find_hits("作者李不凯說", chars, ["李不凯"]) == []),
        ("allowlist doesn't leak outside it", [ch for _, ch in find_hits("李不凯與凯旋", chars, ["李不凯"])] == ["凯"]),
    ]
    for name, ok in checks:
        print(("✓ " if ok else "✗ ") + name)
    bad = sum(1 for _, ok in checks if not ok)
    print(f"selftest: {len(checks) - bad}/{len(checks)} passed")
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    chars = load_chars()
    allow = load_allowlist()
    files = [os.path.relpath(os.path.abspath(a), ROOT).replace(os.sep, "/") for a in argv] if argv else tracked_files()
    hits = []
    for rel in files:
        if not wanted(rel):
            continue
        try:
            text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        subs = allow.get(rel, []) + allow.get("*", [])
        for pos, ch in find_hits(text, chars, subs):
            line_no = text.count("\n", 0, pos) + 1
            line_start = text.rfind("\n", 0, pos) + 1
            col = pos - line_start + 1
            ctx = text[max(line_start, pos - 12):pos + 12].replace("\n", " ")
            hits.append((rel, line_no, col, ch, ctx))
    for rel, line_no, col, ch, ctx in hits:
        print(f"{rel}:{line_no}:{col}: 簡體字 / Simplified「{ch}」 …{ctx}…")
    if hits:
        print(f"\n✗ {len(hits)} 處 / hit(s). 改成繁體；刻意保留的話加進 scripts/zh-check/allowlist.txt"
              f" / fix to Traditional, or allowlist if intentional.")
        return 1
    print(f"✓ 沒有簡體字 / no Simplified characters ({sum(1 for f in files if wanted(f))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
