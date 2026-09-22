#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用 Jev 找出「寫成另一個字」的可疑句子，列給人看；不擋 commit。
Ask Jev which Traditional-Chinese sentences look like they contain a wrong character,
and list them for a human to check. Advisory only: never fails a commit.

  python scripts/zh-check/proofread_jev.py                 # 本次改動的 .md 檔 / .md files changed vs HEAD
  python scripts/zh-check/proofread_jev.py FILE...         # 指定檔案 / these files
  python scripts/zh-check/proofread_jev.py --all           # 所有追蹤中的 .md / every tracked .md
  python scripts/zh-check/proofread_jev.py --threshold 0.5

需要 TYPESAFE_API_KEY。簡體字交給 check_zh.py（確定性、零成本）；這支只處理字元清單抓不到的那一類。
Needs TYPESAFE_API_KEY. Simplified characters are check_zh.py's job; this covers only the
wrong-but-real kind (皮帝 for 皇帝) that no character list can catch.

門檻依據 / threshold basis: suites/zh-proofreading/ (2026-09-22) -- at 0.5, 2.0% of the
repo's own clean sentences were flagged and 67% of SIGHAN learner typos were caught.
Sentences containing code spans are skipped: stripping the code leaves holes that read as errors.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "common"))

QUESTION = ("Does this Traditional Chinese text contain a wrong character — a real character used in place "
            "of the correct one, producing a word that doesn't exist or doesn't fit (for example 皮帝 instead "
            "of 皇帝)? Ignore factual accuracy.")
SENT_SPLIT = re.compile(r"(?<=[。！？])")
CJK = re.compile(r"[一-鿿]")
SKIP_PREFIX = ("|", "#", ">", "```", "<")


def git_files(args):
    out = subprocess.run(["git", "-C", ROOT] + args, capture_output=True, text=True, encoding="utf-8").stdout
    return [f for f in out.splitlines() if f.endswith(".md")]


def sentences(rel):
    text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    in_code = False
    for n, para in enumerate(text.split("\n"), 1):
        if para.startswith("```"):
            in_code = not in_code
            continue
        if in_code or para.startswith(SKIP_PREFIX):
            continue
        for s in SENT_SPLIT.split(para):
            if "`" in s:
                continue
            s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
            # 來源標記（🔬📚📖💭）保留：刪掉會在句子裡留下空洞，被當成錯字
            # keep the source tags: deleting them leaves holes that read as typos
            s = s.replace("**", "").strip(" -*")
            if len(s) >= 8 and len(CJK.findall(s)) / max(1, len(s)) > 0.4:
                yield n, s


def main(argv):
    threshold = 0.5
    if "--threshold" in argv:
        i = argv.index("--threshold")
        threshold = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if "--all" in argv:
        files = git_files(["ls-files"])
    elif argv:
        files = [os.path.relpath(os.path.abspath(a), ROOT).replace(os.sep, "/") for a in argv]
    else:
        files = sorted(set(git_files(["diff", "--name-only", "HEAD"]) +
                           git_files(["ls-files", "--others", "--exclude-standard"])))
    items = [(rel, n, s) for rel in files if os.path.exists(os.path.join(ROOT, rel)) for n, s in sentences(rel)]
    if not items:
        print("沒有要檢查的中文句子 / no Chinese sentences to check")
        return 0

    from jev_client import get_client
    from typesafe_sdk import Noul
    client = get_client()
    q = {"wrong_char": Noul(instructions=QUESTION)}

    def ask(item):
        rel, n, s = item
        try:
            return rel, n, s, client.system_one(state=s, model="jev-latest", questions=q).answers["wrong_char"].noul
        except Exception as e:  # advisory tool: report and keep going
            return rel, n, s, f"error: {type(e).__name__}"

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(ask, items))
    flagged = [r for r in results if isinstance(r[3], float) and r[3] >= threshold]
    errors = [r for r in results if not isinstance(r[3], float)]
    for rel, n, s, p in sorted(flagged, key=lambda r: -r[3]):
        print(f"{rel}:{n}: {p:.2f}  {s}")
    print(f"\n{len(flagged)} / {len(results)} 句可疑（門檻 {threshold}），請人工確認；這支不會擋 commit。"
          f"\n{len(flagged)} of {len(results)} sentences flagged at {threshold} -- check them by hand; advisory only."
          + (f"\n{len(errors)} 句呼叫失敗 / calls failed" if errors else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
