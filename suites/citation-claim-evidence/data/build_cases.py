#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從一篇論文的引用查核帳(ledger.yaml)抽出已判定的「主張＋證據引句＋判定」,寫成 cases.json。
Build cases.json from the judged rows of one paper's citation-audit ledger.

來源:維護者自己的論文 philosophy-of-interaction-reversibility-2026(前一版已公開於 Zenodo),
私人 repo chronicle-lex 內的 ledger.yaml。判定(ok / misread)由查核流程對照被引文獻全文做出,
不是本測試組作者事後判斷。cases.json 已凍結進本 repo,一般不必重建。
Source: the maintainer's own paper (an earlier version is public on Zenodo); verdicts were made by
the audit process against the cited sources' full texts, not by this suite's author afterwards.

  CHRONICLE_LEX=<path> python build_cases.py
"""
import json
import os
import re
import subprocess
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("CHRONICLE_LEX", "M:/ChronicleCore-Forge/chronicle-lex")
LEDGER = "papers/philosophy-of-interaction-reversibility-2026/ledger.yaml"
EXCLUDE = {
    # 只核到摘要層級,判定本身帶保留(ledger 原文:「ok(僅就摘要層級;全文層級見…警示)」)
    "yee2007proteus": "verdict qualified: abstract-level only",
    # 資料錯置,判定不適用
    "may1975courage": "not-applicable (data misplacement in the ledger)",
}


def main():
    commit = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h", "--", LEDGER],
                            capture_output=True, text=True).stdout.strip()
    raw = subprocess.run(["git", "-C", REPO, "show", f"{commit}:{LEDGER}"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    entries = yaml.safe_load(raw)["entries"]
    cases, excluded = [], []
    for x in entries:
        m = re.match(r"\[(\d+)\]", x.get("ref") or "")
        for n, c in enumerate(x["claims"], 1):
            v = c.get("verdict")
            if not v:
                continue
            if x["key"] in EXCLUDE:
                excluded.append({"work": x["key"], "reason": EXCLUDE[x["key"]]})
                continue
            assert v in ("ok", "misread"), (x["key"], v)
            assert c.get("evidence") and m, x["key"]
            cases.append({"id": f"{x['key']}#{n}", "cited_as": f"[{m.group(1)}]", "role": x["role"],
                          "label": "misread" if v == "misread" else "ok",
                          "claim": c["text"].strip(),
                          "quotes": [{"quote": e["quote"].strip(), "where": e.get("where")} for e in c["evidence"]]})
    out = {"frozen": "2026-09-23",
           "source": {"paper": "philosophy-of-interaction-reversibility-2026 (the maintainer's own paper; an earlier "
                               "version is public on Zenodo, DOI 10.5281/zenodo.21225988)",
                      "ledger_commit": commit},
           "license": "Claim sentences are excerpts of the maintainer's manuscript, published with permission; "
                      "quotes are short attributed excerpts of the cited works. Neither is covered by this repo's MIT license.",
           "excluded": excluded, "cases": cases}
    json.dump(out, open(os.path.join(HERE, "cases.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ledger @ {commit}: {len(cases)} cases "
          f"({sum(c['label'] == 'ok' for c in cases)} ok, {sum(c['label'] == 'misread' for c in cases)} misread), "
          f"{len(excluded)} excluded")


if __name__ == "__main__":
    main()
