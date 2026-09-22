#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從兩份現成的對白語料抽樣，組成「這句該配哪個表情」的題目。
Sample two existing dialogue corpora into "which expression fits this line" cases.

兩份語料回答的是不同的問題，所以兩份都要 / the two corpora answer different questions:

  MELD（英文，《六人行》影集台本）——有對話順序，所以能比「只給這一句」跟
  「給這一句＋前面幾句」，直接量出脈絡值多少。
  MELD (English, Friends TV scripts) -- carries turn order, so the same items can be
  asked with and without the preceding turns, measuring what context is worth.

  Chinese_Multi-Emotion_Dialogue_Dataset（繁體中文，日常對話＋電影對白＋AI 生成）
  ——沒有對話順序，只能單句；但它是繁中，正對著官方說「CJK 較弱」那條限制。
  The Chinese set has no turn order, so single-line only -- but it is Traditional
  Chinese, aimed squarely at the documented CJK weakness.

  python build_cases.py                      # 抽樣並寫出 cases.json / sample and write cases.json
  python build_cases.py --stats              # 只看兩份語料的類別分布 / just print class counts
  python build_cases.py --verify RUN.json    # 重建 state 並比對收據裡的雜湊 / rebuild and check hashes

cases.json 與 _cache/ 都不進 git：兩份語料都不是我們的，不轉載原文。釘住 revision
之後重建是決定性的，所以收據裡存雜湊就夠稽核。
Neither cases.json nor _cache/ is committed: neither corpus is ours to redistribute.
With the revisions pinned the rebuild is deterministic, so hashes in the receipts
are enough to audit.
"""
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

# 釘住版本，不然語料換了數字就對不起來 / pinned: an updated corpus silently changes the numbers
MELD_REPO = "zrr1999/MELD_Text"
MELD_REV = "442fba93972d9cc642b9bbdafd123740e02d3250"
MELD_FILE = "test_sent_emo.csv"

ZH_REPO = "Johnson8187/Chinese_Multi-Emotion_Dialogue_Dataset"
ZH_REV = "f3854f9489071a4dc0bb69f2366d95095837ce68"
ZH_FILE = "data.csv"

PER_CLASS = 40        # 每個情緒類別抽幾句 / lines sampled per emotion class
CONTEXT_TURNS = 4     # 有脈絡那一臂最多給前幾句 / at most this many preceding turns
SEED = 17

# MELD 的七類直接沿用 / MELD's seven labels, used as-is
MELD_LABELS = {
    "neutral": "The speaker's delivery is factual, flat, or carries no clear emotion; also use this when the line is too short or ambiguous to tell.",
    "joy": "The speaker sounds happy, amused, grateful, excited, or is celebrating.",
    "anger": "The speaker sounds angry, irritated, frustrated, or indignant.",
    "sadness": "The speaker sounds sad, disappointed, lonely, or hurt.",
    "surprise": "The speaker sounds astonished, amazed, or caught off guard.",
    "fear": "The speaker sounds afraid, anxious, or alarmed.",
    "disgust": "The speaker sounds disgusted, repulsed, or contemptuous.",
}

# 中文那份的八類照它自己的標籤寫描述（注意：它的資料集卡片寫的類別跟實際資料不一樣，
# 卡片列了「恐懼」與「Confuse」，實際檔案裡沒有恐懼、卻有「關切語調」——以檔案為準）
# The Chinese set's own eight labels. NOTE: its dataset card lists categories that the
# actual file does not have (the card says Fear; the file has 關切語調 and no fear).
# The file wins.
ZH_LABELS = {
    "平淡語氣": "語氣平常、陳述事實，或聽不出明顯情緒；句子太短、看不出來時也選這個。",
    "開心語調": "聽起來高興、興奮、得意、在慶祝或在道謝。",
    "悲傷語調": "聽起來難過、失落、委屈或寂寞。",
    "憤怒語調": "聽起來生氣、不耐煩、惱火或在責備。",
    "驚奇語調": "聽起來吃驚、意外、沒想到。",
    "厭惡語調": "聽起來嫌惡、受不了、看不起。",
    "疑問語調": "聽起來在發問、不確定、搞不清楚狀況。",
    "關切語調": "聽起來在關心、擔心對方，或在安慰、提醒。",
}


def fetch(repo, rev, name):
    """下載並快取到 data/_cache/；釘 revision 所以內容不會變。"""
    cache = os.path.join(HERE, "_cache")
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"{repo.replace('/', '_')}_{rev[:8]}_{name}")
    if not os.path.exists(path):
        url = f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{name}"
        with urllib.request.urlopen(url, timeout=120) as r:
            open(path, "wb").write(r.read())
    return list(csv.DictReader(io.StringIO(open(path, encoding="utf-8").read())))


def clean(text):
    return " ".join((text or "").replace("", "'").split())


def build_meld():
    rows = fetch(MELD_REPO, MELD_REV, MELD_FILE)
    by_dialogue = {}
    for r in rows:
        by_dialogue.setdefault(r["Dialogue_ID"], []).append(r)
    for turns in by_dialogue.values():
        turns.sort(key=lambda r: int(r["Utterance_ID"]))

    pool = {k: [] for k in MELD_LABELS}
    for did, turns in sorted(by_dialogue.items(), key=lambda kv: int(kv[0])):
        for i, r in enumerate(turns):
            if i == 0:                      # 沒有前文的句子兩臂不對等，不收
                continue
            line, emo = clean(r["Utterance"]), r["Emotion"]
            if not line or emo not in pool:
                continue
            before = turns[max(0, i - CONTEXT_TURNS):i]
            pool[emo].append({
                "id": f"meld-d{did}-u{r['Utterance_ID']}",
                "speaker": clean(r["Speaker"]),
                "line": line,
                "gold": emo,
                "context": [{"speaker": clean(t["Speaker"]), "line": clean(t["Utterance"])} for t in before],
            })

    rng = random.Random(SEED)
    cases = []
    for emo in sorted(pool):
        items = sorted(pool[emo], key=lambda c: c["id"])
        cases += rng.sample(items, min(PER_CLASS, len(items)))
    return sorted(cases, key=lambda c: c["id"])


def build_zh():
    rows = fetch(ZH_REPO, ZH_REV, ZH_FILE)
    pool = {k: [] for k in ZH_LABELS}
    for n, r in enumerate(rows):
        line, emo = clean(r["text"]), (r["emotion"] or "").strip()
        if not line or emo not in pool:
            continue
        pool[emo].append({"id": f"zh-{n}", "speaker": "", "line": line, "gold": emo, "context": []})

    rng = random.Random(SEED)
    cases = []
    for emo in sorted(pool):
        items = sorted(pool[emo], key=lambda c: c["id"])
        cases += rng.sample(items, min(PER_CLASS, len(items)))
    return sorted(cases, key=lambda c: int(c["id"].split("-")[1]))


def build():
    return {"meld": build_meld(), "zh": build_zh()}


def state_hash(state):
    """收據裡存這個。序列化方式固定，重建出來才對得上。"""
    blob = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def verify(run_path):
    """重建同一批 state，比對收據裡每一筆的 state_sha256。"""
    import run as runner  # noqa: F401  (run.py 定義三臂怎麼組 state)
    run = json.load(open(run_path, encoding="utf-8"))
    rebuilt = {(arm, c["id"]): state_hash(st) for arm, c, st in runner.states(build())}
    bad = [r for r in run["results"]
           if rebuilt.get((r["arm"], r["id"])) != r.get("state_sha256")]
    print(f"{len(run['results'])} receipts, {len(bad)} hash mismatches")
    if bad:
        for r in bad[:5]:
            print("   ", r["arm"], r["id"], r.get("state_sha256"))
        sys.exit(1)


def main():
    if "--verify" in sys.argv:
        sys.path.insert(0, os.path.dirname(HERE))
        verify(sys.argv[sys.argv.index("--verify") + 1])
        return
    if "--stats" in sys.argv:
        import collections
        for name, repo, rev, f, col in (("MELD", MELD_REPO, MELD_REV, MELD_FILE, "Emotion"),
                                        ("ZH", ZH_REPO, ZH_REV, ZH_FILE, "emotion")):
            rows = fetch(repo, rev, f)
            print(f"{name}: {len(rows)} rows")
            for k, v in collections.Counter(r[col] for r in rows).most_common():
                print(f"   {k}: {v}")
        return
    sets = build()
    out = os.path.join(HERE, "cases.json")
    json.dump(sets, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for name, cases in sets.items():
        import collections
        counts = collections.Counter(c["gold"] for c in cases)
        print(f"{name}: {len(cases)} cases  {dict(sorted(counts.items()))}")
    print("wrote", out)


if __name__ == "__main__":
    main()
