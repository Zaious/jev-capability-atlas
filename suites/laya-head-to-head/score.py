#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Score runs/<date>-jev.json and runs/<date>-laya.json against the pinned datasets.
Writes runs/<date>-scores.json and prints the tables used in README.md.

  python score.py [--date YYYY-MM-DD]
"""
import sys, os, json, glob, argparse, statistics
from collections import Counter, defaultdict

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

GENERALIST = ["jev", "laya", "laya-multilingual"]   # zero-shot: never trained on these workflows
SPECIALIST = ["laya-typed-decisions"]                # fine-tuned on typed-decisions' train split
BOOT, SEED = 2000, 7


def latest(pattern):
    fs = sorted(glob.glob(os.path.join(HERE, "runs", pattern)))
    return fs[-1] if fs else None


def train_majority():
    """Per (workflow, question) majority label on the TRAIN split: the input-blind baseline."""
    import pandas as pd
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(common.TD_REPO, "all/train-00000-of-00001.parquet", repo_type="dataset",
                        revision=common.TD_REV)
    cnt = defaultdict(Counter)
    for _, r in pd.read_parquet(p).iterrows():
        for qid, gg in json.loads(r["gold"]).items():
            cnt[(r["workflow"], qid)][str(gg["label"]).lower()] += 1
    return {k: v.most_common(1)[0][0] for k, v in cnt.items()}


def boot_diff(a, b, clusters, rng):
    """Paired bootstrap over clusters (cases) of mean(a) - mean(b); a/b are per-item 0/1 arrays."""
    a, b, clusters = np.asarray(a, float), np.asarray(b, float), np.asarray(clusters)
    ids = np.unique(clusters)
    idx = {c: np.where(clusters == c)[0] for c in ids}
    diffs = []
    for _ in range(BOOT):
        pick = np.concatenate([idx[c] for c in rng.choice(ids, size=len(ids), replace=True)])
        diffs.append(a[pick].mean() - b[pick].mean())
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return round(float(a.mean() - b.mean()), 4), [round(float(lo), 4), round(float(hi), 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    a = ap.parse_args()
    jf = os.path.join(HERE, "runs", f"{a.date}-jev.json") if a.date else latest("????-??-??-jev.json")
    lf = os.path.join(HERE, "runs", f"{a.date}-laya.json") if a.date else latest("????-??-??-laya.json")
    jev, lay = json.load(open(jf, encoding="utf-8")), json.load(open(lf, encoding="utf-8"))
    preds = {"jev": {"typed_decisions": jev["typed_decisions"], "massive": jev["massive"]}}
    preds.update(lay["results"])
    rng = np.random.default_rng(SEED)
    out = {"inputs": {"jev": os.path.basename(jf), "laya": os.path.basename(lf)},
           "jev_models": jev["meta"]["response_models"], "laya_version": lay["meta"]["laya_version"]}

    # ------------------------------------------------ Part A: typed-decisions
    td = common.load_typed_decisions()
    maj = train_majority()
    A, correct_items = {}, {}
    for m in GENERALIST + SPECIALIST:
        P = preds[m]["typed_decisions"]
        rows, soft_pairs, mae, w1, lat, drop = [], [], [], [], [], 0
        by_wf, by_qt, items = defaultdict(list), defaultdict(list), []
        for cid, wf, st, qs, gm in td:
            r = P.get(cid, {})
            if "ms" in r:
                lat.append(r["ms"])
            for qid, g in gm.items():
                p = (r.get("probs") or {}).get(qid)
                rows.append((g["idx"], p))
                ok = p is not None and int(np.argmax(p)) == g["idx"]
                items.append((cid, float(ok)))
                if p is None:
                    drop += 1
                    continue
                by_wf[wf].append((g["idx"], p))
                by_qt[g["type"]].append((g["idx"], p))
                soft_pairs.append((p, g["soft"]))
                if g["type"] == "score":
                    exp = float((np.arange(len(p)) * np.asarray(p)).sum())
                    mae.append(abs(exp - g["gold_score"]))
                    w1.append(float(abs(exp - g["gold_score"]) <= 1))
        res = common.metrics(rows)
        res.update(common.soft_metrics(soft_pairs))
        res.update(score_mae=round(float(np.mean(mae)), 4) if mae else None,
                   within_1_level=round(float(np.mean(w1)), 4) if w1 else None,
                   median_ms_per_case=round(statistics.median(lat), 1) if lat else None,
                   mode="specialist (fine-tuned on this benchmark's train split)" if m in SPECIALIST
                   else "generalist (zero-shot)",
                   by_workflow={k: common.metrics(v) for k, v in sorted(by_wf.items())},
                   by_question_type={k: common.metrics(v) for k, v in sorted(by_qt.items())})
        A[m] = res
        correct_items[m] = items
    # input-blind baseline
    base = []
    for cid, wf, st, qs, gm in td:
        for qid, g in gm.items():
            lab = maj[(wf, qid)]
            if g["type"] == "choice":
                pred = g["keys"].index(lab) if lab in g["keys"] else -1
            elif g["type"] == "noul":
                pred = 1 if lab == "true" else 0
            else:
                pred = int(lab)
            base.append(float(pred == g["idx"]))
    A["_baseline_train_majority"] = {"accuracy": round(float(np.mean(base)), 4),
                                     "note": "per (workflow, question) majority label from the train split; ignores the input"}
    cl = [c for c, _ in correct_items["jev"]]
    A["_jev_minus"] = {m: dict(zip(("diff", "ci95"), boot_diff([x for _, x in correct_items["jev"]],
                                                               [x for _, x in correct_items[m]], cl, rng)))
                       for m in GENERALIST[1:] + SPECIALIST}
    A["_reference_published"] = {
        "laya_repo_table": {"jev_1.13.0": 0.727, "laya": 0.362, "laya-multilingual": 0.342,
                            "laya-typed-decisions": 0.766,
                            "jev_source": "quoted in Laya's repo; Laya states it did not measure Jev"},
        "dataset_card": {"majority_baseline": 0.520, "teacher_self_agreement": 0.735,
                         "note": "measured on the 1600-case set, not the 400-case test split"}}
    out["typed_decisions"] = A

    # ------------------------------------------------ Part B: MASSIVE intent
    B = {}
    for lg in common.MS_LANGS:
        items = common.load_massive(lg)
        B[lg] = {}
        per_item = {}
        for m in ["jev", "laya", "laya-multilingual"]:
            P = preds[m]["massive"]
            rows, lat, flags = [], [], []
            for cid, st, qs, gi, keys in items:
                r = P.get(cid, {})
                p = (r.get("probs") or {}).get("intent")
                rows.append((gi, p))
                flags.append(float(p is not None and int(np.argmax(p)) == gi))
                if "ms" in r:
                    lat.append(r["ms"])
            res = common.metrics(rows)
            res["median_ms"] = round(statistics.median(lat), 1) if lat else None
            B[lg][m] = res
            per_item[m] = flags
        ids = list(range(len(items)))
        B[lg]["_jev_minus"] = {m: dict(zip(("diff", "ci95"), boot_diff(per_item["jev"], per_item[m], ids, rng)))
                               for m in ["laya", "laya-multilingual"]}
    B["_reference_published"] = {"laya": {"zh-TW": 0.46, "zh-CN": 0.62, "en": 0.82},
                                 "laya-multilingual": {"zh-TW": 0.54, "zh-CN": 0.63, "en": 0.68},
                                 "source": "Laya repo research/results/cpu_51_language_sweep.json (laya 0.2.0)"}
    out["massive"] = B

    date = os.path.basename(jf)[:10]
    op = os.path.join(HERE, "runs", f"{date}-scores.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ------------------------------------------------ print
    print("\n## Part A: typed-decisions test split (400 cases / 2,000 decisions)\n")
    print("| model | mode | acc | soft acc | Brier vs soft | ECE | score MAE | dropped | median ms/case |")
    print("|---|---|---|---|---|---|---|---|---|")
    for m in GENERALIST + SPECIALIST:
        r = A[m]
        print(f"| {m} | {'specialist' if m in SPECIALIST else 'zero-shot'} | {r['accuracy']} | {r['soft_accuracy']} | "
              f"{r['brier_vs_soft']} | {r['ece']} | {r['score_mae']} | {r['dropped']} | {r['median_ms_per_case']} |")
    print(f"\ninput-blind train-majority baseline: {A['_baseline_train_majority']['accuracy']}")
    for m, v in A["_jev_minus"].items():
        print(f"jev - {m}: {v['diff']:+.4f}  95% CI {v['ci95']}")
    print("\nby workflow (accuracy):")
    wfs = sorted(A["jev"]["by_workflow"])
    print("| model | " + " | ".join(wfs) + " |")
    for m in GENERALIST + SPECIALIST:
        print(f"| {m} | " + " | ".join(str(A[m]["by_workflow"][w]["accuracy"]) for w in wfs) + " |")
    print("\nby question type (accuracy / ECE):")
    for m in GENERALIST + SPECIALIST:
        print(f"  {m}: " + ", ".join(f"{k} {v['accuracy']}/{v['ece']}" for k, v in A[m]["by_question_type"].items()))
    print("\n## Part B: MASSIVE intent, 20-option choice, 100 per language\n")
    print("| lang | model | acc | ECE | mean conf | median ms |")
    print("|---|---|---|---|---|---|")
    for lg in common.MS_LANGS:
        for m in ["jev", "laya", "laya-multilingual"]:
            r = B[lg][m]
            print(f"| {lg} | {m} | {r['accuracy']} | {r['ece']} | {r['mean_confidence']} | {r['median_ms']} |")
    for lg in common.MS_LANGS:
        for m, v in B[lg]["_jev_minus"].items():
            print(f"{lg}: jev - {m}: {v['diff']:+.4f}  95% CI {v['ci95']}")
    print(f"\nsaved: {op}")


if __name__ == "__main__":
    main()
