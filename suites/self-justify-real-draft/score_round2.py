#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第二輪計分:每個維度與事先寫死的等權組合,各自的分離能力。
Round 2 scoring: separation for each dimension and for the pre-registered equal-weight combination.
  python score_round2.py           # 寫出 runs/<date>-round2-scores.json
  python score_round2.py --check   # 重算並比對,不一致就 exit 1
"""
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ["cut", "kept_lookalike", "unchanged"]


def auc(pos, neg):
    return round(sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg)), 4)


def main():
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]
    kind = {c["id"]: c["kind"] for c in cases}
    man = json.load(open(os.path.join(HERE, "data", "round2_manifest.json"), encoding="utf-8"))
    dims = {k: v["direction"] for k, v in man["dimensions"].items()}
    name = sorted(f for f in os.listdir(os.path.join(HERE, "runs")) if f.endswith("-round2.json"))[-1]
    run = json.load(open(os.path.join(HERE, "runs", name), encoding="utf-8"))

    per = {}
    for r in run["rows"]:
        if "error" not in r:
            per.setdefault(r["id"], []).append(r["p"])
    mean = {i: {k: statistics.fmean(p[k] for p in v) for k in dims} for i, v in per.items()}
    # 方向對齊後的分數:高=不必要/替作者辯護
    aligned = {i: {k: (m[k] if dims[k] > 0 else 1 - m[k]) for k in dims} for i, m in mean.items()}
    aligned_combo = {i: statistics.fmean(a.values()) for i, a in aligned.items()}

    def report(score):
        g = {k: [score[i] for i in score if kind[i] == k] for k in KINDS}
        return {"auc_cut_vs_lookalike": auc(g["cut"], g["kept_lookalike"]),
                "auc_cut_vs_all_kept": auc(g["cut"], g["kept_lookalike"] + g["unchanged"]),
                "mean": {k: round(statistics.fmean(v), 4) for k, v in g.items()},
                "flagged_at_0.5": {k: f"{sum(x >= 0.5 for x in v)}/{len(v)}" for k, v in g.items()}}

    scores = {"run": name, "models": run["meta"]["response_models"], "calls": run["meta"]["calls"],
              "errors": run["meta"]["errors"], "input_tokens": run["meta"]["input_tokens"],
              "dimensions": {k: {"direction": d, **report({i: aligned[i][k] for i in aligned})} for k, d in dims.items()},
              "combo": report(aligned_combo),
              "per_case_aligned": {i: {**{k: round(v, 4) for k, v in aligned[i].items()},
                                       "combo": round(aligned_combo[i], 4)} for i in sorted(aligned)}}
    out = os.path.join(HERE, "runs", name.replace(".json", "-scores.json"))
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            sys.exit(f"MISMATCH: recomputed scores differ from {out}")
        print("ok: recomputed scores match", os.path.basename(out))
        return
    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{'dimension':<16}{'dir':>4}  {'cut/look AUC':>12}  {'cut/all AUC':>11}   mean cut / look / unchanged     flagged@0.5")
    for k, v in list(scores["dimensions"].items()) + [("COMBO", {**scores["combo"], "direction": 0})]:
        m = v["mean"]
        print(f"{k:<16}{v['direction']:>+4}  {v['auc_cut_vs_lookalike']:>12}  {v['auc_cut_vs_all_kept']:>11}   "
              f"{m['cut']:.2f} / {m['kept_lookalike']:.2f} / {m['unchanged']:.2f}     {v['flagged_at_0.5']}")
    print("wrote", out)


if __name__ == "__main__":
    main()
