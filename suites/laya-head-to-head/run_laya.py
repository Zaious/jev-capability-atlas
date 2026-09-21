#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run the same cases through Laya's public API (laya.load(...).predict) on CPU.
Writes runs/<date>-laya.json. Needs: pip install laya==0.3.4 torch pandas pyarrow

  python run_laya.py [--limit N] [--threads N]
"""
import sys, os, json, time, datetime, argparse

os.environ.setdefault("USE_TF", "0")          # same guards Laya's own benchmark script sets
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

# checkpoint -> pinned Hub revision (see protocol.yaml)
CHECKPOINTS = {
    "laya": ("convaiinnovations/laya", "1c5edc17a7acd8701df6fc341c0d179f1c62c982"),
    "laya-multilingual": ("convaiinnovations/laya-multilingual", "052592a15d198d9ad47da779604259b10b47b7aa"),
    "laya-typed-decisions": ("convaiinnovations/laya-typed-decisions", "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"),
}
# which checkpoints answer which part; the typed-decisions checkpoint is a specialist
# fine-tuned on that benchmark's train split, so it only runs there
PARTS = {"td": ["laya", "laya-multilingual", "laya-typed-decisions"], "ms": ["laya", "laya-multilingual"]}


def vectors(res, questions, gold_keys):
    out = {}
    for qid, qd in questions.items():
        a = res["answers"][qid]
        if qd["type"] == "choice":
            out[qid] = common.to_vector("choice", a["probabilities"], keys=gold_keys[qid])
        elif qd["type"] == "noul":
            out[qid] = common.to_vector("noul", a["noul"])
        else:
            out[qid] = common.to_vector("score", a["probabilities"], n=len(qd["criteria"]))
    return out


def predict(agent, st, qs, keys):
    """Whole case in one call, as a user would; if a question overflows the head budget
    (predict raises ValueError), fall back to one call per question and mark the overflow as None."""
    t0 = time.perf_counter()
    try:
        res = agent.predict(st, qs)
        return {"probs": vectors(res, qs, keys), "ms": round((time.perf_counter() - t0) * 1000, 1),
                "input_tokens": res["usage"]["input_tokens"]}
    except ValueError:
        probs, dropped = {}, []
        for qid, qd in qs.items():
            try:
                probs.update(vectors(agent.predict(st, {qid: qd}), {qid: qd}, keys))
            except ValueError:
                probs[qid] = None
                dropped.append(qid)
        return {"probs": probs, "ms": round((time.perf_counter() - t0) * 1000, 1), "dropped": dropped}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--threads", type=int, default=0)
    a = ap.parse_args()

    import torch
    import laya
    from huggingface_hub import snapshot_download
    if a.threads:
        torch.set_num_threads(a.threads)

    td = common.load_typed_decisions()
    ms = [x for lg in common.MS_LANGS for x in common.load_massive(lg)]
    if a.limit:
        td = td[:a.limit]
        ms = [x for lg in common.MS_LANGS for x in common.load_massive(lg)[:a.limit]]

    results = {name: {"typed_decisions": {}, "massive": {}} for name in CHECKPOINTS}
    timing = {}
    for name, (repo, rev) in CHECKPOINTS.items():
        path = snapshot_download(repo, revision=rev)
        agent = laya.load(path, device="cpu")
        agent.model.eval()
        t0 = time.time()
        if name in PARTS["td"]:
            for cid, wf, st, qs, gm in td:
                keys = {qid: g.get("keys") for qid, g in gm.items()}
                results[name]["typed_decisions"][cid] = predict(agent, st, qs, keys)
        if name in PARTS["ms"]:
            for cid, st, qs, gi, keys in ms:
                results[name]["massive"][cid] = predict(agent, st, qs, {"intent": keys})
        timing[name] = round(time.time() - t0, 1)
        print(f"  {name}: {timing[name]}s", flush=True)
        del agent

    meta = {"suite": "laya-head-to-head", "side": "laya", "laya_version": laya.__version__,
            "torch": torch.__version__, "device": "cpu", "threads": torch.get_num_threads(),
            "checkpoints": {k: {"repo": r, "revision": v} for k, (r, v) in CHECKPOINTS.items()},
            "date": datetime.date.today().isoformat(), "seconds_per_checkpoint": timing,
            "api": "laya.load(path, device='cpu').predict(state, questions) -- shipped temperatures, no refit",
            "typed_decisions": {"repo": common.TD_REPO, "revision": common.TD_REV, "cases": len(td)},
            "massive": {"repo": common.MS_REPO, "revision": common.MS_REV, "langs": common.MS_LANGS,
                        "per_lang": common.MS_PER_LANG, "seed": common.MS_SEED, "n_options": common.MS_N_OPTS}}
    suffix = "-smoke" if a.limit else ""
    out = os.path.join(HERE, "runs", f"{meta['date']}-laya{suffix}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "results": results}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
