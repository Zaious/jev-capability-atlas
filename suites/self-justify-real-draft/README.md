🇹🇼 中文｜🇬🇧 English below

# 真實稿件裡的「替作者辯護」：先導測試

> **這是先導測試**：正例只有 7 個，只能看方向，不能下結論。第二輪（整節＋讀者設定）的結果見[下方](#第二輪整節內文讀者設定八個維度)。

## 這組測什麼

前一組 [`suites/self-justify-detection/`](../self-justify-detection/) 的主要結論已撤回：我們照判準字面自己編的題目，判準作者看了覺得都是正當說明，不像真實的 AI 味。作者指出真實常見的情況是：**跟 LLM 來回討論、自己內心轉折的過程，最後被織進文章裡，讀者其實不需要知道。**

這組改用真實稿件。標籤不是我們判斷的，是**作者實際的刪改動作**：維護者自己的一篇論文 `danganronpa-persona-2026`（ACGCT 2026，單盲審查），從 AI 協作底稿到投稿正本共 35 次修改、91 處逐句變動。其中大多數是聲紋修正（冒號改逗號、「你」改「使用者」）或引用修正；**有 7 處刪掉的是同一種東西**。

看過這 7 處與作者保留下來的相似句之後，作者確認了兩者的差別：**留下的在告訴讀者這個主張該怎麼讀（範圍在哪、這個詞是什麼身份）；刪掉的在處理別人會怎麼看作者**（「免得看起來像把好幾套理論硬疊在一起」「不是他讀過這篇論文後的回應」）。

## 方法論

34 題，每題的 state 是「所在段落＋要判斷的句子」：

| 組 | 內容 | 題數 |
|---|---|---|
| 刪掉的（正例）| 作者刪掉或從句中拿掉的部分，取刪前那一版的原句 | 7 |
| 長得像但留下的 | 限定範圍、交代術語身份、預先回應反對意見、AI 使用揭露、說明數字落差——作者逐句核對後保留到正本；包括 P5、P6 被刪之後**留下來的那一半限定** | 7 |
| 原封不動的 | 從 AI 協作底稿一路沒被動過、留到正本的句子，種子 29 隨機抽 | 20 |

兩個 Jev 問法，各問三次、分開請求：

- **判準**：babel-antiai 的 SELF-JUSTIFY 判準逐字（同前一組）。
- **作者對讀者**：作者今天確認的那條區分——「有沒有句子或子句在處理別人會怎麼看作者，而不是告訴讀者這個主張該怎麼讀」。**這個問法是看過這批例子之後寫的，屬於樣本內**，對它有利。

另外用 babel-antiai 的確定性掃描器掃每一句（掃描器有長度下限，34 句中 11 句太短被略過）。資料與方法在執行前以 commit `c8bab45` 凍結推上。

## 結果

收據：`runs/2026-09-23.json`（204 次呼叫、0 失敗，`jev-1.13.0`，130,836 input tokens）、`runs/2026-09-23-scanner.json`；評分：`runs/2026-09-23-scores.json`（`score.py --check` 可重算）。

| | 刪掉的 7 | 長得像但留下的 7 | 原封不動的 20 | 刪掉的 vs 留下的相似句（AUC）|
|---|---|---|---|---|
| 判準・門檻 0.5 | 6 | 5 | **9** | 0.56 |
| 作者對讀者・門檻 0.5 | 5 | 5 | **0** | 0.59 |
| 作者對讀者・門檻 0.7 | 4 | 2 | 0 | — |
| 掃描器（能掃的 23 句）| 0 | 0 | 0 | — |

平均分數：判準 0.63／0.60／0.47，**所有句子都擠在 0.5 附近**；作者對讀者 0.62／0.58／**0.10**。

逐題看「作者對讀者」：

- 抓得到的刪除：「免得看起來像把好幾套理論硬疊在一起」0.86、「不是真的在猜測時間旅行」0.80、「不是他讀過這篇論文後的回應」0.74、「不是他對這篇論文的評論或背書」0.71。
- 漏掉的刪除：**「我把界線劃清楚了，這兩層各自的份量，讀者可以自行判斷」0.40**（作者最典型的一處），以及「那位（並不是未來人的）小高和剛」0.24。
- 被誤判的保留句：「這不是一篇要證明《槍彈辯駁》預言了 AI 的文章」0.78、「這不是說專才型代理天生就優於通才型代理……而是說」0.76。判對的保留句：術語身份的括號說明 0.20。

## 這代表什麼

💭 **這條線，Jev 目前分不出來。**「作者對讀者」這個問法能把「在談主張本身或作者自己的句子」從一般句子裡挑出來（原封不動的 20 句全部低於 0.41、平均 0.10），但在這一群裡面，**分不清哪句是護著作者、哪句是在引導讀者**（AUC 0.59，7 對 7）。從逐題分數看，它對的是**形狀**——「不是 X」這種否定式澄清不管功能是什麼都拿高分；沒有這個形狀的自我交代（「我把界線劃清楚了」）反而漏掉。這跟前一組撤回後剩下的結論一致：判準的關鍵在功能，功能靠的是作者心裡那套沒寫出來的判斷。

💭 **但它可以當第一道篩子。** 用「作者對讀者」問法、門檻 0.5，34 句縮成 10 句待看，7 處刪除抓到 5 處，一般句子零誤報；剩下的由人判斷。原本的判準問法連這一步都做不到（一般句子也誤報 9 句）。

**掃描器在真實稿件上一處都沒抓到**，包括「免得看起來像……」這種明顯的一句——它的五種形狀是從一封信反推出來的，沒涵蓋這篇的寫法。

## 第二輪：整節內文＋讀者設定＋八個維度

**為什麼**：第一輪只給 Jev 一段。「這個解釋是否多餘」的答案大多不在那一段裡——要看讀者是誰、前文說過什麼、這句在幫哪個主張。第二輪把這些放進 state：**整節內文（要判斷的句子用【【】】標出）＋一行讀者設定**（ACGCT 2026 的審稿人與與會者：熟動漫遊戲與角色設計、不一定熟 AI 代理）。一次請求問八個維度，同樣 34 題、各三次。**不做兩版比較**：實際辨識時手上只有一份稿。

**事先凍結**（commit `f16087e`）：讀者設定、八題問法、**組合規則（八維方向對齊後等權平均，不在這 34 題上擬合任何權重）**，以及每題輸入的 sha256。整節內文加起來接近整篇論文，超出作者同意公開的「部分段落」，所以第二輪的收據**不存內文**，只存節名、來源 commit 與雜湊；`run_round2.py` 重建的輸入跟雜湊對不上就拒跑。

收據：`runs/2026-09-23-round2.json`（102 次呼叫、0 失敗，`jev-1.13.0`，236,583 input tokens）；評分：`runs/2026-09-23-round2-scores.json`（`score_round2.py --check` 可重算）。

| 維度 | 刪掉的 vs 保留的相似句（AUC）| 刪掉的 vs 全部保留的（AUC）| 平均：刪／相似／未動 |
|---|---|---|---|
| **overall：以這位讀者來看是不必要的解釋** | **0.898** | **0.966** | 0.40／0.33／0.30 |
| needed_later（反向）：刪掉後文會看不懂 | 0.694 | 0.847 | |
| preempt：預先澄清作者不是那個意思 | 0.663 | 0.902 | 0.89／0.80／0.26 |
| about_author：在談作者自己 | 0.541 | 0.876 | 0.66／0.62／0.13 |
| process：在交代寫作過程 | 0.531 | 0.844 | |
| guides_reading（反向）／repeated／reader_knows | 0.49–0.53 | 0.19–0.46 | |
| **事先寫死的等權組合** | **0.674** | **0.915** | |

- **`overall` 在有整節與讀者設定後，把刪與留分開了**：34 句依分數排序，**前四名全是作者刪掉的**（「免得看起來像把好幾套理論硬疊在一起」0.51、「我把界線劃清楚了……讀者可以自行判斷」0.45、「不是他讀過這篇論文後的回應」0.42、「不是真的在猜測時間旅行」0.39），第五名才是保留的「這不是一篇要證明……的文章」0.38；所有未動句都在 0.36 以下。第一輪漏掉的那句「我把界線劃清楚了」從 0.40 升到第二名。三次重問的標準差中位 0.005，排序是穩的。
- **但分數整體偏低、擠在一起**（0.25–0.51），門檻 0.5 只會標出 1 句。它提供的是**排序**，不是可以直接設門檻的機率。
- **`preempt`（預先澄清）照樣是形狀偵測器**：刪掉的 7/7、保留的 6/7 都過 0.5——跟第一輪一樣，它認得「不是 X」的形狀，不認得功能。
- **事先寫死的等權組合只有 0.674**：幾個維度沒有資訊（repeated、reader_knows 在 0.49 左右），甚至反向（guides_reading 對一般句子給得更高），把組合拖了下來。

💭 **這一輪能說的**：給足上下文之後，**直接問「以這位讀者來看是不是不必要」**比拆成子題更有用——跟我們原本的建議（拆成原子題再用程式組合）相反。實務上的用法是**排序**：「列出這篇最可能不必要的前幾句給作者看」；在這篇稿子上，前五名有四句是作者真的刪掉的。

**但這是八個維度裡最好的一個**，而事先寫死的是組合；從八個裡挑出最好的那一個再報，本身就會高估。`overall` 的 0.898 要在新的稿子上重現才算數——這正是改寫存底要累積的資料。

## 限制

1. **正例只有 7 個、相似反例 7 個**，AUC 的差別在這個樣本量下沒有意義。這組只說方向。
2. **「作者對讀者」問法是看過這些例子才寫的**（樣本內），而它仍然分不出來——這一點是可信的；如果它分得出來，反而要打折。
3. **標籤來自作者的刪改**：刪掉的一定是作者不要的；留下的「相似句」是作者逐句核對後保留的，但不排除只是沒注意到。原封不動的句子更可能只是沒被注意。
4. **單一篇論文、單一作者**，而且是學術寫作。其他文類（部落格、信件、報告）的樣子可能不同。
5. 題目摘自作者自己的稿件，經作者同意公開；著作權屬於作者，不適用本 repo 的 MIT 授權。

## 怎麼跑

```bash
python run.py --dry-run
python run.py                          # 需要 TYPESAFE_API_KEY
BABEL_ANTIAI_SCAN=<path> python baseline_scan.py
python score.py                        # --check 重算並比對
CHRONICLE_LEX=<path> python data/build_cases.py   # 重建題目，需要作者的私人 repo；一般不必
```

## 標籤

🔬（我們自己跑的；收據在 `runs/`）

---

# "Defending the author" in a real draft: a pilot (English)

> **This is a pilot**: seven positives only. Direction, not conclusions. Round 2 (whole section + reader profile) is [below](#round-2-whole-section--reader-profile--eight-dimensions).

## What this tests

The main conclusion of [`suites/self-justify-detection/`](../self-justify-detection/) was withdrawn: the items we wrote from the criterion's literal wording were, in its author's view, legitimate explanations, not real AI-flavoured writing. The author points to the common real case: **the process of deliberating with an LLM, and one's own changes of mind, woven into the finished article when the reader doesn't need it.**

So this pilot uses a real draft, and the labels aren't our judgment but **what the author actually cut**: the maintainer's own paper `danganronpa-persona-2026` (ACGCT 2026, single-blind), 35 revisions and 91 sentence-level changes from the AI-assisted draft to the submitted version. Most were voice fixes (colons to commas, "you" to "users") or citation fixes; **seven removed the same kind of thing**.

Having seen those seven next to the similar sentences the author kept, the author confirmed the difference: **the kept ones tell the reader how to read the claim (its scope, the status of a term); the cut ones manage how others will see the author** ("so it doesn't look like several theories piled together," "not a response to him having read this paper").

## Method

34 cases; each state is "the paragraph + the sentence to judge":

| Group | Content | n |
|---|---|---|
| Cut (positive) | what the author cut or removed from a sentence, in its pre-cut version | 7 |
| Kept look-alikes | scoping, term status, anticipating objections, AI-use disclosure, explaining a number — kept after sentence-by-sentence review; includes **the half of the P5/P6 hedge that survived** | 7 |
| Unchanged | sentences untouched from the AI-assisted draft to submission, sampled with seed 29 | 20 |

Two Jev wordings, three repeats each, separate requests:

- **Criterion**: babel-antiai's SELF-JUSTIFY test, verbatim (as in the previous suite).
- **Author vs reader**: the distinction the author confirmed today — "is any sentence or clause managing how others will see the author, rather than telling the reader how to read the claim?" **This wording was written after seeing these cases, so it's in-sample** and favoured.

babel-antiai's deterministic scanner was also run on each sentence (it has a length floor; 11 of 34 were too short and skipped). Data and method were frozen and pushed in commit `c8bab45` before running.

## Results

Receipts: `runs/2026-09-23.json` (204 calls, 0 failures, `jev-1.13.0`, 130,836 input tokens) and `runs/2026-09-23-scanner.json`; scores: `runs/2026-09-23-scores.json` (`score.py --check` recomputes).

| | Cut (7) | Kept look-alikes (7) | Unchanged (20) | Cut vs kept look-alikes (AUC) |
|---|---|---|---|---|
| Criterion, threshold 0.5 | 6 | 5 | **9** | 0.56 |
| Author vs reader, threshold 0.5 | 5 | 5 | **0** | 0.59 |
| Author vs reader, threshold 0.7 | 4 | 2 | 0 | — |
| Scanner (23 scannable) | 0 | 0 | 0 | — |

Mean scores: criterion 0.63 / 0.60 / 0.47, **everything crowded around 0.5**; author vs reader 0.62 / 0.58 / **0.10**.

Case by case, author vs reader:

- Cuts it caught: "so it doesn't look like several theories piled together" 0.86, "not really speculating about time travel" 0.80, "not a response to him having read this paper" 0.74, "not his comment on or endorsement of this paper" 0.71.
- Cuts it missed: **"I've drawn the line clearly; readers can judge the weight of each layer" 0.40** (the author's most typical case) and "that (not-a-time-traveller) Kodaka" 0.24.
- Kept sentences it got wrong: "This is not an article trying to prove that Danganronpa predicted AI" 0.78, "This isn't to say specialist agents are inherently better than generalists... but that" 0.76. Kept sentence it got right: the parenthetical on a term's status, 0.20.

## What it means

💭 **Jev can't draw this line yet.** The author-vs-reader wording picks out "sentences about the claim itself or about the author" from ordinary ones (all 20 unchanged sentences under 0.41, mean 0.10), but within that group **it can't tell which ones protect the author and which guide the reader** (AUC 0.59, 7 vs 7). The case scores suggest it responds to **shape**: a "this is not X" disclaimer scores high whatever its function, while a self-account without that shape ("I've drawn the line clearly") is missed. That matches what survived the previous suite's withdrawal: the test turns on function, and function rests on judgment the author carries and never writes down.

💭 **It does work as a first filter.** With the author-vs-reader wording at 0.5, 34 sentences narrow to 10 for a person to review, catching 5 of the 7 cuts with no false alarms among ordinary sentences. The criterion wording can't do even that (9 false alarms among ordinary sentences).

**The scanner caught nothing in the real draft**, not even the obvious "so it doesn't look like..." — its five shapes were reverse-engineered from one letter and don't cover how this paper was written.

## Round 2: whole section + reader profile + eight dimensions

**Why**: round 1 gave Jev one paragraph. Whether an explanation is unnecessary mostly isn't answerable from that paragraph — it depends on who the reader is, what the section has already said, and which claim the sentence serves. Round 2 puts those in the state: **the whole section (the sentence marked with 【【】】) plus a one-line reader profile** (ACGCT 2026 reviewers and attendees: know ACG and character design, not necessarily AI agents). Eight dimensions in one request, same 34 cases, three repeats. **No two-version comparison**: in real use there is only one draft.

**Frozen beforehand** (commit `f16087e`): the reader profile, the eight questions, **the combination rule (direction-aligned equal-weight mean of the eight, no weights fitted on these 34 cases)**, and each input's sha256. The sections together come close to the whole paper, beyond the "partial paragraphs" the author agreed to publish, so round-2 receipts **store no text**, only section, source commit and hash; `run_round2.py` refuses to run if a rebuilt input doesn't match.

Receipts: `runs/2026-09-23-round2.json` (102 calls, 0 failures, `jev-1.13.0`, 236,583 input tokens); scores: `runs/2026-09-23-round2-scores.json` (`score_round2.py --check` recomputes).

| Dimension | Cut vs kept look-alikes (AUC) | Cut vs all kept (AUC) | Mean: cut / look-alike / unchanged |
|---|---|---|---|
| **overall: unnecessary for this reader** | **0.898** | **0.966** | 0.40 / 0.33 / 0.30 |
| needed_later (reversed): later text breaks without it | 0.694 | 0.847 | |
| preempt: pre-empting that the author meant something else | 0.663 | 0.902 | 0.89 / 0.80 / 0.26 |
| about_author: about the author, not the argument | 0.541 | 0.876 | 0.66 / 0.62 / 0.13 |
| process: recounting the writing process | 0.531 | 0.844 | |
| guides_reading (reversed) / repeated / reader_knows | 0.49–0.53 | 0.19–0.46 | |
| **Pre-registered equal-weight combination** | **0.674** | **0.915** | |

- **With the whole section and a reader profile, `overall` separates cut from kept**: ranking all 34 sentences by it, **the top four are all sentences the author cut** ("so it doesn't look like several theories piled together" 0.51, "I've drawn the line clearly... readers can judge" 0.45, "not a response to him having read this paper" 0.42, "not really speculating about time travel" 0.39); fifth is the kept "This is not an article trying to prove..." 0.38; every unchanged sentence is under 0.36. The round-1 miss "I've drawn the line clearly" rises from 0.40 to second place. The median standard deviation across three repeats is 0.005; the ordering is stable.
- **But the scores are low and compressed** (0.25–0.51); a 0.5 threshold flags one sentence. What it gives is a **ranking**, not a probability you can threshold directly.
- **`preempt` is still a shape detector**: 7/7 cut and 6/7 kept over 0.5 — as in round 1, it recognises the "this is not X" shape, not the function.
- **The pre-registered equal-weight combination is only 0.674**: several dimensions carry no information (repeated, reader_knows around 0.49) or point the wrong way (guides_reading scores ordinary sentences higher), and they drag the combination down.

💭 **What this round supports**: once the context is there, **asking directly "is this unnecessary for this reader"** works better than splitting it into sub-questions — the opposite of what we had suggested (atomic questions combined in code). In practice the use is **ranking**: "list the sentences in this draft most likely to be unnecessary, for the author to look at"; on this draft, four of the top five are sentences the author actually cut.

**But it is the best of eight dimensions**, and what was pre-registered was the combination; reporting the best of eight overstates it by construction. `overall`'s 0.898 only counts once it replicates on new drafts — which is what the rewrite ledger is now accumulating.

## Limitations

1. **Seven positives and seven look-alikes**: the AUC difference means nothing at this size. Direction only.
2. **The author-vs-reader wording was written after seeing these cases** (in-sample) and still couldn't separate them — that part is credible; had it separated them, it would need discounting.
3. **Labels come from the author's edits**: a cut is certainly unwanted; a kept look-alike survived sentence-by-sentence review but may simply have gone unnoticed, and unchanged sentences even more so.
4. **One paper, one author**, academic writing. Other genres (blog posts, letters, reports) may look different.
5. The excerpts are from the author's own manuscript, published with the author's permission; copyright stays with the author and they're not under this repo's MIT license.

## How to run

```bash
python run.py --dry-run
python run.py                          # needs TYPESAFE_API_KEY
BABEL_ANTIAI_SCAN=<path> python baseline_scan.py
python score.py                        # --check recomputes and compares
CHRONICLE_LEX=<path> python data/build_cases.py   # rebuild cases; needs the author's private repo, normally unnecessary
```

## Tag

🔬 (run by us; receipts in `runs/`)
