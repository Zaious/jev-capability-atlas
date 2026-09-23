#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。README 引用的數字都出自這裡。
Recompute from the receipts; every figure the README quotes comes from here.

  python score.py           # 算並寫出 runs/<日期>-scores.json / compute and write runs/<date>-scores.json
  python score.py --check   # 重算並跟已存檔的比，不一致就 exit 1 / recompute and exit 1 on mismatch
"""
import json
import os
import random
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLD = 0.5
SWEEP = [0.3, 0.5, 0.7]
BOOTSTRAP = 2000
BOOT_SEED = 47
STRATA = ["S1", "S2", "S3", "S4", "S5"]


def run_files():
    names = sorted(os.listdir(os.path.join(HERE, "runs")))
    jev = [n for n in names if n.endswith(".json") and "-" not in n[len("2026-09-23"):]]
    scan = [n for n in names if n.endswith("-scanner.json")]
    return os.path.join(HERE, "runs", jev[-1]), os.path.join(HERE, "runs", scan[-1])


def auc(scores_pos, scores_neg):
    wins = sum((p > n) + 0.5 * (p == n) for p in scores_pos for n in scores_neg)
    return round(wins / (len(scores_pos) * len(scores_neg)), 4)


def by_stratum(cases, predicted):
    out = {}
    for s in STRATA:
        ids = [c["id"] for c in cases if c["stratum"] == s]
        flagged = sum(predicted[i] for i in ids)
        out[s] = {"n": len(ids), "flagged": flagged, "rate": round(flagged / len(ids), 4)}
    return out


def summary(cases, predicted):
    tp = sum(predicted[c["id"]] and c["label"] for c in cases)
    fp = sum(predicted[c["id"]] and not c["label"] for c in cases)
    fn = sum((not predicted[c["id"]]) and c["label"] for c in cases)
    tn = len(cases) - tp - fp - fn
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"accuracy": round((tp + tn) / len(cases), 4), "precision": round(prec, 4),
            "recall": round(rec, 4), "f1": round(2 * prec * rec / (prec + rec), 4) if prec + rec else 0.0,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn, "by_stratum": by_stratum(cases, predicted)}


def paired(cases, pred_a, pred_b, subset=None):
    """b 相對 a 的正確率差，逐題配對 bootstrap。/ accuracy of b minus a, case-paired bootstrap."""
    cs = [c for c in cases if subset is None or c["stratum"] in subset]
    ok_a = [pred_a[c["id"]] == c["label"] for c in cs]
    ok_b = [pred_b[c["id"]] == c["label"] for c in cs]
    diff = statistics.fmean(ok_b) - statistics.fmean(ok_a)
    rng = random.Random(BOOT_SEED)
    boots = []
    for _ in range(BOOTSTRAP):
        idx = [rng.randrange(len(cs)) for _ in cs]
        boots.append(statistics.fmean(ok_b[i] for i in idx) - statistics.fmean(ok_a[i] for i in idx))
    boots.sort()
    return {"items": len(cs), "accuracy_diff": round(diff, 4),
            "ci95": [round(boots[int(0.025 * BOOTSTRAP)], 4), round(boots[int(0.975 * BOOTSTRAP) - 1], 4)],
            "b_won": sum(b and not a for a, b in zip(ok_a, ok_b)),
            "b_lost": sum(a and not b for a, b in zip(ok_a, ok_b))}


def main():
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]
    label = {c["id"]: c["label"] for c in cases}
    jev_path, scan_path = run_files()
    jev = json.load(open(jev_path, encoding="utf-8"))
    scan = json.load(open(scan_path, encoding="utf-8"))

    preds, arms = {}, {}
    for arm in jev["meta"]["instructions"]:
        rows = [r for r in jev["rows"] if r["arm"] == arm and "error" not in r]
        per = {}
        for r in rows:
            per.setdefault(r["id"], []).append(r["p_yes"])
        mean_p = {i: statistics.fmean(v) for i, v in per.items()}
        pred = {i: mean_p[i] >= THRESHOLD for i in mean_p}
        preds[arm] = pred
        stable = sum(len({p >= THRESHOLD for p in v}) == 1 for v in per.values())
        lat = sorted(r["latency_ms"] for r in rows)
        arms[arm] = {
            **summary(cases, pred),
            "auc": auc([mean_p[i] for i in mean_p if label[i]], [mean_p[i] for i in mean_p if not label[i]]),
            "same_side_all_repeats": round(stable / len(per), 4),
            "mean_p_by_stratum": {s: round(statistics.fmean(mean_p[c["id"]] for c in cases if c["stratum"] == s), 4)
                                  for s in STRATA},
            "threshold_sweep": {str(t): summary(cases, {i: mean_p[i] >= t for i in mean_p})["by_stratum"]
                                for t in SWEEP},
            "latency_ms": {"p50": lat[len(lat) // 2], "p95": lat[int(0.95 * (len(lat) - 1))]},
            "per_case_mean_p": {i: round(mean_p[i], 4) for i in sorted(mean_p)},
        }

    scan_pred = {r["id"]: r["hit"] for r in scan["rows"]}
    preds["scanner"] = scan_pred
    arms["scanner"] = {**summary(cases, scan_pred),
                       "skipped": scan["meta"]["skipped"],
                       "hits_by_case": {r["id"]: r["shapes"] for r in scan["rows"] if r["hit"]}}

    comparisons = {}
    for a, b in [("scanner", "J1_criterion"), ("scanner", "J2_with_exceptions"), ("J1_criterion", "J2_with_exceptions")]:
        comparisons[f"{b}_vs_{a}"] = {"all": paired(cases, preds[a], preds[b]),
                                      "S2_no_marker": paired(cases, preds[a], preds[b], {"S2"}),
                                      "S3_legit_with_shape": paired(cases, preds[a], preds[b], {"S3"})}

    # 判準作者事後的覆核：原標籤不動，另算一份。/ The criterion author's later review: original labels kept, scored separately.
    review_path = os.path.join(HERE, "data", "labels-author-review.json")
    author_labels = None
    if os.path.isfile(review_path):
        review = json.load(open(review_path, encoding="utf-8"))
        cases_a = [{**c, "label": review["overrides"].get(c["id"], c["label"])} for c in cases]
        lab_a = {c["id"]: c["label"] for c in cases_a}
        author_labels = {"reviewed": review["reviewed"], "overridden": sorted(review["overrides"]),
                         "uncertain": review.get("uncertain", []), "arms": {}}
        for arm, pred in preds.items():
            entry = summary(cases_a, pred)
            if arm != "scanner":
                mp = arms[arm]["per_case_mean_p"]
                entry["auc"] = auc([mp[i] for i in mp if lab_a[i]], [mp[i] for i in mp if not lab_a[i]])
            author_labels["arms"][arm] = entry

    scores = {"jev_run": os.path.basename(jev_path), "scanner_run": os.path.basename(scan_path),
              "author_labels": author_labels,
              "models": jev["meta"]["response_models"], "calls": jev["meta"]["calls"],
              "errors": jev["meta"]["errors"], "input_tokens": jev["meta"]["input_tokens"],
              "warmup_ms_excluded": jev["meta"]["warmup_ms_excluded"],
              "scanner": {k: scan["meta"][k] for k in ("version", "sha256", "args")},
              "threshold": THRESHOLD, "arms": arms, "comparisons": comparisons}

    out = os.path.join(HERE, "runs", f"{jev['meta']['date']}-scores.json")
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            print("MISMATCH: recomputed scores differ from", out)
            sys.exit(1)
        print("ok: recomputed scores match", os.path.basename(out))
        return
    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"{scores['models']}  calls {scores['calls']}  errors {scores['errors']}  tokens {scores['input_tokens']}")
    print(f"{'arm':<20} {'acc':>6} {'prec':>6} {'rec':>6}   " + "  ".join(f"{s}" for s in STRATA) + "   (flagged/n)")
    for arm, s in arms.items():
        st = "  ".join(f"{v['flagged']:>2}/{v['n']:<2}" for v in s["by_stratum"].values())
        print(f"{arm:<20} {s['accuracy']:>6} {s['precision']:>6} {s['recall']:>6}   {st}")
    for arm in ("J1_criterion", "J2_with_exceptions"):
        a = arms[arm]
        print(f"{arm}: AUC {a['auc']}  same side x3 {a['same_side_all_repeats']}  "
              f"mean p by stratum {a['mean_p_by_stratum']}  latency p50/p95 {a['latency_ms']['p50']}/{a['latency_ms']['p95']} ms")
    for k, v in comparisons.items():
        for sub, r in v.items():
            print(f"{k} [{sub}] n={r['items']}: {r['accuracy_diff']:+} CI {r['ci95']}  won {r['b_won']} lost {r['b_lost']}")
    print("wrote", out)


if __name__ == "__main__":
    main()
