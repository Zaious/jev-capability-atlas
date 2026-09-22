#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""每一句當一次 state，問 Jev 有沒有錯字；收據存進 runs/<日期>.json。
Each sentence is one state; ask Jev whether it contains a typo. Saves runs/<date>.json.

  python run.py --dry-run   # 印出各組數量與前幾句，不打 API / print set sizes and samples, no API calls
  python run.py             # 需要 TYPESAFE_API_KEY
Needs: pip install opencc-python-reimplemented huggingface_hub (for the SIGHAN sets)
"""
import sys, os, json, time, datetime
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "data"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "common"))
import build_cases  # noqa: E402

# 問法與 2026-09-22 試跑相同，一字不改 / same wording as the 2026-09-22 pilot, unchanged
INSTRUCTIONS = {
    "wrong_char": "Does this Traditional Chinese text contain a wrong character — a real character used in place of the correct one, producing a word that doesn't exist or doesn't fit (for example 皮帝 instead of 皇帝)? Ignore factual accuracy.",
    "any_error": "Does this Traditional Chinese text contain any typo: a wrong character, a misspelled word, or a Simplified Chinese character mixed into Traditional text? Judge only the characters and words, not whether the content is factually true.",
}

# 我們自己抓到的真實錯字（數量太少，只列出不計分）/ our own real typos: too few to score, listed only
REPO_REAL_TYPOS = [
    {"id": "real-1", "text": "大清帝國的第二任皮帝是誰？ (1)康燕 (2)雍正 (3)乾隆"},
    {"id": "real-2", "text": "背景資料：清朝皮帝順序依次為：順治、康燕、雍正、乾隆、嘉慶、道光、咸豐、同治、光緒、宣統。"},
    {"id": "real-3", "text": "金住用的參數，跡測性需要——以這份為準，不要在 README.md 裡再寫一次。"},
]


def main():
    sets = build_cases.build()
    sets["repo_real_typo"] = REPO_REAL_TYPOS
    if "--dry-run" in sys.argv:
        for name, cases in sets.items():
            print(f"{name}: {len(cases)}")
            for c in cases[:3]:
                print("   ", c["id"], c["text"])
        return

    from jev_client import get_client
    from typesafe_sdk import Noul
    client = get_client()
    qs = {k: Noul(instructions=v) for k, v in INSTRUCTIONS.items()}
    jobs = [(name, c) for name, cases in sets.items() for c in cases]

    def ask(job):
        name, c = job
        for attempt in range(3):
            try:
                r = client.system_one(state=c["text"], model="jev-latest", questions=qs)
                return name, c, {k: round(r.answers[k].noul, 4) for k in qs}, r.model, r.usage.input_tokens
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
        return name, c, {"error": err}, None, 0

    results = {name: [] for name in sets}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, (name, c, p, model, tok) in enumerate(ex.map(ask, jobs), 1):
            row = {"id": c["id"], "p": p, "model": model, "input_tokens": tok}
            # SIGHAN 原文不存進收據（授權不明，可由 build_cases.py 重建）；repo 的句子是我們自己的文字
            # SIGHAN text is not stored (license unclear; rebuildable); repo sentences are our own text
            if not c["id"].startswith("sighan"):
                row["text"] = c["text"]
            else:
                row["typo_positions"] = c.get("typo_positions", [])
            results[name].append(row)
            if i % 100 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)}", flush=True)

    rows = [r for v in results.values() for r in v]
    meta = {"suite": "zh-proofreading", "requested_model": "jev-latest",
            "response_models": sorted({r["model"] for r in rows if r["model"]}),
            "date": datetime.date.today().isoformat(), "calls": len(rows),
            "errors": sum(1 for r in rows if "error" in r["p"]),
            "input_tokens": sum(r["input_tokens"] for r in rows), "instructions": INSTRUCTIONS,
            "sighan": {"repo": build_cases.SIGHAN_REPO, "revision": build_cases.SIGHAN_REV,
                       "seed": build_cases.SEED, "per_set": build_cases.N_PER_SET}}
    out = os.path.join(HERE, "runs", f"{meta['date']}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"meta": meta, "results": results}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"calls {meta['calls']}, errors {meta['errors']}, models {meta['response_models']}, tokens {meta['input_tokens']}")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
