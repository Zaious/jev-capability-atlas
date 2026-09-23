#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。README 引用的數字都出自這裡。
  python score.py           # 算並寫出 runs/<日期>-scores.json
  python score.py --check   # 重算並跟已存檔的比，不一致就 exit 1
"""
import collections
import json
import os
import random
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BINS = 15
THRESHOLDS = [0.5, 0.7, 0.9]
BOOTSTRAP = 2000
BOOT_SEED = 43


def latest_run():
    runs = sorted(f for f in os.listdir(os.path.join(HERE, "runs"))
                  if f.endswith(".json") and not f.endswith("-scores.json"))
    return os.path.join(HERE, "runs", runs[-1])


def ece(pairs):
    b = [[] for _ in range(BINS)]
    for conf, ok in pairs:
        b[min(BINS - 1, int(conf * BINS))].append((conf, ok))
    return round(sum(len(x) / len(pairs) * abs(statistics.fmean(c for c, _ in x)
                                               - statistics.fmean(1.0 if o else 0.0 for _, o in x))
                     for x in b if x), 4)


def pct(v, q):
    v = sorted(v)
    return round(v[min(len(v) - 1, int(round(q * (len(v) - 1))))], 1)


def block(calls, labels):
    pairs = [(r["confidence"], r["choice"] == r["gold"]) for r in calls]
    by_item = collections.defaultdict(list)
    for r in calls:
        by_item[r["id"]].append(r["choice"])
    maj = collections.Counter(r["gold"] for r in calls).most_common(1)[0]
    per_class = {}
    for g in sorted({r["gold"] for r in calls}):
        sub = [r for r in calls if r["gold"] == g]
        wrong = collections.Counter(r["choice"] for r in sub if r["choice"] != g)
        per_class[g] = {"n": len(sub),
                        "recall": round(sum(1 for r in sub if r["choice"] == g) / len(sub), 3)}
        if wrong:
            per_class[g]["most_confused_with"] = wrong.most_common(1)[0][0]
    sweep = {}
    for t in THRESHOLDS:
        cov = [r for r in calls if r["confidence"] >= t]
        sweep[str(t)] = {"coverage": round(len(cov) / len(calls), 3),
                         "accuracy_on_covered": round(
                             sum(1 for r in cov if r["choice"] == r["gold"]) / len(cov), 3) if cov else None}
    return {
        "items": len(by_item), "calls": len(calls),
        "accuracy": round(statistics.fmean(1.0 if ok else 0.0 for _, ok in pairs), 4),
        "majority_class_baseline": round(maj[1] / len(calls), 4),
        "majority_class_label": maj[0],
        "chance": round(1.0 / len(labels), 4),
        "ece": ece(pairs),
        "mean_confidence": round(statistics.fmean(c for c, _ in pairs), 4),
        "same_answer_all_repeats": round(
            sum(1 for v in by_item.values() if len(set(v)) == 1) / len(by_item), 3),
        "per_class": per_class,
        "threshold_sweep": sweep,
        "latency_ms": {"p50": pct([r["latency_ms"] for r in calls], .50),
                       "p95": pct([r["latency_ms"] for r in calls], .95)},
    }


def paired(a_rows, b_rows):
    key = lambda r: (r["id"], r["repeat"])  # noqa: E731
    a = {key(r): r["choice"] == r["gold"] for r in a_rows}
    b = {key(r): r["choice"] == r["gold"] for r in b_rows}
    shared = sorted(set(a) & set(b))
    by_item = collections.defaultdict(list)
    for k in shared:
        by_item[k[0]].append((a[k], b[k]))
    items = sorted(by_item)

    def diff(sample):
        flat = [p for i in sample for p in by_item[i]]
        return (statistics.fmean(1.0 if y else 0.0 for _, y in flat)
                - statistics.fmean(1.0 if x else 0.0 for x, _ in flat))

    rng = random.Random(BOOT_SEED)
    draws = sorted(diff([rng.choice(items) for _ in items]) for _ in range(BOOTSTRAP))
    return {"items": len(items),
            "b_won": sum(1 for k in shared if b[k] and not a[k]),
            "b_lost": sum(1 for k in shared if a[k] and not b[k]),
            "accuracy_diff": round(diff(items), 4),
            "ci95": [round(draws[int(.025 * BOOTSTRAP)], 4), round(draws[int(.975 * BOOTSTRAP)], 4)]}


def main():
    run = json.load(open(latest_run(), encoding="utf-8"))
    labels = run["labels"]
    rows = collections.defaultdict(list)
    for r in run["results"]:
        if "error" not in r:
            rows[r["arm"]].append(r)

    arms = {}
    for arm, rs in sorted(rows.items()):
        arms[arm] = block(rs, labels)
        unmarked = [r for r in rs if not r["question_marked"]]
        arms[arm]["on_unmarked"] = block(unmarked, labels)     # 沒有問號的那 71%
        marked = [r for r in rs if r["question_marked"]]
        arms[arm]["on_question_marked"] = block(marked, labels)

    scores = {
        "run_file": os.path.basename(latest_run()), "run_date": run["run_date"],
        "model_answered": run["model_answered"], "errors": run["counts"]["errors"],
        "warmup_ms_excluded": run["warmup_ms_excluded"],
        "baselines": run["baselines"],
        "arms": arms,
        "context_effect": paired(rows["act_no_context"], rows["act_context"]),
        "context_effect_on_unmarked": paired(
            [r for r in rows["act_no_context"] if not r["question_marked"]],
            [r for r in rows["act_context"] if not r["question_marked"]]),
    }

    out = os.path.join(HERE, "runs", f"{run['run_date']}-scores.json")
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            print("MISMATCH: recomputed scores differ from", out)
            sys.exit(1)
        print("ok: recomputed scores match", os.path.basename(out))
        return

    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    b = run["baselines"]
    print(f"sample: majority {b['sample_majority_baseline']}  "
          f"punctuation shortcut {b['sample_punctuation_shortcut']}  "
          f"unmarked majority {b['sample_unmarked_majority_baseline']} (n={b['sample_unmarked_n']})")
    for arm, s in arms.items():
        print(f"\n{arm}: {s['items']} items")
        print(f"  ALL       acc {s['accuracy']}  (majority {s['majority_class_baseline']}, "
              f"punct shortcut {b['sample_punctuation_shortcut']})  ECE {s['ece']}  "
              f"same x3 {s['same_answer_all_repeats']}")
        u = s["on_unmarked"]
        print(f"  UNMARKED  acc {u['accuracy']}  (majority {u['majority_class_baseline']})  "
              f"ECE {u['ece']}   <- 這才是真正的題目")
        m = s["on_question_marked"]
        print(f"  MARKED    acc {m['accuracy']}  (majority {m['majority_class_baseline']})")
        print("  per class (all): " + ", ".join(
            f"{g} {v['recall']}" + (f"->{v.get('most_confused_with')}" if v.get("most_confused_with") else "")
            for g, v in s["per_class"].items()))
        print("  thresholds: " + ", ".join(
            f"{t}: cov {v['coverage']} acc {v['accuracy_on_covered']}"
            for t, v in s["threshold_sweep"].items()))
        print(f"  latency p50 {s['latency_ms']['p50']} / p95 {s['latency_ms']['p95']} ms")
    for k in ("context_effect", "context_effect_on_unmarked"):
        v = scores[k]
        print(f"\n{k} ({v['items']} items): {v['accuracy_diff']:+} 95% CI {v['ci95']}, "
              f"won {v['b_won']} / lost {v['b_lost']}")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
