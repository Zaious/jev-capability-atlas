#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從收據重算。/ Recompute from the receipts.
  python score.py           # 寫出 runs/<date>-scores.json
  python score.py --check   # 重算並比對,不一致就 exit 1

事先寫死的判讀規則(凍結於 run 之前):
  A 臂(audit-jev 原規則):任一段引句的 choice 不是 supports,或 confidence < 0.8 → 送人審(flag)
     排序分數 = 1 - 各段引句 P(supports) 的最大值(三次平均)
  B 臂:主判斷 = uncovered_detail(P(yes) 三次平均);門檻 0.5
     另報 supports_all(分數取 1-P)與 overclaim(P)
  指標:66 筆 ok 裡被標幾筆、3 筆 misread 被標幾筆、misread 在 69 筆裡的排名(1=最可疑)、AUC
"""
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
AUTO_ACCEPT = 0.8


def auc(pos, neg):
    return round(sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg)), 4)


def summarize(name, score, flagged, label):
    ids = sorted(score, key=lambda i: -score[i])
    rank = {i: n + 1 for n, i in enumerate(ids)}
    mis = [i for i in score if label[i] == "misread"]
    oks = [i for i in score if label[i] == "ok"]
    return {"flagged_ok": f"{sum(flagged[i] for i in oks)}/{len(oks)}",
            "flagged_misread": f"{sum(flagged[i] for i in mis)}/{len(mis)}",
            "misread_ranks": {i: rank[i] for i in sorted(mis)},
            "auc_misread_vs_ok": auc([score[i] for i in mis], [score[i] for i in oks]),
            "top10": [(i, round(score[i], 4), label[i]) for i in ids[:10]]}


def main():
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]
    label = {c["id"]: c["label"] for c in cases}
    name = sorted(f for f in os.listdir(os.path.join(HERE, "runs")) if f.endswith(".json") and f.count("-") == 2)[-1]
    run = json.load(open(os.path.join(HERE, "runs", name), encoding="utf-8"))
    rows = [r for r in run["rows"] if "error" not in r and r["repeat"] >= 0]

    # A
    per_q = {}
    for r in rows:
        if r["arm"] == "A":
            per_q.setdefault((r["id"], r["quote_index"]), []).append(r["answer"])
    a_score, a_flag, a_choices = {}, {}, {}
    for c in cases:
        qs = [per_q[(c["id"], qi)] for qi in range(len(c["quotes"]))]
        p_sup = [statistics.fmean(x["probabilities"]["supports"] for x in reps) for reps in qs]
        a_score[c["id"]] = 1 - max(p_sup)
        # 原規則逐次判;三次裡多數次會送人審就算 flag
        votes = [any(reps[k]["choice"] != "supports" or reps[k]["confidence"] < AUTO_ACCEPT for reps in qs)
                 for k in range(len(qs[0]))]
        a_flag[c["id"]] = sum(votes) * 2 > len(votes)
        a_choices[c["id"]] = [[x["choice"] for x in reps] for reps in qs]

    # B
    per_c = {}
    for r in rows:
        if r["arm"] == "B":
            per_c.setdefault(r["id"], []).append(r["answer"])
    mean = {i: {k: statistics.fmean(a[k] for a in v) for k in v[0]} for i, v in per_c.items()}
    b = {}
    for key, flip in (("uncovered_detail", False), ("supports_all", True), ("overclaim", False)):
        s = {i: (1 - m[key]) if flip else m[key] for i, m in mean.items()}
        b[key] = summarize(key, s, {i: s[i] >= 0.5 for i in s}, label)

    scores = {"run": name, "models": run["meta"]["response_models"], "calls": run["meta"]["calls"],
              "errors": run["meta"]["errors"], "input_tokens": run["meta"]["input_tokens"],
              "A_audit_jev": summarize("A", a_score, a_flag, label),
              "B_primary_uncovered_detail": b["uncovered_detail"],
              "B_supports_all": b["supports_all"], "B_overclaim": b["overclaim"],
              "per_case": {i: {"label": label[i], "A_score": round(a_score[i], 4), "A_flag": a_flag[i],
                               "A_choices": a_choices[i], **{k: round(v, 4) for k, v in mean[i].items()}}
                           for i in sorted(label)}}
    out = os.path.join(HERE, "runs", name.replace(".json", "-scores.json"))
    if "--check" in sys.argv:
        if json.load(open(out, encoding="utf-8")) != scores:
            sys.exit(f"MISMATCH: recomputed scores differ from {out}")
        print("ok: recomputed scores match", os.path.basename(out))
        return
    json.dump(scores, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k in ("A_audit_jev", "B_primary_uncovered_detail", "B_supports_all", "B_overclaim"):
        s = scores[k]
        print(f"{k:<28} ok flagged {s['flagged_ok']:>6}  misread flagged {s['flagged_misread']}  "
              f"AUC {s['auc_misread_vs_ok']}  misread ranks {s['misread_ranks']}")
    print("wrote", out)


if __name__ == "__main__":
    main()
