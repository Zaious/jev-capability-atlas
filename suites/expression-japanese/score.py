#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。README 引用的數字都出自這裡。
  python score.py           # 算並寫出 runs/<日期>-scores.json
  python score.py --check   # 重算並跟已存檔的比，不一致就 exit 1
"""
import collections
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BINS = 15
THRESHOLDS = [0.3, 0.5, 0.7]


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


def score(calls, question, gold_key, labels):
    """一個問題對一個標準答案。question 是 expressed / felt，gold_key 是 reader_gold / writer_gold。"""
    rows = [(r[question]["choice"], r[question]["confidence"], r[gold_key], r) for r in calls]
    pairs = [(conf, ch == g) for ch, conf, g, _ in rows]
    by_item = collections.defaultdict(list)
    for ch, _, _, r in rows:
        by_item[r["id"]].append(ch)
    majority = collections.Counter(g for _, _, g, _ in rows).most_common(1)[0]
    per_class = {}
    for gold in sorted({g for _, _, g, _ in rows}):
        sub = [x for x in rows if x[2] == gold]
        hit = sum(1 for ch, _, g, _ in sub if ch == g)
        wrong = collections.Counter(ch for ch, _, g, _ in sub if ch != g)
        per_class[gold] = {"n": len(sub), "recall": round(hit / len(sub), 3)}
        if wrong:
            per_class[gold]["most_confused_with"] = wrong.most_common(1)[0][0]
    sweep = {}
    for t in THRESHOLDS:
        cov = [x for x in rows if x[1] >= t]
        sweep[str(t)] = {
            "coverage": round(len(cov) / len(rows), 3),
            "accuracy_on_covered": round(
                sum(1 for ch, _, g, _ in cov if ch == g) / len(cov), 3) if cov else None}
    return {
        "items": len(by_item), "calls": len(rows),
        "accuracy": round(statistics.fmean(1.0 if ok else 0.0 for _, ok in pairs), 4),
        "majority_class_baseline": round(majority[1] / len(rows), 4),
        "majority_class_label": majority[0],
        "chance": round(1.0 / len(labels), 4),
        "ece": ece(pairs),
        "mean_confidence": round(statistics.fmean(c for c, _ in pairs), 4),
        "same_answer_all_repeats": round(
            sum(1 for v in by_item.values() if len(set(v)) == 1) / len(by_item), 3),
        "per_class": per_class,
        "threshold_sweep": sweep,
    }


def main():
    run = json.load(open(latest_run(), encoding="utf-8"))
    calls = [r for r in run["results"] if "error" not in r]
    labels = run["labels"]
    b = run["baselines"]

    # 「Jev 當成第四個標註者」：它跟三個人裡任意一個的同意率，對照人跟人之間的同意率
    as_annotator = tot = 0
    for r in calls:
        for x in r["readers"]:
            tot += 1
            as_annotator += r["expressed"]["choice"] == x

    scores = {
        "run_file": os.path.basename(latest_run()), "run_date": run["run_date"],
        "model_answered": run["model_answered"], "errors": run["counts"]["errors"],
        "warmup_ms_excluded": run["warmup_ms_excluded"],
        "baselines": b,
        "expressed_vs_reader_consensus": score(calls, "expressed", "reader_gold", labels),
        "felt_vs_writer_selfreport": score(calls, "felt", "writer_gold", labels),
        "expressed_vs_writer_selfreport": score(calls, "expressed", "writer_gold", labels),
        "felt_vs_reader_consensus": score(calls, "felt", "reader_gold", labels),
        "expressed_equals_felt": round(
            sum(1 for r in calls if r["expressed"]["choice"] == r["felt"]["choice"]) / len(calls), 4),
        "as_a_fourth_annotator": {
            "agreement_with_any_single_reader": round(as_annotator / tot, 4),
            "human_pairwise_reference": b["human_ceiling_reader"]},
        "latency_ms": {"p50": pct([r["latency_ms"] for r in calls], .50),
                       "p95": pct([r["latency_ms"] for r in calls], .95)},
    }

    out = os.path.join(HERE, "runs", f"{run['run_date']}-scores.json")
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            print("MISMATCH: recomputed scores differ from", out)
            sys.exit(1)
        print("ok: recomputed scores match", os.path.basename(out))
        return

    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baselines:", json.dumps(b, ensure_ascii=False, indent=1))
    for k in ("expressed_vs_reader_consensus", "felt_vs_writer_selfreport",
              "expressed_vs_writer_selfreport", "felt_vs_reader_consensus"):
        s = scores[k]
        print(f"\n{k}: {s['items']} items / {s['calls']} calls")
        print(f"  accuracy {s['accuracy']}   always-{s['majority_class_label']} "
              f"{s['majority_class_baseline']}   chance {s['chance']}")
        print(f"  ECE {s['ece']}   mean conf {s['mean_confidence']}   "
              f"same answer x3 {s['same_answer_all_repeats']}")
        print("  per class: " + ", ".join(
            f"{g} {v['recall']}" + (f"->{v.get('most_confused_with')}" if v.get("most_confused_with") else "")
            for g, v in s["per_class"].items()))
        print("  thresholds: " + ", ".join(
            f"{t}: cov {v['coverage']} acc {v['accuracy_on_covered']}"
            for t, v in s["threshold_sweep"].items()))
    print(f"\nexpressed == felt on the same call: {scores['expressed_equals_felt']}")
    print(f"as a fourth annotator: agrees with a single reader "
          f"{scores['as_a_fourth_annotator']['agreement_with_any_single_reader']} "
          f"(human pairwise reference {scores['as_a_fourth_annotator']['human_pairwise_reference']})")
    print(f"latency p50 {scores['latency_ms']['p50']} / p95 {scores['latency_ms']['p95']} ms")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
