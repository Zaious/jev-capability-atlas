#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Send every typed-decisions test case and every MASSIVE item to the real Jev API.
Same state and questions Laya receives in run_laya.py. Writes runs/<date>-jev.json.

  python run_jev.py [--workers 4] [--limit N]   (--limit: smoke test on the first N cases per part)
"""
import sys, os, json, time, datetime, argparse
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "common"))
import common  # noqa: E402
from jev_client import get_client  # noqa: E402


def answer_vectors(resp, questions, gold_keys):
    out = {}
    for qid, qd in questions.items():
        a = resp.answers[qid]
        if qd["type"] == "choice":
            out[qid] = common.to_vector("choice", a.probabilities, keys=gold_keys[qid])
        elif qd["type"] == "noul":
            out[qid] = common.to_vector("noul", a.noul)
        else:
            out[qid] = common.to_vector("score", a.probabilities, n=len(qd["criteria"]))
    return out


def call(client, state, questions, gold_keys):
    t0 = time.perf_counter()
    resp = client.system_one(state=state, model="jev-latest", questions=questions)
    ms = (time.perf_counter() - t0) * 1000
    return {"probs": answer_vectors(resp, questions, gold_keys), "model": resp.model,
            "ms": round(ms, 1), "input_tokens": resp.usage.input_tokens}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    client = get_client()

    td = common.load_typed_decisions()
    ms = {lg: common.load_massive(lg) for lg in common.MS_LANGS}
    if a.limit:
        td = td[:a.limit]
        ms = {lg: v[:a.limit] for lg, v in ms.items()}

    jobs = []
    for cid, wf, st, qs, gm in td:
        keys = {qid: g.get("keys") for qid, g in gm.items()}
        jobs.append(("td", cid, st, qs, keys))
    for lg, items in ms.items():
        for cid, st, qs, gi, keys in items:
            jobs.append(("ms", cid, st, qs, {"intent": keys}))

    def run(job):
        part, cid, st, qs, keys = job
        for attempt in range(3):
            try:
                return part, cid, call(client, st, qs, keys)
            except Exception as e:  # keep going; record the failure in the receipt
                err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
        return part, cid, {"error": err}

    t0 = time.time()
    results = {"td": {}, "ms": {}}
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for i, (part, cid, r) in enumerate(ex.map(run, jobs), 1):
            results[part][cid] = r
            if i % 50 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)

    rows = [r for p in results.values() for r in p.values()]
    errors = sum(1 for r in rows if "error" in r)
    models = sorted({r["model"] for r in rows if "model" in r})
    tokens = sum(r.get("input_tokens") or 0 for r in rows)
    meta = {"suite": "laya-head-to-head", "side": "jev", "requested_model": "jev-latest",
            "response_models": models, "date": datetime.date.today().isoformat(),
            "calls": len(rows), "errors": errors, "input_tokens": tokens,
            "typed_decisions": {"repo": common.TD_REPO, "revision": common.TD_REV, "cases": len(results["td"])},
            "massive": {"repo": common.MS_REPO, "revision": common.MS_REV, "langs": common.MS_LANGS,
                        "per_lang": common.MS_PER_LANG, "seed": common.MS_SEED, "n_options": common.MS_N_OPTS},
            "note": "ms = client-side wall time per call, network included"}
    suffix = "-smoke" if a.limit else ""
    out = os.path.join(HERE, "runs", f"{meta['date']}-jev{suffix}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "typed_decisions": results["td"], "massive": results["ms"]},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"calls {len(rows)}, errors {errors}, models {models}, input tokens {tokens}")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
