#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""日文：同一批句子，兩個標準答案——「讀的人看到什麼」與「寫的人當時真的感覺什麼」。
Japanese: the same sentences with two oracles -- what a reader sees, and what the writer felt.

前兩組 suite 拿兩份不同的語料去對照「答案在文字裡」與「答案在演出裡」，那個比較有一個
弱點：兩份語料不只標註方式不同，語料本身也不同。WRIME 把這個混淆拿掉了——**同一句話，
筆者本人標一次（主観）、三個群眾標註者只看文字各標一次（客観）**。

所以這組能做到前兩組做不到的事：
  1. 日文（官方說 CJK 較弱，我們之前只測過繁中）。
  2. 同一批句子上直接比兩個標準答案，沒有語料差異的混淆。
  3. **算得出人類天花板**：三個標註者彼此同意多少、他們跟筆者本人同意多少。
     沒有這條，任何準確率都讀不出是模型不行還是題目本身就答不出來。

  python build_cases.py            # 抽樣並寫出 cases.json
  python build_cases.py --stats    # 只印語料層級的基準線與人類天花板（不打 API）
  python build_cases.py --verify RUN.json

語料是 CC BY-NC-ND 4.0，原文不進 repo，也不散布修改版；見 protocol.yaml。
The corpus is CC BY-NC-ND 4.0: its text is neither redistributed nor modified here.
"""
import collections
import csv
import hashlib
import io
import json
import os
import random
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

WRIME_REPO = "ids-cv/wrime"
WRIME_REV = "0681109ab52711110a491f055133033a4e0aea9c"   # 該檔案最後一次變動的 commit
WRIME_FILE = "wrime-ver1.tsv"
SPLIT = "test"

SAMPLE = 400          # 自然分布隨機抽樣（不做每類等量），這樣人類天花板才直接適用
SEED = 37

EMO = ["Joy", "Sadness", "Anticipation", "Surprise", "Anger", "Fear", "Disgust", "Trust"]
JA = {"Joy": "喜び", "Sadness": "悲しみ", "Anticipation": "期待", "Surprise": "驚き",
      "Anger": "怒り", "Fear": "恐れ", "Disgust": "嫌悪", "Trust": "信頼", "Neutral": "平静"}

# 選項用日文寫，描述也用日文——問日文的句子就別混英文進去
LABELS = {
    "喜び": "うれしい、楽しい、ありがたい、誇らしいといった気持ちが出ている。",
    "悲しみ": "かなしい、さびしい、がっかり、つらいという気持ちが出ている。",
    "期待": "これから起きることを待っている、楽しみにしている、そうなってほしいという気持ちが出ている。",
    "驚き": "思いがけない、びっくりした、意外だという気持ちが出ている。",
    "怒り": "腹が立つ、いらいらする、責めたいという気持ちが出ている。",
    "恐れ": "こわい、不安だ、心配だという気持ちが出ている。",
    "嫌悪": "いやだ、うんざりする、受けつけないという気持ちが出ている。",
    "信頼": "相手や物事を信じている、安心して任せているという気持ちが出ている。",
    "平静": "はっきりした感情が出ていない。事実を述べているだけ、または短すぎて判断できない場合もこれを選ぶ。",
}


def fetch():
    cache = os.path.join(HERE, "_cache")
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"wrime_{WRIME_REV[:8]}_{WRIME_FILE}")
    if not os.path.exists(path):
        url = f"https://raw.githubusercontent.com/{WRIME_REPO}/{WRIME_REV}/{WRIME_FILE}"
        with urllib.request.urlopen(url, timeout=180) as r:
            open(path, "wb").write(r.read())
    return list(csv.DictReader(io.StringIO(open(path, encoding="utf-8-sig").read()), delimiter="\t"))


def label(row, prefix):
    """八個強度取最大；全為 0 就是平静。平手時照 EMO 的固定順序取，結果才可重現。"""
    vals = [(int(row[f"{prefix}_{e}"]), e) for e in EMO]
    top = max(v for v, _ in vals)
    if top == 0:
        return JA["Neutral"]
    return JA[sorted((e for v, e in vals if v == top), key=EMO.index)[0]]


def consensus(three):
    c = collections.Counter(three).most_common()
    return c[0][0] if c[0][1] >= 2 else None


def rows():
    return [r for r in fetch() if r["Train/Dev/Test"] == SPLIT]


def build():
    out = []
    for n, r in enumerate(rows()):
        readers = [label(r, f"Reader{i}") for i in (1, 2, 3)]
        cons = consensus(readers)
        if not cons:                      # 三個人各說各話的句子不收：沒有可用的客觀答案
            continue
        out.append({
            "id": f"wrime-{SPLIT}-{n}",
            "text": " ".join(r["Sentence"].split()),
            "reader_gold": cons,
            "writer_gold": label(r, "Writer"),
            "readers": readers,
        })
    rng = random.Random(SEED)
    picked = rng.sample(sorted(out, key=lambda c: c["id"]), min(SAMPLE, len(out)))
    return sorted(picked, key=lambda c: int(c["id"].rsplit("-", 1)[1]))


def state_hash(state):
    blob = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def verify(run_path):
    import run as runner
    run = json.load(open(run_path, encoding="utf-8"))
    rebuilt = {c["id"]: state_hash(st) for c, st in runner.states(build())}
    bad = [r for r in run["results"] if rebuilt.get(r["id"]) != r.get("state_sha256")]
    print(f"{len(run['results'])} receipts, {len(bad)} hash mismatches")
    if bad:
        sys.exit(1)


def baselines(cases=None):
    """人類天花板與基準線。全部零成本、不打 API。"""
    allr = []
    for r in rows():
        readers = [label(r, f"Reader{i}") for i in (1, 2, 3)]
        cons = consensus(readers)
        allr.append((readers, cons, label(r, "Writer")))
    have = [x for x in allr if x[1]]

    hits = tot = 0
    for readers, _, _ in have:
        for k in range(3):
            pair = [readers[j] for j in range(3) if j != k]
            if pair[0] == pair[1]:           # 另外兩人一致，才拿來當這一題的標準
                tot += 1
                hits += readers[k] == pair[0]

    out = {
        "split": SPLIT,
        "test_rows": len(allr),
        "reader_consensus_rows": len(have),
        "reader_consensus_rate": round(len(have) / len(allr), 4),
        "reader_majority_class": collections.Counter(c for _, c, _ in have).most_common(1)[0][0],
        "reader_majority_baseline": round(
            collections.Counter(c for _, c, _ in have).most_common(1)[0][1] / len(have), 4),
        "human_ceiling_reader": round(hits / tot, 4),
        "human_ceiling_reader_n": tot,
        "writer_majority_class": collections.Counter(w for _, _, w in have).most_common(1)[0][0],
        "writer_majority_baseline": round(
            collections.Counter(w for _, _, w in have).most_common(1)[0][1] / len(have), 4),
        "human_ceiling_writer": round(sum(1 for _, c, w in have if c == w) / len(have), 4),
    }
    if cases:
        out["sample_reader_majority_baseline"] = round(
            collections.Counter(c["reader_gold"] for c in cases).most_common(1)[0][1] / len(cases), 4)
        out["sample_writer_majority_baseline"] = round(
            collections.Counter(c["writer_gold"] for c in cases).most_common(1)[0][1] / len(cases), 4)
        out["sample_human_ceiling_writer"] = round(
            sum(1 for c in cases if c["reader_gold"] == c["writer_gold"]) / len(cases), 4)
    return out


def main():
    if "--verify" in sys.argv:
        sys.path.insert(0, os.path.dirname(HERE))
        verify(sys.argv[sys.argv.index("--verify") + 1])
        return
    if "--stats" in sys.argv:
        for k, v in baselines(build()).items():
            print(f"  {k}: {v}")
        return
    cases = build()
    json.dump(cases, open(os.path.join(HERE, "cases.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{len(cases)} cases")
    print(" reader gold:", dict(collections.Counter(c["reader_gold"] for c in cases).most_common()))
    print(" writer gold:", dict(collections.Counter(c["writer_gold"] for c in cases).most_common()))


if __name__ == "__main__":
    main()
