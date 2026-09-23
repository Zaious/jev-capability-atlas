#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""從作者一篇論文的 git 歷史抽出測試題，寫成 cases.json。
Build cases.json from the git history of one of the author's papers.

標籤來自作者**實際的刪改動作**，不是事後判斷：
  - 正例：作者在逐輪修改中刪掉（或從句中拿掉）的那一句，取它被刪前一版的原句與所在段落
  - 難反例：外形相近（預先限定、澄清、自我說明），但作者逐句核對後保留到投稿正本的句子
  - 普通反例：從 AI 協作底稿一路原封不動留到投稿正本的句子，隨機抽 20 句
Labels come from what the author actually did, not a later judgment:
  - positive: a sentence (or clause) the author cut during revision, taken from the version just before the cut
  - hard negative: similar-looking (pre-emptive scoping, clarification, self-description) but kept
    through the author's sentence-by-sentence review into the submitted version
  - ordinary negative: 20 sentences sampled from those that survived untouched from the AI-assisted draft

需要 chronicle-lex 的本機 clone（私人 repo）；cases.json 已經凍結進本 repo，一般不必重建。
Needs a local clone of chronicle-lex (private); cases.json is frozen in this repo and normally
needs no rebuilding.

  CHRONICLE_LEX=<path> python build_cases.py
"""
import json
import os
import random
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("CHRONICLE_LEX", "M:/ChronicleCore-Forge/chronicle-lex")
PAPER = "papers/danganronpa-persona-2026/paper.md"
DRAFT, FINAL = "644b3c5", "27c775c"   # AI 協作底稿收編 / 投稿正本
SEED = 29
N_ORDINARY = 20

# (id, 取句的 commit, 句中關鍵字, 被拿掉的部分, 刪改所在 commit)
POSITIVES = [
    ("P1", "de681d3^", "我把界線劃清楚了", "整段兩句", "de681d3"),
    ("P2", "86108a9^", "免得看起來像", "，免得看起來像把好幾套理論硬疊在一起", "86108a9"),
    ("P3", "f2412e4^", "各自摸到同一件事", "，但只是各自摸到同一件事，不是他讀過這篇論文後的回應", "f2412e4"),
    ("P4", "9346412^", "不是他對這篇論文的評論或背書", "是修辭上的巧合式共鳴，不是他對這篇論文的評論或背書", "9346412"),
    ("P5", "842d197^", "不是真的在猜測時間旅行", "，不是真的在猜測時間旅行", "842d197"),
    ("P6", "86108a9^", "不是認真的論證", "，不是認真的論證", "86108a9"),
    ("P7", "2d6fac0^", "並不是未來人的", "（並不是未來人的）", "2d6fac0"),
]
HARD = [
    ("H1", "只是不作為本文的論證支柱", "範圍：本文不是在證明什麼"),
    ("H2", "天生就優於通才型代理", "範圍：主張的適用條件"),
    ("H3", "不是既有理論裡的固定術語", "術語身份"),
    ("H4", "可能招來一個懷疑", "預先回應反對意見"),
    ("H5", "並非判斷的委任", "AI 使用揭露"),
    ("H6", "這當然只是修辭上的巧合", "作者保留下來的那一半限定（對照 P5、P6）"),
    ("H7", "多出來的這一位", "說明數字落差"),
]


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8").stdout


def body(text):
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    for mark in ("## 參考文獻", "## References"):
        if mark in text:
            text = text.split(mark)[0]
    return text


def split_sentences(para):
    return [s.strip() for s in re.split(r"(?<=[。！？])", para) if s.strip()]


def find(commit, key):
    paras = [p.strip() for p in body(git("show", f"{commit}:{PAPER}")).split("\n") if key in p]
    assert len(paras) == 1, (commit, key, len(paras))
    para = paras[0]
    sents = split_sentences(para)
    hit = [i for i, s in enumerate(sents) if key in s]
    assert len(hit) == 1, (commit, key)
    return para, sents[hit[0]], sents, hit[0]


def cjk(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def main():
    cases = []
    for cid, commit, key, removed, cut_in in POSITIVES:
        para, target, sents, i = find(commit, key)
        if cid == "P1":  # 兩句一起被刪 / both sentences were cut together
            target = sents[i - 1] + sents[i]
        cases.append({"id": cid, "kind": "cut", "label": True, "target": target, "paragraph": para,
                      "removed": removed, "source_commit": commit, "cut_in": cut_in})
    for cid, key, why in HARD:
        para, target, _, _ = find(FINAL, key)
        cases.append({"id": cid, "kind": "kept_lookalike", "label": False, "target": target,
                      "paragraph": para, "why_lookalike": why, "source_commit": FINAL})

    draft_paras = [p.strip() for p in body(git("show", f"{DRAFT}:{PAPER}")).split("\n")]
    final_paras = [p.strip() for p in body(git("show", f"{FINAL}:{PAPER}")).split("\n")]
    draft_sents = {s for p in draft_paras for s in split_sentences(p)}
    used = {c["target"] for c in cases}
    pool = []
    for p in final_paras:
        if not p or p.startswith(("#", "|", "![", "<", "*", ">")):
            continue
        for s in split_sentences(p):
            if s in draft_sents and s not in used and cjk(s) >= 15 and "（" not in s[:2]:
                pool.append((s, p))
    random.Random(SEED).shuffle(pool)
    for n, (s, p) in enumerate(pool[:N_ORDINARY], 1):
        cases.append({"id": f"N{n:02d}", "kind": "unchanged", "label": False, "target": s,
                      "paragraph": p, "source_commit": FINAL})

    out = {"frozen": "2026-09-23",
           "source": {"paper": "danganronpa-persona-2026 (the maintainer's own paper; ACGCT 2026, single-blind review)",
                      "draft_commit": DRAFT, "final_commit": FINAL, "ordinary_pool": len(pool), "seed": SEED},
           "license": "Excerpts from the maintainer's own manuscript, published with the author's permission; "
                      "copyright stays with the author and the excerpts are not covered by this repo's MIT license.",
           "cases": cases}
    json.dump(out, open(os.path.join(HERE, "cases.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{sum(c['label'] for c in cases)} cut, {sum(c['kind'] == 'kept_lookalike' for c in cases)} kept look-alikes, "
          f"{sum(c['kind'] == 'unchanged' for c in cases)} unchanged (pool {len(pool)})")


if __name__ == "__main__":
    main()
