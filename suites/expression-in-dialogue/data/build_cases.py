#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""整段對話抽樣：量「聆聽表情」與「跨句換臉的頻率」。
Sample whole dialogues, to measure the listener's expression and how often the face changes.

[`suites/expression-selection/`](../../expression-selection/) 量的是「一句話配一個表情」，
每類抽一樣多句。這組換一個抽法：**整段對話照順序全拿**，因為要量的兩件事都只有在
一整段裡才看得到——

  聆聽表情：A 說了這句，**聽的人 B** 該擺什麼臉？MELD 沒有標聆聽者的表情，
    所以用 B 緊接著那一句的情緒標籤當代理答案。不完美，但是別人標的，不是我們編的。
  跨句一致性：同一個角色連續幾句話之間，表情換了幾次？跟標準答案換的次數比。

  python build_cases.py                      # 抽樣並寫出 cases.json
  python build_cases.py --stats              # 只印語料層級的基準線（不打 API）
  python build_cases.py --verify RUN.json    # 重建 state 比對收據裡的雜湊

語料原文不進 repo（見 protocol.yaml 的授權欄）；cases.json 與 _cache/ 都 gitignored。
The corpus text is not committed; cases.json and _cache/ are gitignored.
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

MELD_REPO = "zrr1999/MELD_Text"
MELD_REV = "442fba93972d9cc642b9bbdafd123740e02d3250"
MELD_FILE = "test_sent_emo.csv"

DIALOGUES = 30        # 抽幾段對話 / dialogues sampled
MIN_TURNS = 6         # 至少幾句才收（太短看不出換不換臉）/ minimum utterances
CONTEXT_TURNS = 4
SEED = 29

LABELS = {
    "neutral": "The speaker's delivery is factual, flat, or carries no clear emotion; also use this when the line is too short or ambiguous to tell.",
    "joy": "The speaker sounds happy, amused, grateful, excited, or is celebrating.",
    "anger": "The speaker sounds angry, irritated, frustrated, or indignant.",
    "sadness": "The speaker sounds sad, disappointed, lonely, or hurt.",
    "surprise": "The speaker sounds astonished, amazed, or caught off guard.",
    "fear": "The speaker sounds afraid, anxious, or alarmed.",
    "disgust": "The speaker sounds disgusted, repulsed, or contemptuous.",
}
# 聆聽那一臂問的是「聽的人」該擺什麼臉，所以選項的描述要換成聽者視角
# The listening arm asks about the person hearing the line, so the options are rewritten
LISTENER_LABELS = {
    "neutral": "The listener has no clear reason to react visibly; also use this when the line is small talk or too ambiguous to react to.",
    "joy": "The listener would look pleased, amused, or glad at what was just said.",
    "anger": "The listener would look angry, irritated, or offended by what was just said.",
    "sadness": "The listener would look saddened, disappointed, or hurt by what was just said.",
    "surprise": "The listener would look startled or taken aback by what was just said.",
    "fear": "The listener would look alarmed or worried by what was just said.",
    "disgust": "The listener would look disgusted or repelled by what was just said.",
}


def fetch(repo, rev, name):
    cache = os.path.join(HERE, "_cache")
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"{repo.replace('/', '_')}_{rev[:8]}_{name}")
    if not os.path.exists(path):
        url = f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{name}"
        with urllib.request.urlopen(url, timeout=120) as r:
            open(path, "wb").write(r.read())
    return list(csv.DictReader(io.StringIO(open(path, encoding="utf-8").read())))


def clean(t):
    return " ".join((t or "").replace("", "'").split())


def dialogues():
    by_id = collections.defaultdict(list)
    for r in fetch(MELD_REPO, MELD_REV, MELD_FILE):
        by_id[r["Dialogue_ID"]].append(r)
    out = {}
    for did, turns in by_id.items():
        turns = sorted(turns, key=lambda r: int(r["Utterance_ID"]))
        turns = [{"speaker": clean(t["Speaker"]), "line": clean(t["Utterance"]),
                  "gold": t["Emotion"], "u": int(t["Utterance_ID"])} for t in turns]
        if len(turns) >= MIN_TURNS and all(t["line"] and t["gold"] in LABELS for t in turns):
            out[did] = turns
    return out


