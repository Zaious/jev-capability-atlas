#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""引用查核帳逐條核:主張 vs 證據引句。兩個臂,各問三次;收據存進 runs/<date>.json。
Check each audited citation claim against its evidence quotes. Two arms, three repeats each.

  A_audit_jev  照抄 paper-source-audit/audit-jev.py:每段引句一次請求,一題 Choice
               (supports / contradicts / says_nothing),state={claim, quote, where}
  B_three      一次請求、整筆主張與全部引句,三題 Noul;state 帶引用編號,只判該引用負責的部分

  python run.py --dry-run
  python run.py             # 需要 TYPESAFE_API_KEY
"""
import datetime
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "common"))
REPEATS = 3

# A:逐字照抄 audit-jev.py v0.1 的問法
A_INSTRUCTIONS = "Does the quote support, contradict, or fail to address the claim?"
A_CRITERIA = {
    "supports": "The quote states the claim or directly implies that it is true",
    "contradicts": "The quote states the opposite of the claim or implies the claim is false",
    "says_nothing": "The quote does not address what the claim asserts, either way",
}
# B:三題;主判斷事先定為 uncovered_detail
SCOPE = ("Consider only the part of the claim that is attributed to the source named in cited_as "
         "(the claim sentence may also cite other sources; ignore their parts). ")
B_QUESTIONS = {
    "supports_all": SCOPE + "Do the quotes, taken together, support every element of that part?",
    "uncovered_detail": SCOPE + ("Does that part contain a specific detail - a name, a term presented in quotation "
                                 "marks, an example, a listed reason, or a comparison - that none of the quotes mention?"),
    "overclaim": SCOPE + "Does that part present the source's point more broadly or more strongly than the quotes do?",
}


def load_cases():
    return json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]


def main():
    cases = load_cases()
    if "--dry-run" in sys.argv:
        c = next(x for x in cases if x["label"] == "misread")
        print("[A]", A_INSTRUCTIONS, A_CRITERIA)
        for k, q in B_QUESTIONS.items():
            print(f"[B {k}] {q}")
        print(json.dumps({"cited_as": c["cited_as"], "claim": c["claim"], "quotes": [q["quote"] for q in c["quotes"]]},
                         ensure_ascii=False, indent=1)[:900])
        na = sum(len(c["quotes"]) for c in cases)
        print(f"\nA: {na} quotes x {REPEATS} = {na * REPEATS} calls;  B: {len(cases)} cases x {REPEATS} = {len(cases) * REPEATS} calls")
        return

    from jev_client import get_client
    from typesafe_sdk import Choice, Noul
    client = get_client()

    def call(job):
        arm, c, qi, rep = job
        if arm == "A":
            q = c["quotes"][qi]
            state = {"claim": c["claim"], "quote": q["quote"], "where": q["where"] or "(未標出處)"}
            questions = {"relation": Choice(instructions=A_INSTRUCTIONS, criteria=A_CRITERIA)}
        else:
            state = {"cited_as": c["cited_as"], "claim": c["claim"], "quotes": [q["quote"] for q in c["quotes"]]}
            questions = {k: Noul(instructions=v) for k, v in B_QUESTIONS.items()}
        err = None
        for attempt in range(3):
            try:
                t = time.perf_counter()
                r = client.system_one(state=state, model="jev-latest", questions=questions)
                if arm == "A":
                    a = r.answers["relation"]
                    ans = {"choice": a.choice, "confidence": round(a.confidence, 4),
                           "probabilities": {k: round(v, 4) for k, v in a.probabilities.items()}}
                else:
                    ans = {k: round(r.answers[k].noul, 4) for k in questions}
                return {"arm": arm, "id": c["id"], "quote_index": qi, "repeat": rep, "answer": ans,
                        "model": r.model, "input_tokens": r.usage.input_tokens,
                        "latency_ms": round((time.perf_counter() - t) * 1000, 1), "state": state}
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
        return {"arm": arm, "id": c["id"], "quote_index": qi, "repeat": rep, "error": err}

    for arm in ("A", "B"):   # 暖機:兩種臂各走一次同一個函式,失敗就中止
        w = call((arm, cases[0], 0 if arm == "A" else None, -1))
        if "error" in w:
            sys.exit(f"warm-up {arm} failed, aborting: {w['error']}")
    jobs = [("A", c, qi, rep) for rep in range(REPEATS) for c in cases for qi in range(len(c["quotes"]))]
    jobs += [("B", c, None, rep) for rep in range(REPEATS) for c in cases]
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(call, jobs))
    ok = [r for r in rows if "error" not in r]
    meta = {"suite": "citation-claim-evidence", "date": datetime.date.today().isoformat(), "requested_model": "jev-latest",
            "response_models": sorted({r["model"] for r in ok}), "calls": len(rows), "errors": len(rows) - len(ok),
            "input_tokens": sum(r["input_tokens"] for r in ok), "repeats": REPEATS,
            "A": {"instructions": A_INSTRUCTIONS, "criteria": A_CRITERIA}, "B": B_QUESTIONS}
    out = os.path.join(HERE, "runs", f"{meta['date']}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"calls {meta['calls']}, errors {meta['errors']}, models {meta['response_models']}, tokens {meta['input_tokens']}")
    if meta["errors"]:
        sys.exit("errors in the batch; see receipt")


if __name__ == "__main__":
    main()
