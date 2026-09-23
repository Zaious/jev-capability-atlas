#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""每一題把「所在段落＋要判斷的句子」當 state；兩個問法分開請求、各問三次。收據存進 runs/<date>.json。
Each case's state is the paragraph plus the sentence to judge; two wordings, separate requests,
three repeats each. Saves runs/<date>.json.

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
ARMS = {
    # babel-antiai 的 SELF-JUSTIFY 判準，逐字（同 suites/self-justify-detection）
    "criterion": ("標出的這句話（或其中某個子句），是不是「自證式解釋」——功能在替作者辯白、展示他想過了，"
                  "而不在讓讀者做決定？判準：刪掉這句，讀者還能做出同樣的決定嗎？能，就刪。"),
    # 作者在看過這批例子後確認的區分（2026-09-23）；因此這個問法是在樣本內寫成的
    "reader_vs_author": ("標出的這句話裡，有沒有一個句子或子句是在處理「別人會怎麼看作者」——預先替作者辯解、"
                         "澄清作者不是那個意思、避免被誤會成某種立場——而不是在告訴讀者這個主張該怎麼讀"
                         "（範圍在哪、這個詞是什麼身份、證據有多強）？"),
}


def state(c):
    return f"段落：{c['paragraph']}\n\n要判斷的句子：{c['target']}"


def main():
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]
    if "--dry-run" in sys.argv:
        for arm, q in ARMS.items():
            print(f"[{arm}] {q}\n")
        print(state(cases[0]))
        print(f"\n{len(cases)} cases x {len(ARMS)} arms x {REPEATS} repeats = {len(cases) * len(ARMS) * REPEATS} calls")
        return

    from jev_client import get_client
    from typesafe_sdk import Noul
    client = get_client()

    def ask(job):
        c, arm, rep = job
        err = None
        for attempt in range(3):
            try:
                t = time.perf_counter()
                r = client.system_one(state=state(c), model="jev-latest",
                                      questions={"q": Noul(instructions=ARMS[arm])})
                return {"id": c["id"], "arm": arm, "repeat": rep, "p_yes": round(r.answers["q"].noul, 4),
                        "model": r.model, "input_tokens": r.usage.input_tokens,
                        "latency_ms": round((time.perf_counter() - t) * 1000, 1), "state": state(c)}
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
        return {"id": c["id"], "arm": arm, "repeat": rep, "error": err, "state": state(c)}

    warm = ask((cases[0], "criterion", -1))  # 同一個函式；失敗就中止 / same function; abort on failure
    if "error" in warm:
        sys.exit(f"warm-up failed, aborting before the batch: {warm['error']}")

    jobs = [(c, arm, rep) for rep in range(REPEATS) for arm in ARMS for c in cases]
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(ask, jobs))
    ok = [r for r in rows if "error" not in r]
    meta = {"suite": "self-justify-real-draft", "requested_model": "jev-latest",
            "response_models": sorted({r["model"] for r in ok}), "date": datetime.date.today().isoformat(),
            "calls": len(rows), "errors": len(rows) - len(ok), "input_tokens": sum(r["input_tokens"] for r in ok),
            "warmup_ms_excluded": warm["latency_ms"], "repeats": REPEATS, "instructions": ARMS}
    out = os.path.join(HERE, "runs", f"{meta['date']}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"calls {meta['calls']}, errors {meta['errors']}, models {meta['response_models']}, tokens {meta['input_tokens']}")
    if meta["errors"]:
        sys.exit("errors in the batch; see receipt")


if __name__ == "__main__":
    main()