def build():
    pool = dialogues()
    rng = random.Random(SEED)
    picked = sorted(rng.sample(sorted(pool), min(DIALOGUES, len(pool))), key=int)

    self_cases, listening = [], []
    for did in picked:
        turns = pool[did]
        for i, t in enumerate(turns):
            before = turns[max(0, i - CONTEXT_TURNS):i]
            self_cases.append({
                "id": f"d{did}-u{t['u']}", "dialogue": did, "index": i,
                "speaker": t["speaker"], "line": t["line"], "gold": t["gold"],
                "context": [{"speaker": b["speaker"], "line": b["line"]} for b in before],
            })
            if i + 1 < len(turns) and turns[i + 1]["speaker"] != t["speaker"]:
                nxt = turns[i + 1]
                listening.append({
                    "id": f"d{did}-u{t['u']}-listen", "dialogue": did, "index": i,
                    "speaker": t["speaker"], "line": t["line"],
                    "listener": nxt["speaker"],
                    "gold": nxt["gold"],              # 代理答案：聽者下一句的情緒
                    "speaker_gold": t["gold"],        # 用來算「照鏡子」基準線
                    "context": [{"speaker": b["speaker"], "line": b["line"]} for b in before],
                })
    return {"self": self_cases, "listening": listening}


def state_hash(state):
    blob = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def verify(run_path):
    import run as runner
    run = json.load(open(run_path, encoding="utf-8"))
    rebuilt = {(arm, c["id"]): state_hash(st) for arm, c, st in runner.states(build())}
    bad = [r for r in run["results"] if rebuilt.get((r["arm"], r["id"])) != r.get("state_sha256")]
    print(f"{len(run['results'])} receipts, {len(bad)} hash mismatches")
    if bad:
        for r in bad[:5]:
            print("   ", r["arm"], r["id"])
        sys.exit(1)


def corpus_baselines():
    """語料層級的基準線，零成本、不打 API——沒有這些，下面的準確率讀不出意思。"""
    pool = dialogues()
    pairs = [(t, turns[i + 1]) for turns in pool.values() for i, t in enumerate(turns[:-1])
             if turns[i + 1]["speaker"] != t["speaker"]]
    listener = collections.Counter(b["gold"] for _, b in pairs)
    mirror = sum(1 for a, b in pairs if a["gold"] == b["gold"]) / len(pairs)
    switch = tot = 0
    for turns in pool.values():
        per = collections.defaultdict(list)
        for t in turns:
            per[t["speaker"]].append(t["gold"])
        for seq in per.values():
            for x, y in zip(seq, seq[1:]):
                tot += 1
                switch += x != y
    return {
        "dialogues_ge_min_turns": len(pool),
        "listening_pairs": len(pairs),
        "listening_majority_class": round(listener.most_common(1)[0][1] / len(pairs), 4),
        "listening_majority_label": listener.most_common(1)[0][0],
        "listening_mirror_baseline": round(mirror, 4),
        "gold_same_speaker_switch_rate": round(switch / tot, 4),
        "gold_switch_opportunities": tot,
    }


def main():
    if "--verify" in sys.argv:
        sys.path.insert(0, os.path.dirname(HERE))
        verify(sys.argv[sys.argv.index("--verify") + 1])
        return
    if "--stats" in sys.argv:
        for k, v in corpus_baselines().items():
            print(f"  {k}: {v}")
        return
    sets = build()
    json.dump(sets, open(os.path.join(HERE, "cases.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for name, cases in sets.items():
        counts = collections.Counter(c["gold"] for c in cases)
        print(f"{name}: {len(cases)} cases  {dict(sorted(counts.items()))}")
    print(f"dialogues: {len({c['dialogue'] for c in sets['self']})}")


if __name__ == "__main__":
    main()
