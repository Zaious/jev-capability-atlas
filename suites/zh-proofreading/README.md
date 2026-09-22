🇹🇼 中文｜🇬🇧 English below

# 用 Jev 校稿：抓繁體中文裡「寫成另一個字」的錯

## 這組測什麼

把一句繁體中文當成 `state`，問 Jev「這句話裡有沒有寫錯的字」，看它能不能分辨有錯字的句子和正確的句子。

## 為什麼測這個

這個 repo 自己就被錯字咬過：第一次大量生成的內容裡混了兩類錯——簡體字混進繁體（写、际、处、没），以及寫成另一個真的存在的字（皮帝、康燕、金住）。第一類已經有確定性的字元清單檢查（`scripts/zh-check/check_zh.py`，每個 PR 自動跑）；第二類沒有任何字元清單抓得到，只能靠讀。這組要回答：這種「靠語感判斷」的窄問題，能不能交給 Jev 當第二意見。照核心那條軸看，它是候選——答案就寫在句子裡，不需要外部知識——但官方說 Jev 的中日韓準確率較低 📖，要實測才知道。

## 方法論

四組句子，每句一次呼叫，同時問兩題 Noul（問法寫死在 `run.py`，跟前一天的小型試跑一字不差）：`wrong_char`（有沒有寫成另一個字）與 `any_error`（有沒有任何錯字，包括簡體字）。

| 組別 | 內容 | 句數 |
|---|---|---|
| `sighan_error` | SIGHAN 2015 中文拼寫檢查測試集裡**有錯字**的句子（學習中文的學生寫的作文，錯字是真的）| 200 |
| `sighan_clean` | 同一個測試集裡標為**沒有錯**的句子 | 200 |
| `repo_clean` | 從本 repo 的中文文件抽出的句子（含程式碼片段、或引用我們自己舊錯字的句子不收），凍結在 `data/repo_clean.json` | 152 |
| `repo_real_typo` | 我們自己那三句真實錯字（皮帝／康燕、金住／跡測性），數量太少、只列出不計分 | 3 |

- **SIGHAN 怎麼變回繁體**：SIGHAN 2015 原本就是繁體，但官方下載要填註冊表；我們找到唯一公開的副本（Hugging Face 上的 `AnonymousSubmissionOnly/sighan15`）被轉成了簡體。所以每一對「錯字句／正確句」用 OpenCC `s2tw`（逐字轉換、長度不變）轉回繁體，**只保留轉換後兩句仍然剛好在原本那些位置不同的配對**——也就是錯字在來回轉換中存活、其他地方沒被動到。1,100 對裡只有 2 對因此被丟掉。
- 抽樣種子 11；版本全部釘在 `protocol.yaml`。
- 評分：`score.py` 從收據算出排序能力（AUC：隨機拿一句有錯的、一句沒錯的，前者分數比較高的機率）與三個門檻下的抓錯率、誤報率。

## 資料來源與授權

- SIGHAN 2015 CSC：官方釋出供研究使用；我們用的公開副本標示 MIT，但它不是原始發布者。**SIGHAN 的原文不放進 repo**，執行時從釘住的版本下載並重建，收據只存句子編號和錯字位置。
- `repo_clean.json`：本 repo 自己的文字，MIT。

## 結果

收據：`runs/2026-09-22.json`（555 次呼叫、0 失敗，全部由 `jev-1.13.0` 回答，224,078 input tokens，約 0.009 美元）；評分：`runs/2026-09-22-scores.json`。

**`wrong_char`（有沒有寫成另一個字）——兩題裡較好的一題**

| 門檻 | 抓到的學生錯字 | SIGHAN「沒錯」句的誤報 | 本 repo 句子的誤報 |
|---|---|---|---|
| 0.3 | 82.5% | 31.0% | 13.8% |
| **0.5** | **67.0%** | 12.0% | **2.0%**（152 句中 3 句）|
| 0.7 | 38.0% | 5.0% | 0% |

排序能力：有錯句 vs SIGHAN「沒錯」句 0.84；有錯句 vs 本 repo 句子 0.90。我們自己的三句真實錯字：0.96、0.95、0.68（門檻 0.5 全部抓到；門檻 0.7 會漏掉「金住」那句）。

**`any_error`（有沒有任何錯字）** 每一項都比較差：排序能力 0.80／0.85，門檻 0.5 時只抓到 51.0%。想用它順便抓簡體字也不行——前一天的小型試跑裡，它把改正後的句子評得比含簡體字的句子還可疑。

