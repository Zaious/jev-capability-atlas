#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從 runs/*.json 重新算出 README 表格裡的四個數字，並檢查有沒有對上。

Re-derive the four headline metrics in README.md from a committed run file, and
check they still match. The README's numbers were worked out by hand; this makes
that arithmetic executable, so a future re-run cannot drift away from the prose
without something failing.

    python metrics.py                     # 用預設 run，印出表格 / default run, print the table
    python metrics.py runs/2026-09-19.json
    python metrics.py --check             # 另外比對 README 公布的數字，不符就 exit 1
                                          # also assert the published figures; exit 1 on mismatch

不打任何 API：只讀已經committed 的 receipts。
Makes no API calls: it only reads receipts that are already committed.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUN = os.path.join(HERE, "runs", "2026-09-19.json")

# README.md 的 Results 表格（2026-09-19 那次 run）。改了 run 就要一起改這裡。
# The Results table in README.md for the 2026-09-19 run. Change one, change both.
PUBLISHED = {
    "run": "runs/2026-09-19.json",
    "accuracy": (19, 30),
    "sensitivity": (5, 15),
    "specificity": (14, 15),
    "official_score": 0.271,
}

# 官方計分法：抑制掉一個真警報要罰 5 倍。
# The challenge's official score: a suppressed true alarm costs 5x.
# score = (TP + TN) / (TP + TN + FP + 5*FN)
OFFICIAL_FN_PENALTY = 5


def confusion(rows):
    tp = sum(1 for r in rows if r["true_alarm"] == 1 and r["predicted"] == 1)
    tn = sum(1 for r in rows if r["true_alarm"] == 0 and r["predicted"] == 0)
    fp = sum(1 for r in rows if r["true_alarm"] == 0 and r["predicted"] == 1)
    fn = sum(1 for r in rows if r["true_alarm"] == 1 and r["predicted"] == 0)
    return tp, tn, fp, fn


def official_score(tp, tn, fp, fn):
    denominator = tp + tn + fp + OFFICIAL_FN_PENALTY * fn
    return (tp + tn) / denominator if denominator else float("nan")


def by_alarm_type(rows):
    types = {}
    for r in rows:
        if r["true_alarm"] != 1:
            continue
        caught, total = types.get(r["alarm_type"], (0, 0))
        types[r["alarm_type"]] = (caught + (r["predicted"] == 1), total + 1)
    return dict(sorted(types.items()))


def main():
    args = [a for a in sys.argv[1:] if a != "--check"]
    check = "--check" in sys.argv
    run_path = args[0] if args else DEFAULT_RUN
    run = json.load(open(run_path, encoding="utf-8"))
    rows = run["results"]

    tp, tn, fp, fn = confusion(rows)
    n = len(rows)
    positives = tp + fn
    negatives = tn + fp
    accuracy = (tp + tn, n)
    sensitivity = (tp, positives)
    specificity = (tn, negatives)
    score = official_score(tp, tn, fp, fn)

    print(f"run: {os.path.relpath(run_path, HERE)}  model: {run.get('model', '?')}  n={n}")
    print(f"confusion: TP={tp} TN={tn} FP={fp} FN={fn}")
    print()
    print(f"{'Accuracy':<44} {accuracy[0]}/{accuracy[1]} = {accuracy[0]/accuracy[1]:.1%}")
    print(f"{'Sensitivity (true alarms caught)':<44} {sensitivity[0]}/{sensitivity[1]} = {sensitivity[0]/sensitivity[1]:.1%}")
    print(f"{'Specificity (false alarms identified as false)':<44} {specificity[0]}/{specificity[1]} = {specificity[0]/specificity[1]:.1%}")
    print(f"{'Official score (FN penalised 5x)':<44} {score:.3f}")
    print()
    print("sensitivity by alarm type:")
    for alarm_type, (caught, total) in by_alarm_type(rows).items():
        print(f"  {alarm_type:<28} {caught}/{total} = {caught/total:.0%}")

    if not check:
        return 0

    if os.path.relpath(run_path, HERE).replace(os.sep, "/") != PUBLISHED["run"]:
        print(f"\n--check compares against README's figures for {PUBLISHED['run']}; "
              f"skipping for this run file.")
        return 0

    failures = []
    for name, got, want in (
        ("accuracy", accuracy, PUBLISHED["accuracy"]),
        ("sensitivity", sensitivity, PUBLISHED["sensitivity"]),
        ("specificity", specificity, PUBLISHED["specificity"]),
    ):
        if got != want:
            failures.append(f"{name}: receipts say {got[0]}/{got[1]}, README says {want[0]}/{want[1]}")
    if round(score, 3) != PUBLISHED["official_score"]:
        failures.append(f"official score: receipts say {score:.3f}, README says {PUBLISHED['official_score']}")

    print()
    if failures:
        for line in failures:
            print(f"✗ {line}")
        return 1
    print("✓ all four published figures reproduce from the receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
