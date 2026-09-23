#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。/ Recompute from the receipts.
  python score.py           # 寫出 runs/<date>-scores.json
  python score.py --check   # 重算並比對，不一致就 exit 1
"""
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLDS = [0.5, 0.7]
KINDS = ["cut", "kept_lookalike", "unchanged"]


def auc(pos, neg):
    return round(sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg)), 4)


def main():
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]
    kind = {c["id"]: c["kind"] for c in cases}
    label = {c["id"]: c["label"] for c in cases}
    run_name = sorted(f for f in os.listdir(os.path.join(HERE, "runs")) if f.endswith(".json") and f.count("-") == 2)[-1]
    run = json.load(open(os.path.join(HERE, "runs", run_name), encoding="utf-8"))

    arms = {}
    for arm in run["meta"]["instructions"]:
        per = {}
        for r in run["rows"]:
            if r["arm"] == arm and "error" not in r:
                per.setdefault(r["id"], []).append(r["p_yes"])
        mp = {i: round(statistics.fmean(v), 4) for i, v in per.items()}
        arms[arm] = {
            "auc_cut_vs_all_kept": auc([mp[i] for i in mp if label[i]], [mp[i] for i in mp if not label[i]]),
            "auc_cut_vs_lookalike": auc([mp[i] for i in mp if kind[i] == "cut"],
                                        [mp[i] for i in mp if kind[i] == "kept_lookalike"]),
            "mean_p": {k: round(statistics.fmean(mp[i] for i in mp if kind[i] == k), 4) for k in KINDS},
            "flagged": {str(t): {k: f"{sum(mp[i] >= t for i in mp if kind[i] == k)}/{sum(kind[i] == k for i in mp)}"
                                 for k in KINDS} for t in THRESHOLDS},
            "same_side_all_repeats": round(sum(len({p >= 0.5 for p in v}) == 1 for v in per.values()) / len(per), 4),
            "per_case_mean_p": dict(sorted(mp.items())),
        }
    scores = {"run": run_name, "models": run["meta"]["response_models"], "calls": run["meta"]["calls"],
              "errors": run["meta"]["errors"], "input_tokens": run["meta"]["input_tokens"], "arms": arms}
    out = os.path.join(HERE, "runs", run_name.replace(".json", "-scores.json"))
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            sys.exit(f"MISMATCH: recomputed scores differ from {out}")
        print("ok: recomputed scores match", os.path.basename(out))
        return
    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for arm, a in arms.items():
        print(f"{arm}: AUC cut vs kept {a['auc_cut_vs_all_kept']}, cut vs look-alike {a['auc_cut_vs_lookalike']}, "
              f"mean p {a['mean_p']}, flagged {a['flagged']}, stable {a['same_side_all_repeats']}")
    print("wrote", out)


if __name__ == "__main__":
    main()