**被標成可疑的 3 句本 repo 句子，我們逐句人工檢查過，都沒有錯字**：「你的任務如果是新的…能直接用的是 Jev。」「…不是雜訊/導聯脫落/動作假影嗎？」（「假影」是台灣醫學影像的通用說法）「好處是任何現成模型都能用…多半要自己調溫度。」

### 實際用在整份 repo

用這組結果做出的複查工具（`scripts/zh-check/proofread_jev.py`，門檻 0.5）掃了本 repo 全部 677 句中文：標出 16 句，逐句人工檢查——3 句是更正紀錄裡刻意引用的「康燕」「皮帝」（抓對了，只是那些錯字本來就該留著），13 句是誤報（約 1.9%，跟上表的 2.0% 一致），**沒有找到任何遺漏的錯字**。第一版工具還多標了 5 句，原因是我們把 🔬📚 這類標記刪掉、在句子裡留下空洞，看起來像錯字；改成保留標記後消失。

## 這代表什麼

💭 **當成不擋 commit、只提醒人看一眼的複查工具，門檻 0.5 站得住**：大約每 50 句正確的句子誤報 1 句，同時抓到約三分之二的學生錯字，以及我們自己那三句 AI 產生的錯字。它只會標出可疑的句子，不會告訴你正確的字，也不該拿來自動擋東西。

**分工照 repo 一路講的那樣**：簡體字交給確定性的字元清單（零成本、不會錯）；寫成另一個字這種需要語感的窄判斷交給 Jev；被標出來的交給人。

## 限制

- **SIGHAN 的錯字跟我們要抓的不是同一種**：SIGHAN 是學習中文的學生寫的，錯字多半是讀音相近（側／測、不過／不夠）；AI 生成的錯字比較像字形或亂掉的字（金住、康燕）。後者我們只有 3 句，不足以量化。
- **SIGHAN「沒錯」那組其實藏著沒被標出來的錯字**（例如「下課的時侯」「如何減化」），而且是學生的中文，文法本來就不完全通順。所以它上面的誤報率偏高，只能當上限看；本 repo 的句子才是比較可靠的反例。
- 本 repo 的句子不保證 100% 正確；被標出來的我們逐句看過，沒被標出來的沒有逐句檢查。
- 含程式碼片段的句子沒有測（去掉程式碼會在句子裡留下空洞）。
- 每句只跑一次；沒有跟專門的中文拼寫檢查模型或大型語言模型同場比較。

## 怎麼重跑

```
pip install typesafe-sdk --extra-index-url https://pypi.typesafe.ai/
pip install opencc-python-reimplemented huggingface_hub
python run.py --dry-run   # 先看各組的句子
python run.py             # 需要 TYPESAFE_API_KEY
python score.py
```

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# Proofreading with Jev: catching wrong characters in Traditional Chinese (English)

## What this tests

Hand Jev one Traditional-Chinese sentence as the `state` and ask "does this sentence contain a wrong character?" — can it tell sentences with a typo from correct ones?

## Why this task

This repo was bitten by typos itself: its first bulk-generated content mixed two kinds of error — Simplified characters inside Traditional text (写, 际, 处, 没), and real characters used in place of the right one (皮帝, 康燕, 金住). The first kind now has a deterministic character-list check (`scripts/zh-check/check_zh.py`, run on every PR); the second can't be caught by any character list — it needs a reader. This suite asks whether that kind of "judge by feel for the language" narrow question can go to Jev as a second opinion. By the core axis it's a candidate — the answer is in the sentence, no outside knowledge needed — but TypeSafe says Jev is less accurate in CJK 📖, so it needs measuring.

## Methodology

