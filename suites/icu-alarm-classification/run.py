#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""跑這組測試，將真實 API 回應存進 runs/<日期>.json。
Runs this suite; saves real API responses into runs/<date>.json.

data/cases.json 的 state 是從 PhysioNet/CinC Challenge 2015 原始波形抽出來的文字特徵
（見 data/extract_features.py），不是這支腳本產生的——這支只負責打 API。
The `state` in data/cases.json was extracted from PhysioNet/CinC Challenge 2015
raw waveforms (see data/extract_features.py) -- this script only calls the API.
"""
import sys, os, json, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))
from jev_client import get_client  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

QUESTION = (
    "Based only on the bedside monitor data described in the state, is this alarm "
    "a real, clinically significant event -- not an artifact, sensor noise, motion "
    "artifact, or lead-off?"
)


def main():
    from typesafe_sdk import Noul

    client = get_client()
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))
    Q = {"is_real": Noul(instructions=QUESTION)}

    results = []
    n_correct = 0
    for c in cases:
        resp = client.system_one(state=c["state"], model="jev-latest", questions=Q)
        p_real = resp.answers["is_real"].noul
        predicted = 1 if p_real >= 0.5 else 0
        correct = predicted == c["expected_true_alarm"]
        n_correct += correct
        row = {
            "id": c["id"],
            "alarm_type": c["alarm_type"],
            "true_alarm": c["expected_true_alarm"],
            "state": c["state"],
            "question": QUESTION,
            "model": resp.model,
            "p_real": p_real,
            "predicted": predicted,
            "correct": correct,
            "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
        }
        results.append(row)
        print(f"{c['id']} ({c['alarm_type']}, true={c['expected_true_alarm']}): "
              f"p_real={p_real:.3f} pred={predicted} {'✓' if correct else '✗'}")

    print(f"\n{n_correct}/{len(cases)} correct ({n_correct/len(cases):.1%})")

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "icu-alarm-classification", "model": "jev-latest", "results": results},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
