#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""claim vs quote 關係判讀，合成資料(非真實論文)。存真實 log 進 runs/。
Claim-vs-quote relation judgment on synthetic (not a real manuscript's) data.
The real 16/12-citation methodology validation ran against an actual
in-progress academic paper -- see the linked evaluation report in the repo
README for those aggregate numbers. This suite ships reproducible synthetic
data instead, so anyone can re-run it without needing access to unpublished
work."""
import sys, os, json, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))
from jev_client import get_client  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    from typesafe_sdk import Choice

    client = get_client()
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))
    Q = {"relation": Choice(
        instructions="Does the quote support, contradict, or fail to address the claim?",
        criteria={
            "supports": "The quote states the claim or directly implies that it is true",
            "contradicts": "The quote states the opposite of the claim or implies the claim is false",
            "says_nothing": "The quote does not address what the claim asserts, either way",
        },
    )}

    results, correct = [], 0
    for c in cases:
        state = {"claim": c["claim"], "quote": c["quote"]}
        resp = client.system_one(state=state, model="jev-latest", questions=Q)
        ans = resp.answers["relation"]
        hit = ans.choice == c["expected"]
        correct += hit
        results.append({"id": c["id"], "expected": c["expected"], "choice": ans.choice,
                         "confidence": ans.confidence, "probabilities": ans.probabilities,
                         "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}})
        print(f"  {c['id']}: {ans.choice} conf={ans.confidence:.2f} {'✓' if hit else '✗'}")
    print(f"citation-support-check: {correct}/{len(cases)}")

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "citation-support-check", "model": "jev-latest", "results": results},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
