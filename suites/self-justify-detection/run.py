#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""每一段當一次 state，問 Jev 這段裡有沒有自證式解釋；兩個臂分開請求、各問三次。
Each paragraph is one state; ask Jev whether it contains a self-justifying sentence.
The two arms are separate requests, three repeats each. Saves runs/<date>.json.

  python run.py --dry-run   # 印出題目與前幾段，不打 API / print the questions and samples, no API calls
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

# 判準那一句逐字取自 babel-antiai 的 SELF-JUSTIFY 一節（經其作者同意公開）。
# The criterion sentence is verbatim from babel-antiai's SELF-JUSTIFY section (published with its author's consent).
CRITERION = ("這段文字裡，有沒有至少一句是「自證式解釋」——句子的功能在替作者辯白、展示他想過了，"
             "而不在讓讀者做決定？判準：刪掉這句，讀者還能做出同樣的決定嗎？能，就刪。")
# 三種正當解釋取自 babel-antiai 自己記錄的「正當、不該抓」的情況。
# The three legitimate kinds come from babel-antiai's own documented legitimate cases.
EXCEPTIONS = ("以下三種是正當的解釋，不算：①說明做法的理由，而且讀者需要這個理由才能處理例外或判斷能不能照做；"
              "②對不熟背景的讀者補上他需要的前提或名詞解釋；③安全、法律或健康上必要的免責與提醒。")
ARMS = {
    "J1_criterion": CRITERION,
    "J2_with_exceptions": CRITERION + EXCEPTIONS,
}


def load_cases():
    return json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]


def main():
    cases = load_cases()
    if "--dry-run" in sys.argv:
        for arm, q in ARMS.items():
            print(f"[{arm}] {q}\n")
        for c in cases[:3]:
            print(c["id"], c["stratum"], c["label"], c["text"])
        print(f"\n{len(cases)} cases x {len(ARMS)} arms x {REPEATS} repeats = {len(cases) * len(ARMS) * REPEATS} calls")
        return

    from jev_client import get_client
    from typesafe_sdk import Noul
    client = get_client()

    jobs = [(c, arm, rep) for rep in range(REPEATS) for arm in ARMS for c in cases]

    def ask(job):
        c, arm, rep = job
        err = None
        for attempt in range(3):
            try:
                t = time.perf_counter()
                r = client.system_one(state=c["text"], model="jev-latest",
                                      questions={"q": Noul(instructions=ARMS[arm])})
                ms = round((time.perf_counter() - t) * 1000, 1)
                a = r.answers["q"]
                return {"id": c["id"], "arm": arm, "repeat": rep, "p_yes": round(a.noul, 4), "model": r.model,
                        "input_tokens": r.usage.input_tokens, "latency_ms": ms, "state": c["text"]}
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
        return {"id": c["id"], "arm": arm, "repeat": rep, "error": err, "state": c["text"]}

    # 暖機走跟正式呼叫同一個函式、不計入；它失敗就代表整批都會失敗，直接中止。
    # 2026-09-23 第一次跑時暖機走另一條路徑，讀答案的 bug 因此沒被抓到，360 次全部白跑。
    # The warm-up goes through the same function as the real calls and is excluded; if it
    # fails, the whole batch would fail, so stop. On the first 2026-09-23 attempt the warm-up
    # took a different path, a bug in reading the answer went uncaught, and all 360 calls were wasted.
    warm = ask((cases[0], "J1_criterion", -1))
    if "error" in warm:
        sys.exit(f"warm-up failed, aborting before the batch: {warm['error']}")
    warmup_ms = warm["latency_ms"]

    rows = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, row in enumerate(ex.map(ask, jobs), 1):
            rows.append(row)
            if i % 60 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)}", flush=True)

    ok = [r for r in rows if "error" not in r]
    meta = {"suite": "self-justify-detection", "requested_model": "jev-latest",
            "response_models": sorted({r["model"] for r in ok}),
            "date": datetime.date.today().isoformat(), "calls": len(rows),
            "errors": len(rows) - len(ok), "input_tokens": sum(r["input_tokens"] for r in ok),
            "warmup_ms_excluded": warmup_ms, "repeats": REPEATS, "instructions": ARMS}
    out = os.path.join(HERE, "runs", f"{meta['date']}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"calls {meta['calls']}, errors {meta['errors']}, models {meta['response_models']}, "
          f"tokens {meta['input_tokens']}, warm-up {warmup_ms} ms excluded")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
