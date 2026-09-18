#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同句版 + 跨句版兩組，存真實 log 進 runs/。"""
import sys, os, json, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))
from jev_client import get_client  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CRITERIA = {
    "sincere": "The speaker genuinely means the statement as written",
    "sarcastic": "Positive on the surface, but the real meaning is negative, critical, or ironic",
}


def run_same_clause(client, Choice):
    cases = json.load(open(os.path.join(HERE, "data", "same-clause.json"), encoding="utf-8"))
    Q = {"relation": Choice(
        instructions="Is the speaker's positive-sounding statement sincere, or sarcastic/ironic?",
        criteria=CRITERIA)}
    results, correct = [], 0
    for c in cases:
        resp = client.system_one(state=c["state"], model="jev-latest", questions=Q)
        ans = resp.answers["relation"]
        hit = ans.choice == c["expected"]
        correct += hit
        results.append({"id": c["id"], "expected": c["expected"], "choice": ans.choice,
                         "confidence": ans.confidence, "probabilities": ans.probabilities,
                         "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}})
        print(f"  {c['id']}: {ans.choice} conf={ans.confidence:.2f} {'✓' if hit else '✗'}")
    print(f"same-clause: {correct}/{len(cases)}")
    return results


def run_cross_turn(client, Choice):
    cases = json.load(open(os.path.join(HERE, "data", "cross-turn.json"), encoding="utf-8"))
    Q = {"relation": Choice(
        instructions="Given the earlier context, is the positive-sounding statement_to_judge sincere, "
                     "or sarcastic/ironic given what the context establishes?",
        criteria=CRITERIA)}
    results, correct, scored = [], 0, 0
    for c in cases:
        state = {"earlier_context": c["context"], "statement_to_judge": c["statement"]}
        resp = client.system_one(state=state, model="jev-latest", questions=Q)
        ans = resp.answers["relation"]
        row = {"id": c["id"], "expected": c["expected"], "choice": ans.choice,
               "confidence": ans.confidence, "probabilities": ans.probabilities,
               "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}}
        results.append(row)
        if c["expected"] is None:
            print(f"  {c['id']}: {ans.choice} conf={ans.confidence:.2f} (unscored, deliberately ambiguous)")
        else:
            scored += 1
            hit = ans.choice == c["expected"]
            correct += hit
            print(f"  {c['id']}: {ans.choice} conf={ans.confidence:.2f} {'✓' if hit else '✗'}")
    print(f"cross-turn: {correct}/{scored} scored")
    return results


def main():
    from typesafe_sdk import Choice
    client = get_client()
    print("Same-clause:")
    a = run_same_clause(client, Choice)
    print("Cross-turn:")
    b = run_cross_turn(client, Choice)

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "sarcasm-vs-sincere-praise", "model": "jev-latest",
              "same_clause": a, "cross_turn": b},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
