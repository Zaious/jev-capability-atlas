#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第二輪:state 換成「整節內文＋讀者設定＋標出的句子」,一次請求問八個維度。
Round 2: the state is the whole section + a reader profile + the marked sentence; eight
dimensions asked in one request.

同樣 34 題(data/cases.json,不動)。不做兩版比較——辨識時手上只有一份稿。
Same 34 cases (data/cases.json, unchanged). No two-version comparison: in real use there is
only one draft.

整節內文加起來接近整篇論文,超出作者同意公開的「部分段落」,所以收據**不存內文**,
只存節名、來源 commit 與送出內容的 sha256;data/round2_manifest.json 在執行前凍結,
可核對輸入沒被換過。重建內文需要作者的私人 repo(CHRONICLE_LEX)。
The sections together are close to the whole paper, beyond the "partial paragraphs" the author
agreed to publish, so receipts store no text: only the section, source commit and the sha256 of
what was sent. data/round2_manifest.json is frozen before running so the inputs can be checked.

  CHRONICLE_LEX=<path> python run_round2.py --build-manifest   # 凍結前做一次
  CHRONICLE_LEX=<path> python run_round2.py --dry-run
  CHRONICLE_LEX=<path> python run_round2.py                    # 需要 TYPESAFE_API_KEY
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "common"))
REPO = os.environ.get("CHRONICLE_LEX", "M:/ChronicleCore-Forge/chronicle-lex")
PAPER = "papers/danganronpa-persona-2026/paper.md"
MANIFEST = os.path.join(HERE, "data", "round2_manifest.json")
REPEATS = 3

# 讀者設定:依投稿場合寫,執行前凍結
READER = ("讀者設定:ACGCT 2026(第 15 屆 ACG 文化與技術國際學術研討會)的審稿人與與會者。"
          "熟悉動漫、遊戲與角色設計,多數玩過或知道《槍彈辯駁》;熟悉學術寫作的慣例;"
          "不一定熟悉 AI 代理系統的技術細節。")

# 八個維度。direction:+1 = 分數高代表「不必要／替作者辯護」,-1 = 分數高代表「必要」
DIMENSIONS = {
    "repeated": (+1, "標出的句子所說的內容,在本節它之前的文字裡已經說過了嗎?"),
    "needed_later": (-1, "如果刪掉標出的句子,本節它之後有沒有哪一句會變得看不懂、或失去它需要的依據?"),
    "about_author": (+1, "標出的句子主要在談作者自己——作者的意圖、立場、寫法,或作者可能被怎麼看——"
                         "而不是在談論點本身的內容嗎?"),
    "reader_knows": (+1, "以讀者設定裡的這位讀者來說,標出的句子所解釋的東西,是他本來就知道、不需要被告知的嗎?"),
    "preempt": (+1, "標出的句子(或其中一個子句)是在預先澄清作者不是那個意思,或避免作者被誤會成某種立場嗎?"),
    "guides_reading": (-1, "標出的句子是在告訴讀者該怎麼理解本文的主張——主張的範圍、某個術語的身份,或證據有多強嗎?"),
    "process": (+1, "標出的句子是在交代作者寫作或思考的過程——考慮過什麼、怎麼安排、為什麼這樣寫——而不是交代結果嗎?"),
    "overall": (+1, "以這位讀者來看,標出的句子是不必要的解釋,刪掉之後讀者不會失去任何需要的東西嗎?"),
}
# 事先寫死的組合規則:八維等權平均(方向已定),不在這 34 題上擬合任何權重
COMBO = "mean over the eight dimensions of p (direction +1) or 1-p (direction -1), equal weights"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def sections(text):
    """回傳 [(節名, 節內文)];去掉 frontmatter 與參考文獻。"""
    text = text.replace("\r\n", "\n")
    if text.startswith("---"):
        text = text.split("\n---", 1)[1].split("\n", 1)[1]
    text = text.split("\n## 參考文獻")[0]
    out, cur, buf = [], None, []
    for line in text.split("\n"):
        if line.startswith("## "):
            if cur is not None:
                out.append((cur, "\n".join(buf).strip()))
            cur, buf = line[3:].strip(), [line]
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out.append((cur, "\n".join(buf).strip()))
    return out


