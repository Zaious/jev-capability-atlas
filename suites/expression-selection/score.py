#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算所有數字。README 引用的數字都要出自這裡。
Recompute every number from the receipts. Anything quoted in README comes from here.

  python score.py                       # 算並寫出 runs/<日期>-scores.json
  python score.py --check               # 重算並跟已存檔的比，不一致就 exit 1
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
THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]
BOOTSTRAP = 2000
BOOT_SEED = 23
NEUTRAL = {"meld_no_context": "neutral", "meld_context": "neutral", "zh_single": "平淡語氣"}


def latest_run():
    runs = sorted(f for f in os.listdir(os.path.join(HERE, "runs"))
                  if f.endswith(".json") and not f.endswith("-scores.json"))
    return os.path.join(HERE, "runs", runs[-1])


def ece(pairs):
    """pairs = [(信心, 對不對)]；15 格、等寬，按最高機率分箱。"""
    buckets = [[] for _ in range(BINS)]
    for conf, ok in pairs:
        buckets[min(BINS - 1, int(conf * BINS))].append((conf, ok))
    total = len(pairs)
    return round(sum(len(b) / total * abs(statistics.fmean(c for c, _ in b)
                                          - statistics.fmean(1.0 if o else 0.0 for _, o in b))
                     for b in buckets if b), 4)


def percentile(values, q):
    values = sorted(values)
    return round(values[min(len(values) - 1, int(round(q * (len(values) - 1))))], 1)


def arm_stats(rows, labels):
    calls = [r for r in rows if "error" not in r]
    correct = [r["choice"] == r["gold"] for r in calls]
    pairs = [(r["confidence"], r["choice"] == r["gold"]) for r in calls]
    brier = statistics.fmean(
        sum((r["probabilities"].get(k, 0.0) - (1.0 if k == r["gold"] else 0.0)) ** 2 for k in labels)
        for r in calls)

    by_item = collections.defaultdict(list)
    for r in calls:
        by_item[r["id"]].append(r)
    stable = sum(1 for rs in by_item.values() if len({r["choice"] for r in rs}) == 1)

    per_class = {}
    confusion = collections.Counter()
    for gold in sorted({r["gold"] for r in calls}):
        sub = [r for r in calls if r["gold"] == gold]
        hit = sum(1 for r in sub if r["choice"] == gold)
        per_class[gold] = {"n": len(sub), "recall": round(hit / len(sub), 3)}
        wrong = collections.Counter(r["choice"] for r in sub if r["choice"] != gold)
        if wrong:
            per_class[gold]["most_confused_with"] = wrong.most_common(1)[0][0]
        for r in sub:
            if r["choice"] != gold:
                confusion[f"{gold} -> {r['choice']}"] += 1

    neutral = NEUTRAL[calls[0]["arm"]]
    sweep = {}
    for t in THRESHOLDS:
        covered = [r for r in calls if r["confidence"] >= t]
        after = [(r["choice"] if r["confidence"] >= t else neutral) == r["gold"] for r in calls]
        sweep[str(t)] = {
            "coverage": round(len(covered) / len(calls), 3),
            "accuracy_on_covered": round(
                sum(1 for r in covered if r["choice"] == r["gold"]) / len(covered), 3) if covered else None,
            "accuracy_after_neutral_fallback": round(statistics.fmean(1.0 if x else 0.0 for x in after), 3),
        }

    lat = [r["latency_ms"] for r in calls]
    return {
        "items": len(by_item), "calls": len(calls),
        "accuracy": round(statistics.fmean(1.0 if c else 0.0 for c in correct), 4),
        "majority_baseline": round(1.0 / len(labels), 4),
        "ece": ece(pairs), "brier": round(brier, 4),
        "mean_confidence": round(statistics.fmean(c for c, _ in pairs), 4),
        "same_answer_all_repeats": round(stable / len(by_item), 3),
        "per_class": per_class,
        "top_confusions": [{"pair": k, "n": v} for k, v in confusion.most_common(5)],
        "threshold_sweep": sweep,
        "latency_ms": {"p50": percentile(lat, .50), "p95": percentile(lat, .95), "max": round(max(lat), 1)},
    }


