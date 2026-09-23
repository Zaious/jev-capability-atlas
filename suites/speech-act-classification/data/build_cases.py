#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""這句是哪一種話（陳述／提問／要對方做／承諾自己做）——而不是「說的人什麼心情」。
Which kind of utterance is this (inform / question / directive / commissive)?

前三組表情 suite 的結論是：「說話的人當時什麼情緒」在文字裡答不出來（WRIME 的人類
天花板只有 0.524，因為情緒在聲音裡）。那條路對 VRChat 這種「自己說話→自己的臉」的
場景是死的。這組測的是替代形狀：**別問情緒，問這句是哪一種話**——言語行為是真的
寫在文字裡的，理論上落在軸上自足的那一側，再由程式把種類映射成動作。

  python build_cases.py            # 抽樣並寫出 cases.json
  python build_cases.py --stats    # 只印基準線（含「標點捷徑」那條，不打 API）
  python build_cases.py --verify RUN.json

**最重要的一條基準線是標點捷徑**：光用「結尾有問號就答提問，否則答最大類別」就有
0.718。所以整體準確率會好看但沒有意義——該看的是**結尾沒有問號的那 68% 句子**，
那裡的基準線是 0.669。這組的設計就是要讓這件事看得見。

語料是 CC BY-NC-SA 4.0，原文不進 repo；見 protocol.yaml。
"""
import collections
import hashlib
import io
import json
import os
import random
import sys
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

DD_REPO = "roskoN/dailydialog"
DD_REV = "5214b2a66405abf87fd229e5c1007985501ffe3e"
DD_FILE = "test.zip"

SAMPLE = 500
CONTEXT_TURNS = 4
SEED = 41

ACT = {1: "inform", 2: "question", 3: "directive", 4: "commissive"}
LABELS = {
    "inform": "The speaker is stating something: a fact, an opinion, an answer, or a description of what happened.",
    "question": "The speaker is asking the other person for information, confirmation, or an opinion.",
    "directive": "The speaker is trying to get the other person to do something: a request, an instruction, a suggestion, or an invitation.",
    "commissive": "The speaker is committing themselves to something: accepting, agreeing, promising, or offering to do it themselves.",
}


def fetch():
    cache = os.path.join(HERE, "_cache")
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"dailydialog_{DD_REV[:8]}_{DD_FILE}")
    if not os.path.exists(path):
        url = f"https://huggingface.co/datasets/{DD_REPO}/resolve/{DD_REV}/{DD_FILE}"
        with urllib.request.urlopen(url, timeout=180) as r:
            open(path, "wb").write(r.read())
    z = zipfile.ZipFile(path)
    dlg = z.read("test/dialogues_test.txt").decode("utf-8").strip().split("\n")
    act = z.read("test/dialogues_act_test.txt").decode("utf-8").strip().split("\n")
    return dlg, act


def clean(t):
    return " ".join(t.split())


def rows():
    out = []
    dlg, act = fetch()
    for n, (d, a) in enumerate(zip(dlg, act)):
        uts = [clean(u) for u in d.split("__eou__") if u.strip()]
        acts = [int(x) for x in a.split()]
        if len(uts) != len(acts):
            continue                      # 少數幾段對不齊，整段丟掉
        for i, (u, ai) in enumerate(zip(uts, acts)):
            out.append({
                "id": f"dd-test-{n}-{i}", "dialogue": n, "index": i, "text": u,
                "gold": ACT[ai], "question_marked": "?" in u[-3:],
                "context": uts[max(0, i - CONTEXT_TURNS):i],
            })
    return out


def build():
    pool = [r for r in rows() if r["context"]]     # 兩臂要看到同一批題目
    rng = random.Random(SEED)
    picked = rng.sample(sorted(pool, key=lambda c: c["id"]), min(SAMPLE, len(pool)))
    return sorted(picked, key=lambda c: (c["dialogue"], c["index"]))


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
        sys.exit(1)


def baselines(cases=None):
    """零成本基準線。標點捷徑那條是這組的重點。"""
    allr = rows()

    def block(items, name):
        c = collections.Counter(r["gold"] for r in items)
        maj = c.most_common(1)[0]
        marked = [r for r in items if r["question_marked"]]
        unmarked = [r for r in items if not r["question_marked"]]
        shortcut = (sum(1 for r in marked if r["gold"] == "question")
                    + sum(1 for r in unmarked if r["gold"] == maj[0])) / len(items)
        cu = collections.Counter(r["gold"] for r in unmarked)
        return {
            f"{name}_n": len(items),
            f"{name}_distribution": dict(c.most_common()),
            f"{name}_majority_class": maj[0],
            f"{name}_majority_baseline": round(maj[1] / len(items), 4),
            f"{name}_punctuation_shortcut": round(shortcut, 4),
            f"{name}_question_marked_share": round(len(marked) / len(items), 4),
            f"{name}_question_marked_are_questions": round(
                sum(1 for r in marked if r["gold"] == "question") / len(marked), 4),
            f"{name}_unmarked_n": len(unmarked),
            f"{name}_unmarked_majority_class": cu.most_common(1)[0][0],
            f"{name}_unmarked_majority_baseline": round(cu.most_common(1)[0][1] / len(unmarked), 4),
        }

    out = {"split": "test", "corpus_utterances": len(allr)}
    out.update(block(allr, "corpus"))
    if cases:
        out.update(block(cases, "sample"))
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
    print(f"{len(cases)} cases  {dict(collections.Counter(c['gold'] for c in cases).most_common())}")
    print(f"question-marked: {sum(1 for c in cases if c['question_marked'])}")


if __name__ == "__main__":
    main()