def build_state(case):
    secs = sections(git("show", f"{case['source_commit']}:{PAPER}"))
    hit = [(h, s) for h, s in secs if case["paragraph"] in s]
    assert len(hit) == 1, (case["id"], len(hit))
    head, sec = hit[0]
    para = case["paragraph"]
    assert para.count(case["target"]) == 1, case["id"]
    marked = sec.replace(para, para.replace(case["target"], "【【" + case["target"] + "】】"), 1)
    state = f"{READER}\n\n以下是論文的一節,要判斷的句子用【【】】標出。\n\n{marked}\n\n要判斷的句子:{case['target']}"
    return head, state


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_cases():
    return json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))["cases"]


def main():
    cases = load_cases()
    if "--build-manifest" in sys.argv:
        rows = []
        for c in cases:
            head, st = build_state(c)
            rows.append({"id": c["id"], "section": head, "source_commit": c["source_commit"],
                         "state_sha256": sha(st), "state_chars": len(st)})
        man = {"frozen": datetime.date.today().isoformat(), "reader": READER,
               "dimensions": {k: {"direction": d, "question": q} for k, (d, q) in DIMENSIONS.items()},
               "combo": COMBO, "repeats": REPEATS, "cases": rows}
        json.dump(man, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"manifest: {len(rows)} cases, {sum(r['state_chars'] for r in rows)} chars total")
        return

    man = json.load(open(MANIFEST, encoding="utf-8"))
    frozen = {r["id"]: r for r in man["cases"]}
    states = {}
    for c in cases:
        head, st = build_state(c)
        if sha(st) != frozen[c["id"]]["state_sha256"]:
            sys.exit(f"{c['id']}: 重建出的輸入跟凍結的 sha256 不符,中止")
        states[c["id"]] = st
    if "--dry-run" in sys.argv:
        c = cases[0]
        print(states[c["id"]][:900], "\n...\n")
        for k, (d, q) in DIMENSIONS.items():
            print(f"[{k} {d:+d}] {q}")
        print(f"\n{len(cases)} cases x {REPEATS} repeats = {len(cases) * REPEATS} calls, {len(DIMENSIONS)} questions each")
        return

    from jev_client import get_client
    from typesafe_sdk import Noul
    client = get_client()
    qs = {k: Noul(instructions=q) for k, (d, q) in DIMENSIONS.items()}

    def ask(job):
        c, rep = job
        err = None
        for attempt in range(3):
            try:
                t = time.perf_counter()
                r = client.system_one(state=states[c["id"]], model="jev-latest", questions=qs)
                return {"id": c["id"], "repeat": rep, "p": {k: round(r.answers[k].noul, 4) for k in qs},
                        "model": r.model, "input_tokens": r.usage.input_tokens,
                        "latency_ms": round((time.perf_counter() - t) * 1000, 1),
                        "state_sha256": frozen[c["id"]]["state_sha256"]}
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
        return {"id": c["id"], "repeat": rep, "error": err}

    warm = ask((cases[0], -1))
    if "error" in warm:
        sys.exit(f"warm-up failed, aborting before the batch: {warm['error']}")
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(ask, [(c, rep) for rep in range(REPEATS) for c in cases]))
    ok = [r for r in rows if "error" not in r]
    meta = {"suite": "self-justify-real-draft", "round": 2, "date": datetime.date.today().isoformat(),
            "requested_model": "jev-latest", "response_models": sorted({r["model"] for r in ok}),
            "calls": len(rows), "errors": len(rows) - len(ok), "input_tokens": sum(r["input_tokens"] for r in ok),
            "warmup_ms_excluded": warm["latency_ms"], "manifest_sha256": sha(open(MANIFEST, encoding="utf-8").read())}
    out = os.path.join(HERE, "runs", f"{meta['date']}-round2.json")
    json.dump({"meta": meta, "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"calls {meta['calls']}, errors {meta['errors']}, models {meta['response_models']}, tokens {meta['input_tokens']}")
    if meta["errors"]:
        sys.exit("errors in the batch; see receipt")


if __name__ == "__main__":
    main()
