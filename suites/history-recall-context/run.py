#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""跑這組測試，將真實 API 回應存進 runs/<日期>.json。
Runs this suite; saves real API responses into runs/<date>.json.

  python run.py --dry-run   只印出將送出的 state，不打 API（送出前先用眼睛校一次字）
                            print the exact states that would be sent, no API calls
"""
import sys, os, json, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))

HERE = os.path.dirname(os.path.abspath(__file__))
REPEATS = 3  # 同一題重問幾次；Jev 有隨機性，單次 choice 不足以下結論


def main():
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))

    if "--dry-run" in sys.argv:
        for c in cases:
            print(f"{c['id']}  expected={c['expected']}  scored={c['scored']}\n  {c['state']}\n")
        return

    from jev_client import get_client  # noqa: E402
    from typesafe_sdk import Choice

    client = get_client()
    Q = {"answer": Choice(
        instructions="Which is the correct answer to the multiple-choice question in the state?",
        criteria={"1": "option 1", "2": "option 2", "3": "option 3"},
    )}

    results = []
    for c in cases:
        repeats = []
        for _ in range(REPEATS):
            resp = client.system_one(state=c["state"], model="jev-latest", questions=Q)
            ans = resp.answers["answer"]
            repeats.append({
                "choice": ans.choice, "confidence": ans.confidence, "probabilities": ans.probabilities,
                "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
            })
        results.append({
            "id": c["id"], "state": c["state"], "expected": c["expected"], "scored": c["scored"],
            "note": c["note"], "repeats": repeats,
        })
        picks = " ".join(
            f"{r['choice']}@{r['confidence']:.2f}"
            + ("" if not c["scored"] else ("✓" if r["choice"] == c["expected"] else "✗"))
            for r in repeats
        )
        print(f"{c['id']}: {picks}")

    tokens = sum(r["usage"]["input_tokens"] for c in results for r in c["repeats"])
    print(f"input tokens {tokens}")

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "history-recall-context", "model": "jev-latest", "repeats": REPEATS,
               "results": results},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
