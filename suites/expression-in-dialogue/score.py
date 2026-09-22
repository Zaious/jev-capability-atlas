#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。README 引用的數字都出自這裡。
Recompute from the receipts. Everything quoted in README comes from here.

runs/ 底下所有非 -scores 的檔案都會被讀進來合併（同一天可以分批跑不同的臂）。
Every non "-scores" file under runs/ is merged, so arms can be run in separate batches.

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
sys.path.insert(0, os.path.join(HERE, "data"))
import build_cases  # noqa: E402

BINS = 15
BOOTSTRAP = 2000
BOOT_SEED = 31


def run_files():
    return sorted(os.path.join(HERE, "runs", f) for f in os.listdir(os.path.join(HERE, "runs"))
                  if f.endswith(".json") and not f.endswith("-scores.json"))


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
    per_repeat = []
    tot = 0
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


def arm_stats(rows, labels, sample_gold_switch=None):
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
        prior = [r for r in calls if r.get("listener_prior_gold")]
        if prior:
            out["persistence_baseline_on_sample"] = round(
                sum(1 for r in prior if r["listener_prior_gold"] == r["gold"]) / len(prior), 4)
            out["matched_listener_prior_emotion"] = round(
                sum(1 for r in prior if r["choice"] == r["listener_prior_gold"]) / len(prior), 4)
    else:
        rate, n = switch_rate(calls)
        out["switch_rate"] = rate
        out["switch_opportunities_per_repeat"] = n
        out["gold_switch_rate_on_sample"] = sample_gold_switch
    return out


def paired(rows_a, rows_b, keep=None):
    key = lambda r: (r["id"], r["repeat"])  # noqa: E731
    ok = keep or (lambda r: True)
    a = {key(r): r["choice"] == r["gold"] for r in rows_a if "error" not in r and ok(r)}
    b = {key(r): r["choice"] == r["gold"] for r in rows_b if "error" not in r and ok(r)}
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
    files = run_files()
    runs = [json.load(open(f, encoding="utf-8")) for f in files]
    rows = collections.defaultdict(list)
    for run in runs:
        for r in run["results"]:
            rows[r["arm"]].append(r)
    base_run = runs[0]

    # 這 30 段對話自己的標準答案換臉率
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
    baselines = dict(base_run["corpus_baselines"])
    baselines["sample_gold_switch_rate"] = round(sw / tot, 4)
    baselines["sample_switch_opportunities"] = tot

    # 有「聽者狀態」可給的那些題（追蹤臂只跑得了這些）
    eligible = {c["id"] for c in build_cases.build()["listening"] if c["listener_state"]}
    in_elig = lambda r: r["id"] in eligible  # noqa: E731

    labels_for = lambda arm: base_run["labels"]["listening" if arm.startswith("listening") else "self"]  # noqa: E731
    arms = {arm: arm_stats(rows[arm], labels_for(arm), baselines["sample_gold_switch_rate"])
            for arm in sorted(rows)}
    # 追蹤臂只涵蓋合格子集，所以把沒有追蹤的那兩臂也限制到同一批題目，才比得起來
    for arm in ("listening_no_context", "listening_context"):
        subset = [r for r in rows[arm] if in_elig(r)]
        arms[arm]["on_eligible_subset"] = arm_stats(subset, labels_for(arm))

    scores = {
        "run_files": [os.path.basename(f) for f in files],
        "run_date": base_run["run_date"],
        "model_answered": base_run["model_answered"],
        "errors": sum(r["counts"]["errors"] for r in runs),
        "eligible_listening_items": len(eligible),
        "baselines": baselines,
        "arms": arms,
        "context_effect": {
            "self": paired(rows["self_no_context"], rows["self_context"],
                           keep=lambda r: r["index"] >= 1),
            "listening": paired(rows["listening_no_context"], rows["listening_context"],
                                keep=lambda r: r["index"] >= 1),
        },
        "listener_state_effect": {
            "tracked_vs_context": paired(rows["listening_context"], rows["listening_tracked"]),
            "tracked_vs_tracked_nolabel": paired(rows["listening_tracked_nolabel"],
                                                 rows["listening_tracked"]),
            "nolabel_vs_context": paired(rows["listening_context"],
                                         rows["listening_tracked_nolabel"]),
        },
    }

    out = os.path.join(HERE, "runs", f"{base_run['run_date']}-scores.json")
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            print("MISMATCH: recomputed scores differ from", out)
            sys.exit(1)
        print("ok: recomputed scores match", os.path.basename(out))
        return

    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baselines:", json.dumps(baselines, ensure_ascii=False))
    print("eligible listening items:", len(eligible))
    for arm, s in scores["arms"].items():
        print(f"\n{arm}: {s['items']} items / {s['calls']} calls")
        print(f"  accuracy {s['accuracy']}   always-{s['majority_class_label']} "
              f"{s['majority_class_baseline']}   ECE {s['ece']}   mean conf {s['mean_confidence']}")
        if "matched_speaker_emotion" in s:
            print(f"  answered = speaker's emotion {s['matched_speaker_emotion']}"
                  + (f"   = listener's own prior emotion {s['matched_listener_prior_emotion']}"
                     if "matched_listener_prior_emotion" in s else ""))
        if "switch_rate" in s:
            print(f"  switch rate {s['switch_rate']} vs gold {s['gold_switch_rate_on_sample']}")
        if "on_eligible_subset" in s:
            e = s["on_eligible_subset"]
            print(f"  on the eligible subset: accuracy {e['accuracy']} "
                  f"(always-{e['majority_class_label']} {e['majority_class_baseline']}), ECE {e['ece']}")
    for group in ("context_effect", "listener_state_effect"):
        for k, v in scores[group].items():
            if v:
                print(f"\n{group}/{k} ({v['items']} items): {v['accuracy_diff']:+} "
                      f"95% CI {v['ci95']}, won {v['b_won']} / lost {v['b_lost']}")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
