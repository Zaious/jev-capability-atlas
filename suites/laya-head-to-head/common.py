#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared by run_jev.py / run_laya.py / score.py.

Case construction and metric definitions deliberately mirror Laya's own benchmark
script (github.com/NandhaKishorM/laya, research/scripts/bench_local.py @ 42626c3,
Apache-2.0), so Jev and Laya are scored on exactly the inputs and yardstick Laya
itself used. Datasets are pinned to exact Hub revisions (see protocol.yaml).
"""
import gzip
import json
import math
import random

import numpy as np

TD_REPO, TD_REV = "LocalLLaMA/typed-decisions", "ea9306458d6e9563628369a3d1e72e362fb381d2"
MS_REPO, MS_REV = "mteb/amazon_massive_intent", "940fd47a81eaa7f2cc7b129674d945d618ac38c2"
MS_LANGS = ["zh-TW", "zh-CN", "en"]
MS_PER_LANG, MS_SEED, MS_N_OPTS = 100, 13, 20   # = Laya's published cpu_51_language_sweep.json config


# ---------------------------------------------------------------- typed-decisions
def load_typed_decisions():
    """Test split, 400 cases x 5 questions. Returns [(id, workflow, state, questions, gold)]."""
    import pandas as pd
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(TD_REPO, "all/test-00000-of-00001.parquet", repo_type="dataset", revision=TD_REV)
    out = []
    for _, r in pd.read_parquet(p).iterrows():
        qs, g = json.loads(r["questions"]), json.loads(r["gold"])
        st = r["state"]
        try:
            st = json.loads(st)
        except Exception:
            pass
        gm = {}
        for qid, qd in qs.items():
            gg = g[qid]
            if qd["type"] == "choice":
                keys = list(qd["criteria"].keys())
                gm[qid] = {"type": "choice", "keys": keys, "idx": keys.index(str(gg["label"])),
                           "soft": [float(gg.get("probabilities", {}).get(k, 0.0)) for k in keys]}
            elif qd["type"] == "noul":
                pt = float(gg.get("probabilities", {}).get("true", gg.get("noul", 0.5)))
                gm[qid] = {"type": "noul", "idx": 1 if str(gg["label"]).lower() == "true" else 0,
                           "soft": [1 - pt, pt]}
            else:
                n = len(qd["criteria"])
                gm[qid] = {"type": "score", "idx": int(gg["label"]),
                           "soft": [float(gg.get("probabilities", {}).get(str(i), 0.0)) for i in range(n)],
                           "gold_score": float(gg.get("score", float(gg["label"])))}
        out.append((r["id"], r["workflow"], st, qs, gm))
    return out


# ---------------------------------------------------------------- MASSIVE intent
def load_massive(lang):
    """First MS_PER_LANG test utterances; 20-option choice built exactly as Laya's build_massive().
    Returns [(case_id, state, questions, gold_idx, keys)]."""
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(MS_REPO, f"test/{lang}.json.gz", repo_type="dataset", revision=MS_REV)
    rows = [json.loads(l) for l in gzip.open(p, "rt", encoding="utf-8") if l.strip()]
    labels = sorted(set(r["label_text"] for r in rows))
    rng = random.Random(MS_SEED)
    out = []
    for r in rows[:MS_PER_LANG]:
        pool = [x for x in labels if x != r["label_text"]]
        keys = [r["label_text"]] + rng.sample(pool, min(MS_N_OPTS - 1, len(pool)))
        rng.shuffle(keys)
        q = {"intent": {"type": "choice",
                        "instructions": "What is the user asking for in `utterance`?",
                        "criteria": {k: k.replace("_", " ").replace(".", ": ") for k in keys}}}
        out.append((f"{lang}:{r['id']}", {"utterance": r["text"]}, q, keys.index(r["label_text"]), keys))
    return out


# ---------------------------------------------------------------- answers -> probability vectors
def to_vector(qtype, answer_probs, keys=None, n=None):
    """Normalise one answer to an ordered probability list.
    choice: dict option->p, ordered by `keys`; noul: p(true) float -> [p_false, p_true];
    score: dict level->p (int or str keys), ordered 0..n-1."""
    if qtype == "choice":
        v = [float(answer_probs.get(k, 0.0)) for k in keys]
    elif qtype == "noul":
        v = [1.0 - float(answer_probs), float(answer_probs)]
    else:
        v = [float(answer_probs.get(i, answer_probs.get(str(i), 0.0))) for i in range(n)]
    s = sum(v)
    return [round(x / s, 4) for x in v] if s > 0 else v


# ---------------------------------------------------------------- metrics (= bench_local.py)
def ece_score(conf, corr, bins=15):
    conf, corr = np.asarray(conf, float), np.asarray(corr, float)
    if not len(conf):
        return float("nan")
    e, edges = 0.0, np.linspace(0, 1, bins + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = (conf > lo) & (conf <= hi)
        if s.any():
            e += s.mean() * abs(conf[s].mean() - corr[s].mean())
    return float(e)


def metrics(rows):
    """rows: [(gold_idx, probs or None)]. None = the model could not answer (dropped).
    `accuracy` excludes dropped rows, as Laya's script does; `accuracy_counting_dropped` doesn't."""
    total = len(rows)
    rows = [r for r in rows if r[1] is not None]
    if not rows:
        return {"n": 0, "dropped": total}
    g = np.array([x[0] for x in rows])
    P = [np.asarray(x[1], float) for x in rows]
    p = np.array([int(np.argmax(x)) for x in P])
    c = np.array([float(np.max(x)) for x in P])
    corr = (p == g).astype(float)
    return {"n": len(rows), "dropped": total - len(rows),
            "accuracy": round(float(corr.mean()), 4),
            "accuracy_counting_dropped": round(float(corr.sum() / total), 4),
            "ece": round(ece_score(c, corr), 4),
            "brier": round(float(np.mean([((x - np.eye(len(x))[gi]) ** 2).sum() for x, gi in zip(P, g)])), 4),
            "nll": round(float(np.mean([-math.log(max(float(x[gi]), 1e-12)) for x, gi in zip(P, g)])), 4),
            "mean_confidence": round(float(c.mean()), 4)}


def soft_metrics(pairs):
    """pairs: [(probs, gold_soft)] -> soft accuracy (sum p*g) and Brier vs the soft gold."""
    soft, brier = [], []
    for pp, gp in pairs:
        gp = np.asarray(gp, float)
        if gp.sum() <= 0:
            continue
        gp = gp / gp.sum()
        pp = np.asarray(pp, float)
        pp = pp[:len(gp)] if len(pp) >= len(gp) else np.pad(pp, (0, len(gp) - len(pp)))
        pp = pp / max(pp.sum(), 1e-12)
        soft.append(float((pp * gp).sum()))
        brier.append(float(((pp - gp) ** 2).sum()))
    return {"soft_accuracy": round(float(np.mean(soft)), 4) if soft else None,
            "brier_vs_soft": round(float(np.mean(brier)), 4) if brier else None}
