#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""跑這組測試，將真實 API 回應存進 runs/<日期>.json。
Runs this suite; saves real API responses into runs/<date>.json."""
import sys, os, json, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))
from jev_client import get_client  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    from typesafe_sdk import Choice

    client = get_client()
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))
    Q = {"answer": Choice(
        instructions="Which is the correct answer to the multiple-choice question in the state?",
        criteria={"1": "option 1", "2": "option 2", "3": "option 3"},
    )}

    results = []
    for c in cases:
        resp = client.system_one(state=c["state"], model="jev-latest", questions=Q)
        ans = resp.answers["answer"]
        row = {
            "id": c["id"], "expected": c["expected"], "note": c["note"],
            "choice": ans.choice, "confidence": ans.confidence, "probabilities": ans.probabilities,
            "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
        }
        results.append(row)
        correct = "✓" if ans.choice == c["expected"] else "✗"
        print(f"{c['id']}: choice={ans.choice} conf={ans.confidence:.2f} {correct}")

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "history-recall-context", "model": "jev-latest", "results": results},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
