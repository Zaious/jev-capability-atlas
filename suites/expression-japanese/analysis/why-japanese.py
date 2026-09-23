"""為什麼日文比較弱？先拆拆看是語言還是題目。全部從既有收據算，不打 API。"""
import collections
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.path.dirname(HERE)

sys.stdout.reconfigure(encoding="utf-8")
S = SUITE
sys.path.insert(0, os.path.join(S, "data"))
import build_cases as bc  # noqa: E402

run = json.load(open(os.path.join(S, "runs", "2026-09-23.json"), encoding="utf-8"))
cases = {c["id"]: c for c in bc.build()}
calls = [r for r in run["results"] if "error" not in r]

KAO = re.compile(r"[（(][^（）()]{0,12}[）)]|[ｗw]{2,}|[!！?？]{2,}|[。．\.]{3,}|[〜～ー]{2,}"
                 r"|[\U0001F300-\U0001FAFF\u2600-\u27BF]")


def ceiling(items):
    """同一批題目上，一位標註者 vs 另外兩人一致時的同意率。"""
    hit = tot = 0
    for c in items:
        rs = c["readers"]
        for k in range(3):
            pair = [rs[j] for j in range(3) if j != k]
            if pair[0] == pair[1]:
                tot += 1
                hit += rs[k] == pair[0]
    return (round(hit / tot, 4), tot) if tot else (None, 0)


def report(name, keep):
    sub = [r for r in calls if keep(cases[r["id"]])]
    if len(sub) < 60:
        print(f"{name}: n too small ({len(sub)})")
        return
    items = [cases[i] for i in {r["id"] for r in sub}]
    acc_f = statistics.fmean(1.0 if r["felt"]["choice"] == r["reader_gold"] else 0.0 for r in sub)
    acc_e = statistics.fmean(1.0 if r["expressed"]["choice"] == r["reader_gold"] else 0.0 for r in sub)
    ceil, n = ceiling(items)
    maj = collections.Counter(r["reader_gold"] for r in sub).most_common(1)[0]
    print(f"{name}: items {len(items)}  felt {acc_f:.3f}  expressed {acc_e:.3f}  "
          f"ceiling {ceil}  felt/ceiling {acc_f / ceil:.2f}  majority {maj[1] / len(sub):.3f} ({maj[0]})")


print("=== 1. 是不是 Plutchik 的兩個非表情類別在拖？ ===")
report("all", lambda c: True)
report("排除 期待/信頼", lambda c: c["reader_gold"] not in ("期待", "信頼"))
report("只有 期待/信頼", lambda c: c["reader_gold"] in ("期待", "信頼"))

print()
print("=== 2. 長度 ===")
lens = sorted(len(c["text"]) for c in cases.values())
q1, q2, q3 = lens[len(lens) // 4], lens[len(lens) // 2], lens[3 * len(lens) // 4]
print(f"(length quartiles: {q1} / {q2} / {q3} chars)")
report(f"<= {q1} 字", lambda c: len(c["text"]) <= q1)
report(f"{q1}-{q2} 字", lambda c: q1 < len(c["text"]) <= q2)
report(f"{q2}-{q3} 字", lambda c: q2 < len(c["text"]) <= q3)
report(f"> {q3} 字", lambda c: len(c["text"]) > q3)

print()
print("=== 3. 有沒有顏文字／符號情緒標記 ===")
n_kao = sum(1 for c in cases.values() if KAO.search(c["text"]))
print(f"(posts with such markers: {n_kao} / {len(cases)})")
report("有標記", lambda c: bool(KAO.search(c["text"])))
report("沒有標記", lambda c: not KAO.search(c["text"]))

print()
print("=== 4. 它最常把什麼答成什麼（felt 對客観） ===")
conf = collections.Counter(f"{r['reader_gold']} -> {r['felt']['choice']}"
                           for r in calls if r["felt"]["choice"] != r["reader_gold"])
for k, v in conf.most_common(8):
    print("   ", k, v)

print()
print("=== 5. 人類自己最常在哪兩類之間分歧 ===")
dis = collections.Counter()
for c in cases.values():
    rs = sorted(set(c["readers"]))
    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            dis[f"{rs[i]} / {rs[j]}"] += 1
for k, v in dis.most_common(8):
    print("   ", k, v)
