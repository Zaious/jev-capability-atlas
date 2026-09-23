#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""在本機跑 babel-antiai 的確定性掃描器，只記錄每段 SELF-JUSTIFY 有沒有命中；存成 runs/<date>-scanner.json。
Run babel-antiai's deterministic scanner locally and record only whether SELF-JUSTIFY fired
on each case. Saves runs/<date>-scanner.json.

babel-antiai 是本 repo 維護者的私有 skill，掃描器程式碼沒有公開；這支腳本只呼叫它、
不包含它的任何規則。沒有這支掃描器的人無法重跑這一臂，但收據裡的逐段結果與腳本的
sha256 足以核對我們報告的數字。
babel-antiai is the maintainer's private skill and its scanner is not public. This script
only invokes it and contains none of its rules. Without the scanner this arm can't be
re-run, but the per-case verdicts and the script's sha256 in the receipt are enough to
check the numbers we report.

  BABEL_ANTIAI_SCAN=<path to ai-quality-scan.sh> python baseline_scan.py
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(os.path.expanduser("~"), ".claude", "skills", "babel-antiai", "scripts", "ai-quality-scan.sh")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def main():
    scan = os.environ.get("BABEL_ANTIAI_SCAN", DEFAULT)
    if not os.path.isfile(scan):
        sys.exit(f"scanner not found: {scan} (set BABEL_ANTIAI_SCAN)")
    sha = hashlib.sha256(open(scan, "rb").read()).hexdigest()
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]
    rows, version = [], None
    with tempfile.TemporaryDirectory() as tmp:
        for c in cases:
            path = os.path.join(tmp, f"{c['id']}.md")
            open(path, "w", encoding="utf-8").write(c["text"] + "\n")
            out = subprocess.run(["bash", scan, "--lang", "zh", "--verbose", path],
                                 capture_output=True, text=True, encoding="utf-8").stdout
            out = ANSI.sub("", out)
            if version is None:
                m = re.search(r"ai-quality-scan (v[\d.]+)", out)
                version = m.group(1) if m else "unknown"
            skipped = "未掃描" in out
            # 摘要行長這樣：「SELF-JUSTIFY:宣告1 辯護1 工時1」，後面可能還接別的維度，只取中文形狀名＋次數
            # The summary line reads "SELF-JUSTIFY:<shape><n> ...", possibly followed by other
            # dimensions; take only CJK shape names with counts.
            m = re.search(r"SELF-JUSTIFY:((?:[一-鿿]+\d+ ?)+)", out)
            shapes = {k: int(v) for k, v in re.findall(r"([一-鿿]+)(\d+)", m.group(1))} if m else {}
            hit = bool(shapes) or "[SELF-JUSTIFY]" in out
            rows.append({"id": c["id"], "hit": hit, "shapes": shapes, "skipped": skipped})
    meta = {"scanner": "babel-antiai ai-quality-scan.sh", "version": version, "sha256": sha,
            "args": "--lang zh --verbose", "date": datetime.date.today().isoformat(),
            "cases": len(rows), "skipped": sum(r["skipped"] for r in rows)}
    out = os.path.join(HERE, "runs", f"{meta['date']}-scanner.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{meta['scanner']} {version}  sha256 {sha[:12]}  hits {sum(r['hit'] for r in rows)}/{len(rows)}  "
          f"skipped {meta['skipped']}")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
