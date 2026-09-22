#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。README 引用的數字都出自這裡。
Recompute from the receipts. Everything quoted in README comes from here.

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
BOOTSTRAP = 2000
BOOT_SEED = 31


def latest_run():
    runs = sorted(f for f in os.listdir(os.path.join(HERE, "runs"))
                  if f.endswith(".json") and not f.endswith("-scores.json"))
    return os.path.join(HERE, "runs", runs[-1])


def ece(pairs):
    buckets = [[] for _ in range(BINS)]
    for conf, ok in pairs:
        buckets[min(BINS - 1, int(conf * BINS))].append((conf, ok))
    return round(sum(len(b) / len(pairs) * abs(statistics.fmean(c for c, _ in b)
                                               - statistics.fmean(1.0 if o else 0.0 for _, o in b))
                     for b in buckets if b), 4)


def pct(values, q):
    v = sorted(values)
    return round(v[min(len(v) - 1, int(round(q * (len(v) - 1))))], 1)


def switch_rate(rows):
    """同一段對話、同一個角色，連續兩句之間表情換掉的比例（每次重複各算一遍再平均）。"""
    per_repeat = []
    for rep in sorted({r["repeat"] for r in rows}):
        seqs = collections.defaultdict(list)
        for r in sorted((x for x in rows if x["repeat"] == rep), key=lambda x: x["index"]):
            seqs[(r["dialogue"], r["speaker"])].append(r["choice"])
        switch = tot = 0
        for seq in seqs.values():
            for x, y in zip(seq, seq[1:]):
                tot += 1
                switch += x != y
        if tot:
            per_repeat.append(switch / tot)
    return round(statistics.fmean(per_repeat), 4), tot


def arm_stats(rows, labels, baselines):
    calls = [r for r in rows if "error" not in r]
    arm = calls[0]["arm"]
    pairs = [(r["confidence"], r["choice"] == r["gold"]) for r in calls]
    by_item = collections.defaultdict(list)
    for r in calls:
        by_item[r["id"]].append(r)

    majority = collections.Counter(r["gold"] for r in calls).most_common(1)[0]
    out = {
        "items": len(by_item), "calls": len(calls),
        "accuracy": round(statistics.fmean(1.0 if ok else 0.0 for _, ok in pairs), 4),
        "majority_class_baseline": round(majority[1] / len(calls), 4),
        "majority_class_label": majority[0],
        "chance": round(1.0 / len(labels), 4),
        "ece": ece(pairs),
        "mean_confidence": round(statistics.fmean(c for c, _ in pairs), 4),
        "same_answer_all_repeats": round(
            sum(1 for rs in by_item.values() if len({r["choice"] for r in rs}) == 1) / len(by_item), 3),
        "predicted_neutral_share": round(
            sum(1 for r in calls if r["choice"] == "neutral") / len(calls), 4),
        "gold_neutral_share": round(sum(1 for r in calls if r["gold"] == "neutral") / len(calls), 4),
        "latency_ms": {"p50": pct([r["latency_ms"] for r in calls], .50),
                       "p95": pct([r["latency_ms"] for r in calls], .95)},
    }
    if arm.startswith("listening"):
        out["mirror_baseline_on_sample"] = round(
            sum(1 for r in calls if r["speaker_gold"] == r["gold"]) / len(calls), 4)
        out["matched_speaker_emotion"] = round(
            sum(1 for r in calls if r["choice"] == r["speaker_gold"]) / len(calls), 4)
    else:
        rate, n = switch_rate(calls)
        out["switch_rate"] = rate
        out["switch_opportunities_per_repeat"] = n
        out["gold_switch_rate_on_sample"] = baselines["sample_gold_switch_rate"]
    return out


def paired(rows_a, rows_b, only_with_context=True):
    """同題同重複配對；預設只算真的有前文的題目（第一句兩臂看到的資訊一樣）。"""
    keep = lambda r: (not only_with_context) or r["index"] >= 1  # noqa: E731
    a = {(r["id"], r["repeat"]): r["choice"] == r["gold"]
         for r in rows_a if "error" not in r and keep(r)}
    b = {(r["id"], r["repeat"]): r["choice"] == r["gold"]
         for r in rows_b if "error" not in r and keep(r)}
    shared = sorted(set(a) & set(b))
    if not shared:
        return None
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
    rows = collections.defaultdict(list)
    for r in run["results"]:
        rows[r["arm"]].append(r)

    # 抽到的這 30 段對話自己的標準答案換臉率（不是整個語料的）
    gold_seqs = collections.defaultdict(list)
    for r in rows["self_no_context"]:
        if r["repeat"] == 0:
            gold_seqs[(r["dialogue"], r["speaker"])].append((r["index"], r["gold"]))
    sw = tot = 0
    for seq in gold_seqs.values():
        labels = [g for _, g in sorted(seq)]
        for x, y in zip(labels, labels[1:]):
            tot += 1
            sw += x != y
    baselines = dict(run["corpus_baselines"])
    baselines["sample_gold_switch_rate"] = round(sw / tot, 4)
    baselines["sample_switch_opportunities"] = tot

    scores = {
        "run_file": os.path.basename(latest_run()), "run_date": run["run_date"],
        "model_answered": run["model_answered"], "errors": run["counts"]["errors"],
        "warmup_ms_excluded": run["warmup_ms_excluded"],
        "baselines": baselines,
        "arms": {arm: arm_stats(rows[arm], run["labels"]["listening" if arm.startswith("listening") else "self"],
                                baselines) for arm in sorted(rows)},
        "context_effect": {
            "self": paired(rows["self_no_context"], rows["self_context"]),
            "listening": paired(rows["listening_no_context"], rows["listening_context"]),
        },
    }

    out = os.path.join(HERE, "runs", f"{run['run_date']}-scores.json")
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            print("MISMATCH: recomputed scores differ from", out)
            sys.exit(1)
        print("ok: recomputed scores match", os.path.basename(out))
        return

    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baselines:", json.dumps(baselines, ensure_ascii=False))
    for arm, s in scores["arms"].items():
        print(f"\n{arm}: {s['items']} items / {s['calls']} calls")
        print(f"  accuracy {s['accuracy']}   always-{s['majority_class_label']} baseline "
              f"{s['majority_class_baseline']}   chance {s['chance']}")
        print(f"  ECE {s['ece']}   mean conf {s['mean_confidence']}   "
              f"same answer x3 {s['same_answer_all_repeats']}")
        print(f"  predicted neutral {s['predicted_neutral_share']} vs gold neutral {s['gold_neutral_share']}")
        if "switch_rate" in s:
            print(f"  switch rate {s['switch_rate']} vs gold {s['gold_switch_rate_on_sample']}")
        if "mirror_baseline_on_sample" in s:
            print(f"  mirror baseline {s['mirror_baseline_on_sample']}   "
                  f"answered same as speaker's own emotion {s['matched_speaker_emotion']}")
        print(f"  latency p50 {s['latency_ms']['p50']} / p95 {s['latency_ms']['p95']} ms")
    for k, v in scores["context_effect"].items():
        if v:
            print(f"\n{k}: context vs no context ({v['items']} items with >=1 prior turn): "
                  f"{v['accuracy_diff']:+} 95% CI {v['ci95']}, won {v['b_won']} / lost {v['b_lost']}")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