Four sets of sentences, one call per sentence, two Noul questions per call (wording fixed in `run.py`, identical to the previous day's small pilot): `wrong_char` (is a character written as a different one?) and `any_error` (any typo at all, including Simplified characters).

| Set | Contents | Sentences |
|---|---|---|
| `sighan_error` | Sentences **with a typo** from the SIGHAN 2015 Chinese Spelling Check test set (essays by learners of Chinese; the typos are real) | 200 |
| `sighan_clean` | Sentences in the same test set labelled **error-free** | 200 |
| `repo_clean` | Sentences taken from this repo's Chinese docs (skipping any with code spans or quoting our own old typos), frozen in `data/repo_clean.json` | 152 |
| `repo_real_typo` | Our own three real typo sentences (皮帝/康燕, 金住/跡測性); too few to score, listed only | 3 |

- **Getting SIGHAN back to Traditional**: SIGHAN 2015 is Traditional Chinese, but the official download needs a registration form; the only open copy we found (`AnonymousSubmissionOnly/sighan15` on Hugging Face) had been converted to Simplified. Each (wrong, correct) pair was converted back with OpenCC `s2tw` (character-level, length-preserving), **keeping only pairs that still differ at exactly the original positions** — the typo survived the round trip and nothing else changed. Only 2 of 1,100 pairs were dropped.
- Sampling seed 11; every version is pinned in `protocol.yaml`.
- Scoring: `score.py` computes ranking ability from the receipt (AUC: the probability that a random typo sentence scores above a random clean one) and the catch rate and false-alarm rate at three thresholds.

## Data source and license

- SIGHAN 2015 CSC: officially released for research; the open copy we used is labelled MIT but isn't the original publisher. **SIGHAN's text is not committed**: it's downloaded from the pinned revision and rebuilt at run time, and receipts store only sentence IDs and typo positions.
- `repo_clean.json`: this repo's own text, MIT.

## Results

Receipt: `runs/2026-09-22.json` (555 calls, 0 errors, all answered by `jev-1.13.0`, 224,078 input tokens, about $0.009); scores: `runs/2026-09-22-scores.json`.

**`wrong_char` (is a character written as a different one?) — the better of the two questions**

| Threshold | Learner typos caught | False alarms, SIGHAN "clean" | False alarms, this repo |
|---|---|---|---|
| 0.3 | 82.5% | 31.0% | 13.8% |
| **0.5** | **67.0%** | 12.0% | **2.0%** (3 of 152) |
| 0.7 | 38.0% | 5.0% | 0% |

Ranking ability: typo vs SIGHAN "clean" 0.84; typo vs this repo 0.90. Our own three real typos: 0.96, 0.95, 0.68 (all caught at 0.5; the 金住 sentence is missed at 0.7).

**`any_error` (any typo at all)** is worse on every measure: ranking ability 0.80 / 0.85, and only 51.0% caught at 0.5. It doesn't work for Simplified characters either — in the previous day's pilot it rated a corrected sentence as more suspicious than one containing a Simplified character.

**We checked the 3 flagged repo sentences by hand; none contains a typo**: "你的任務如果是新的…能直接用的是 Jev。", "…不是雜訊/導聯脫落/動作假影嗎？" (假影 is the standard Taiwanese medical-imaging term), "好處是任何現成模型都能用…多半要自己調溫度。"

### Used on the whole repo

The review tool built from these results (`scripts/zh-check/proofread_jev.py`, threshold 0.5) scanned all 677 Chinese sentences in this repo: 16 flagged, each checked by hand — 3 are the deliberately quoted 康燕 and 皮帝 in correction records (correctly caught; those typos are meant to stay), 13 are false alarms (about 1.9%, matching the 2.0% above), and **no missed typo turned up**. The first version of the tool flagged 5 more, because we had deleted source tags like 🔬📚 and left holes that read as typos; keeping the tags made them disappear.

## What this means

💭 **As a non-blocking review tool that asks a person to take a look, a 0.5 threshold holds up**: about 1 false alarm per 50 correct sentences, while catching about two-thirds of learner typos and all three of our own AI-generated ones. It only flags suspicious sentences — it won't tell you the right character, and it shouldn't be used to block anything automatically.

**The division of labour is the one this repo keeps recommending**: Simplified characters go to the deterministic character list (free, never wrong); the narrow feel-for-language judgment of a wrong character goes to Jev; whatever it flags goes to a person.

## Limitations

- **SIGHAN's typos aren't the kind we most want to catch**: they're written by learners of Chinese and are mostly sound-alikes (側/測, 不過/不夠); AI-generated typos look more like shape errors or garbled characters (金住, 康燕). We have only 3 of the latter — not enough to quantify.
- **SIGHAN's "clean" set actually hides unlabelled typos** (e.g. 下課的時侯, 如何減化), and it's learner Chinese that isn't fully fluent to begin with. So its false-alarm rate runs high and is only an upper bound; this repo's sentences are the more reliable negatives.
- This repo's sentences aren't guaranteed 100% correct; we checked every flagged one by hand, but not every unflagged one.
- Sentences containing code spans weren't tested (removing the code leaves holes).
- One call per sentence; no side-by-side comparison with a dedicated Chinese spelling-check model or a large language model.

## Re-running

```
pip install typesafe-sdk --extra-index-url https://pypi.typesafe.ai/
pip install opencc-python-reimplemented huggingface_hub
python run.py --dry-run   # look at each set's sentences first
python run.py             # needs TYPESAFE_API_KEY
python score.py
```

## Tag

🔬 Our own test, real API calls, see `runs/`.
