#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據算出抓錯率與誤報率 / catch rate and false-alarm rate from the receipt.

  python score.py [runs/<date>.json]
"""
import sys, os, json, glob

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLDS = (0.3, 0.5, 0.7)


def auc(pos, neg):
    """Probability a random positive scores above a random negative (ties count half)."""
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 4)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(HERE, "runs", "????-??-??.json")))[-1]
    d = json.load(open(path, encoding="utf-8"))
    res = d["results"]
    print(f"receipt: {os.path.relpath(path, HERE)}  models: {d['meta']['response_models']}  calls: {d['meta']['calls']}  errors: {d['meta']['errors']}\n")
    summary = {}
    for q in d["meta"]["instructions"]:
        s = {name: [r["p"][q] for r in rows if q in r["p"]] for name, rows in res.items()}
        summary[q] = {
            "auc_sighan_error_vs_sighan_clean": auc(s["sighan_error"], s["sighan_clean"]),
            "auc_sighan_error_vs_repo_clean": auc(s["sighan_error"], s["repo_clean"]),
            "at_threshold": {t: {"catch_sighan_error": round(sum(x >= t for x in s["sighan_error"]) / len(s["sighan_error"]), 3),
                                 "false_alarm_sighan_clean": round(sum(x >= t for x in s["sighan_clean"]) / len(s["sighan_clean"]), 3),
                                 "false_alarm_repo_clean": round(sum(x >= t for x in s["repo_clean"]) / len(s["repo_clean"]), 3)}
                             for t in THRESHOLDS},
            "repo_real_typo": {r["id"]: r["p"][q] for r in res["repo_real_typo"]},
        }
        print(f"## {q}")
        print(f"  AUC  sighan_error vs sighan_clean: {summary[q]['auc_sighan_error_vs_sighan_clean']}"
              f"   vs repo_clean: {summary[q]['auc_sighan_error_vs_repo_clean']}")
        print("  threshold | catch (sighan_error) | false alarm (sighan_clean) | false alarm (repo_clean)")
        for t, v in summary[q]["at_threshold"].items():
            print(f"    {t:.1f}    |        {v['catch_sighan_error']:.3f}         |          {v['false_alarm_sighan_clean']:.3f}           |         {v['false_alarm_repo_clean']:.3f}")
        print(f"  our real typos: {summary[q]['repo_real_typo']}\n")
    print("repo_clean sentences at or above 0.5 on wrong_char (inspect each by hand):")
    for r in sorted(res["repo_clean"], key=lambda r: -r["p"].get("wrong_char", 0)):
        if r["p"].get("wrong_char", 0) >= 0.5:
            print(f"  {r['p']['wrong_char']:.2f}  {r['id']}  {r['text']}")
    json.dump(summary, open(path.replace(".json", "-scores.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
