#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""跑這組測試，將真實 API 回應存進 runs/<日期>.json。
Runs this suite; saves real API responses into runs/<date>.json.

兩題 Noul + 門檻分流:高信心才觸發 active/reject,其餘一律進批次複查。
Two Noul questions + a threshold: only a confident answer triggers
active/reject; everything else routes to batch review.
"""
import sys, os, json, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))
from jev_client import get_client  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLD = 0.75

ACTIVE_Q = (
    "Read the specific reason this topic is being watched (in state), not just the general topic. "
    "Does this captured item clearly and specifically match that watch reason, containing something "
    "genuinely actionable (a breaking change, a deprecation, a new capability worth adopting, or -- for "
    "the general-awareness topics -- a genuinely major announcement)? Answer only yes if you are confident; "
    "this triggers immediate, costly human attention, so it should be reserved for clear cases, not "
    "generically 'relevant' or 'legitimate' content."
)
REJECT_Q = (
    "Is this captured item pure boilerplate, a bare navigation/logistics page, legal/terms text, or "
    "otherwise substantively empty of real content -- regardless of whether the general topic is relevant? "
    "Answer only yes if you are confident; this permanently discards the item and blocks re-capture of the "
    "same source for months, so it should be reserved for clear cases."
)


def main():
    from typesafe_sdk import Noul

    client = get_client()
    data = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))
    reasons, roster, cases = data["watch_reasons"], data["roster_note"], data["cases"]

    results = []
    for c in cases:
        state = (
            f"Captured item metadata:\nTitle: {c['title']}\nURL: {c['url']}\nTopic tag: {c['topic']}\n\n"
            f"Why this topic is watched: {reasons[c['topic']]}\n\n"
            f"Content summary: {c['content']}\n\n{roster}"
        )
        resp = client.system_one(
            state=state, model="jev-latest",
            questions={"active_trigger": Noul(instructions=ACTIVE_Q),
                       "reject_trigger": Noul(instructions=REJECT_Q)},
        )
        p_active = resp.answers["active_trigger"].noul
        p_reject = resp.answers["reject_trigger"].noul
        if p_active >= THRESHOLD:
            routed = "active"
        elif p_reject >= THRESHOLD:
            routed = "rejected"
        else:
            routed = "batch_review"
        results.append({
            "id": c["id"], "topic": c["topic"], "title": c["title"],
            "historical_label": c["historical_label"], "historical_score": c["historical_score"],
            "p_active": p_active, "p_reject": p_reject, "routed": routed,
            "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
        })
        print(f"{c['id']}  hist={c['historical_label']:>9}({c['historical_score']:>3})  "
              f"routed={routed:>12}  p_active={p_active:.2f} p_reject={p_reject:.2f}  {c['title'][:42]}")

    n = len(results)
    act = [r for r in results if r["routed"] == "active"]
    rej = [r for r in results if r["routed"] == "rejected"]
    bat = [r for r in results if r["routed"] == "batch_review"]
    act_hit = sum(1 for r in act if r["historical_label"] == "active")
    rej_hit = sum(1 for r in rej if r["historical_label"] == "rejected")
    tokens = sum(r["usage"]["input_tokens"] for r in results)
    print(f"\nactive triggered {len(act)}/{n} (agreed with historical label {act_hit}/{len(act) or 1})")
    print(f"reject triggered {len(rej)}/{n} (agreed with historical label {rej_hit}/{len(rej) or 1})")
    print(f"batch_review     {len(bat)}/{n}")
    print(f"input tokens {tokens}, est. cost ${tokens/1e6*0.042:.4f}")

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "stage1-triage-filter", "model": "jev-latest", "threshold": THRESHOLD,
               "results": results}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