def paired_meld(rows_a, rows_b):
    """同一題、同一次重複，兩臂配對比較（bootstrap 重抽的是題目）。"""
    key = lambda r: (r["id"], r["repeat"])  # noqa: E731
    a = {key(r): r["choice"] == r["gold"] for r in rows_a if "error" not in r}
    b = {key(r): r["choice"] == r["gold"] for r in rows_b if "error" not in r}
    shared = sorted(set(a) & set(b))
    by_item = collections.defaultdict(list)
    for k in shared:
        by_item[k[0]].append((a[k], b[k]))
    items = sorted(by_item)
    won = sum(1 for k in shared if b[k] and not a[k])
    lost = sum(1 for k in shared if a[k] and not b[k])

    def diff(sample):
        flat = [pair for i in sample for pair in by_item[i]]
        return (statistics.fmean(1.0 if y else 0.0 for _, y in flat)
                - statistics.fmean(1.0 if x else 0.0 for x, _ in flat))

    rng = random.Random(BOOT_SEED)
    draws = sorted(diff([rng.choice(items) for _ in items]) for _ in range(BOOTSTRAP))
    return {"items": len(items), "context_won": won, "context_lost": lost,
            "accuracy_diff": round(diff(items), 4),
            "ci95": [round(draws[int(.025 * BOOTSTRAP)], 4), round(draws[int(.975 * BOOTSTRAP)], 4)]}


def main():
    run = json.load(open(latest_run(), encoding="utf-8"))
    rows = collections.defaultdict(list)
    for r in run["results"]:
        rows[r["arm"]].append(r)
    labels = run["labels"]

    scores = {
        "run_file": os.path.basename(latest_run()),
        "run_date": run["run_date"],
        "model_answered": run["model_answered"],
        "warmup_ms_excluded": run["warmup_ms_excluded"],
        "errors": run["counts"]["errors"],
        "arms": {arm: arm_stats(rows[arm], labels["zh" if arm.startswith("zh") else "meld"])
                 for arm in sorted(rows)},
        "meld_context_vs_no_context": paired_meld(rows["meld_no_context"], rows["meld_context"]),
    }

    out = os.path.join(HERE, "runs", f"{run['run_date']}-scores.json")
    if "--check" in sys.argv:
        stored = json.load(open(out, encoding="utf-8"))
        if stored != scores:
            print("MISMATCH: recomputed scores differ from", out)
            sys.exit(1)
        print("ok: recomputed scores match", os.path.basename(out))
        return

    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for arm, s in scores["arms"].items():
        print(f"\n{arm}: {s['items']} items / {s['calls']} calls")
        print(f"  accuracy {s['accuracy']}  (chance {s['majority_baseline']})   "
              f"ECE {s['ece']}   Brier {s['brier']}   mean conf {s['mean_confidence']}")
        print(f"  同一題三次都一樣 / same answer all 3 repeats: {s['same_answer_all_repeats']}")
        print(f"  latency p50 {s['latency_ms']['p50']} ms  p95 {s['latency_ms']['p95']} ms  "
              f"max {s['latency_ms']['max']} ms")
        print("  per class: " + ", ".join(
            f"{k} {v['recall']}" + (f"->{v.get('most_confused_with')}" if v.get('most_confused_with') else "")
            for k, v in s["per_class"].items()))
        print("  threshold sweep (coverage / acc on covered / acc after neutral fallback):")
        for t, v in s["threshold_sweep"].items():
            print(f"    {t}: {v['coverage']} / {v['accuracy_on_covered']} / "
                  f"{v['accuracy_after_neutral_fallback']}")
    p = scores["meld_context_vs_no_context"]
    print(f"\nMELD 脈絡 vs 無脈絡 / context vs no context ({p['items']} items): "
          f"diff {p['accuracy_diff']:+} 95% CI {p['ci95']}, "
          f"context won {p['context_won']} / lost {p['context_lost']}")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
