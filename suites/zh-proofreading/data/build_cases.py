#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""建立這組測試的題目 / build this suite's cases.

三組 / three sets:
  sighan_error : SIGHAN 2015 CSC test sentences that contain a real learner typo
  sighan_clean : SIGHAN 2015 test sentences with no typo
  repo_clean   : Traditional-Chinese sentences taken from this repo's own docs
                 (data/repo_clean.json, frozen so re-runs use the same sentences)

SIGHAN 2015 is Traditional Chinese, but the official download needs a registration
form. The only open copy we found (AnonymousSubmissionOnly/sighan15 on Hugging Face)
had been converted to Simplified, so each (wrong, correct) pair is converted back
with OpenCC s2tw (character-level, keeps length). A pair is kept only if, after
conversion, the two sentences still differ at exactly the same positions as before
-- i.e. the typo survived the round trip and nothing else changed.

Needs: pip install opencc-python-reimplemented huggingface_hub
Writes nothing to the repo except data/repo_clean.json when --freeze-repo is given.
"""
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

SIGHAN_REPO = "AnonymousSubmissionOnly/sighan15"
SIGHAN_REV = "1a936bafdb86abcb8bddae860504302c77b4fd9a"
SEED = 11
N_PER_SET = 200


def diff_positions(a, b):
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def load_sighan():
    from huggingface_hub import hf_hub_download
    import opencc
    cc = opencc.OpenCC("s2tw")
    path = hf_hub_download(SIGHAN_REPO, "test.txt", repo_type="dataset", revision=SIGHAN_REV)
    errors, clean, dropped = [], [], 0
    for n, line in enumerate(open(path, encoding="utf-8").read().splitlines()):
        wrong, correct = line.split("\t")
        before = diff_positions(wrong, correct)
        tw, tc = cc.convert(wrong), cc.convert(correct)
        if len(tw) != len(wrong) or len(tc) != len(correct) or diff_positions(tw, tc) != before:
            dropped += 1
            continue
        case = {"id": f"sighan15-test-{n:04d}", "text": tw}
        if before:
            case["typo_positions"] = before
            case["correct"] = tc
            errors.append(case)
        else:
            clean.append(case)
    return errors, clean, dropped


SENT_SPLIT = re.compile(r"(?<=[。！？])")
CJK = re.compile(r"[一-鿿]")
QUOTED_TYPOS = re.compile("皮帝|康燕|金住|跡測性|另写|實际|此处|没有")


def extract_repo_sentences():
    """Plain Traditional-Chinese prose sentences from the repo's zh docs, no code or links."""
    files = ["README.md", "AGENTS.md", "CONTRIBUTING.md", "capability-map.md", "jev-variants.md",
             "browser-automation.md"]
    files += [f"suites/{d}/README.md" for d in sorted(os.listdir(os.path.join(ROOT, "suites")))
              if os.path.exists(os.path.join(ROOT, "suites", d, "README.md")) and d not in ("TEMPLATE", "zh-proofreading")]
    out = []
    for f in files:
        text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        zh = text.split("\n---\n")[0]  # Chinese block only
        for para in zh.split("\n"):
            if para.startswith(("|", "#", ">", "```", "- [", "<")):
                continue
            for s in SENT_SPLIT.split(para):
                # skip rather than strip: removing a code span leaves a sentence with a hole,
                # and sentences that quote our own historical typos aren't clean text
                if "`" in s or QUOTED_TYPOS.search(s):
                    continue
                s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)      # keep link text, drop target
                s = re.sub(r"\*\*|[🔬📚📖💭]", "", s).strip(" -*")
                cjk = len(CJK.findall(s))
                if 12 <= len(s) <= 90 and cjk / max(1, len(s)) > 0.6 and "http" not in s:
                    out.append({"source": f, "text": s})
    return out


def main():
    rng = random.Random(SEED)
    if "--freeze-repo" in sys.argv:
        sents = extract_repo_sentences()
        # these sentences are known-corrected text; the historical typos were fixed before freezing
        pick = rng.sample(sents, min(N_PER_SET, len(sents)))
        for i, s in enumerate(pick):
            s["id"] = f"repo-{i:03d}"
        json.dump(pick, open(os.path.join(HERE, "repo_clean.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"froze {len(pick)} of {len(sents)} repo sentences -> data/repo_clean.json")
        return
    errors, clean, dropped = load_sighan()
    print(f"sighan: {len(errors)} with typo, {len(clean)} clean kept; {dropped} pairs dropped by the round-trip check")


def build():
    """Return the three sets used by run.py (SIGHAN sampled with a fixed seed)."""
    rng = random.Random(SEED)
    errors, clean, _ = load_sighan()
    repo = json.load(open(os.path.join(HERE, "repo_clean.json"), encoding="utf-8"))
    return {"sighan_error": rng.sample(errors, N_PER_SET),
            "sighan_clean": rng.sample(clean, N_PER_SET),
            "repo_clean": repo}


if __name__ == "__main__":
    main()
