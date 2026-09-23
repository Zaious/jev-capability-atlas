🇹🇼 中文｜🇬🇧 [English below](#classifying-what-kind-of-utterance-this-is-english)

# 這句是哪一種話：情緒問不出來時的替代形狀

## 這組測什麼

前三組表情 suite 收斂到一個結論：**「說話的人當時是什麼情緒」在文字裡答不出來**。[`suites/expression-japanese/`](../expression-japanese/) 量到的人類天花板是 **0.524**——三個人只看文字猜筆者的心情，只有一半對，因為情緒在**聲音**裡。對 VRChat 這種「自己說話 → 語音轉文字 → 自己的臉」的場景，那條路等於先把答案（語音）刪掉再問答案。

所以這組測**替代形狀**：別問情緒，**問這句是哪一種話**——陳述／提問／要對方做／承諾自己做。言語行為理論上是真的寫在文字裡的，如果成立，就可以由程式把「話的種類」映射成動作（問句→歪頭、請求→前傾、答應→點頭），完全不碰情緒。

**這組是為了證偽我們自己前一則的提議而跑的**：如果它掉進 0.5 那一區，那個替代方案就該被丟掉。

## 最重要的是基準線，不是準確率

DailyDialog 的四類裡，「提問」幾乎等於問號。**光用一條規則——結尾有問號就答提問，否則答最大類別——在這 500 題上就有 0.708。** 所以整體準確率好看沒有意義。

| 基準線（零成本算出來，不打 API） | 值 |
|---|---|
| 最大類別（inform） | 0.454 |
| **標點捷徑** | **0.708** |
| 帶問號的句子（佔 29.0%）真的是提問的比例 | 0.876 |
| **沒有問號的 355 題上，一律答 inform** | **0.639** |

**真正的題目是那 355 題。**

## 結果

`jev-1.13.0`，3,000 次呼叫、0 次錯誤、88.3 秒、1,637,448 input tokens（約 0.069 美元）。暖機 349.4 毫秒不計入。

| 臂 | 全部 500 題 | **沒有問號的 355 題** | 有問號的 145 題 | ECE | 三次都一樣 | p50 / p95 |
|---|---|---|---|---|---|---|
| 這一句＋前四句 | 0.785 | **0.756**（基準 0.639） | 0.858（基準 0.876） | 0.131 | 0.978 | 231 / 293 ms |
| 只給這一句 | 0.755 | **0.701**（基準 0.639） | 0.887（基準 0.876） | 0.140 | 0.990 | 227 / 291 ms |
| 標點捷徑 | 0.708 | — | — | — | — | — |

**脈絡的效果**（配對比較）：全部 **+0.031，95% CI [+0.007, +0.056]**（86 勝 40 敗）；**沒有問號的子集 +0.055，95% CI [+0.024, +0.087]**（83 勝 24 敗）。

**逐類 recall（有脈絡那臂）**：

| 類別 | recall | 最常錯成 |
|---|---|---|
| inform（陳述） | 0.856 | commissive |
| question（提問） | 0.856 | inform |
| **directive（要對方做）** | **0.680** | inform |
| **commissive（承諾自己做）** | **0.477** | inform |

**信心門檻**（有脈絡那臂）：0.9 時覆蓋 68.9%、被覆蓋的準確率 **0.865**。

## 這代表什麼

### 一、替代方案成立，但沒有我們原本說的那麼好

我們原本預測言語行為分類會落在「繁中選表情」那種 **0.8 的區間**。**實際是 0.70–0.76**，介於中間。

但它**確實不是只靠標點**：在沒有問號的 355 題上，0.756 對上「一律 inform」的 0.639——**高出 11.7 分**。所以「這句是哪一種話」比「說話的人什麼心情」**明顯更可讀**（後者連人都只有 0.524），只是沒到我們宣稱的水準。

### 二、弱的正好是有用的那兩類

這是對我們提議最傷的一點。**它最會的是「提問」（0.856）——但那也是一條 regex 就能做到的。** 而真正會驅動有趣動作的兩類：

- **directive（請求／指示／邀請）0.680**
- **commissive（答應／承諾／我來做）0.477**

兩類都往 inform 倒。也就是說，「問句 → 歪頭」這個最好做的映射不需要模型；「請求 → 前傾」「答應 → 點頭」需要模型，而模型在那裡最不準。**提議要照這個修正：別拿四類直接當動作表，先看你想要的動作對應到哪一類，再看那一類的 recall。**

### 三、脈絡在這裡第一次真的買到準確率

前兩組 suite 的結論是「脈絡買到的是校準，不是準確率」（兩次的準確率 CI 都幾乎或確實跨零）。這一組不一樣：**沒有問號的子集上 +0.055，95% CI [+0.024, +0.087]，83 勝 24 敗——乾淨地不含零。**

💭 合理的解釋：言語行為**本來就是相對於前一句定義的**。「明天可以嗎」是提問還是答應，取決於上一句是不是在邀約。情緒不是這樣——情緒在說話者身上，不在回合關係裡。所以脈絡對這個任務是**必要資訊**，對情緒任務只是**額外線索**。這條也給前兩組的結果一個更好的解釋。

### 四、門檻閘在這裡好用

0.9 門檻覆蓋 68.9%、準確率 0.865。三次重問給同一答案的比例 0.978–0.990，是我們四組表情相關 suite 裡最穩的。做產品的話這是可用的形狀：**高信心的七成驅動動作，其餘用預設或維持上一個。**

## 限制

- **沒有人類天花板。** DailyDialog 只發布每句一個標籤，不是逐標註者的，所以不像 [`suites/expression-japanese/`](../expression-japanese/) 能說「離人多遠」。0.756 是高是低，我們**沒有辦法判斷**。
- **四類太粗，不是動作表。** 真正要驅動表情的是更細的言語行為（道歉、打招呼、附和、玩笑、驚訝的反應），DailyDialog 沒有標。把這組的數字直接當成「動作分類可行性」會高估。
- **英文、日常情境對話**。VRChat 的語音轉文字會有辨識錯誤、口語省略、沒有標點——**這組沒有測那個**（我們之前引用過的 NPC 那筆顯示，逐字稿變髒時 F1 從 0.96 掉到 0.93，但那是另一個任務）。
- **問號子集上有脈絡反而略差**（0.858 對 0.887），樣本只有 145 題，可能是雜訊，但沒有再測。
- 單一 run date、單一模型版本。延遲從台灣量，含網路往返。

## 這組跑的時候撞到的一個坑（跟 Jev 無關，但會擋住所有人）

開跑當下**每一次呼叫**都死在 `TypeError: process() takes no keyword arguments`，看起來像 API 掛了。實際是用戶端解壓縮的版本相撞：伺服器回 brotli 壓縮，而 `httpx2` 2.13.0 的 brotli 路徑呼叫 `decompressor.process(data, output_buffer_limit=...)`，`brotli` 1.1.0 的 `process()` 不吃關鍵字參數。

修法是不要宣告 `br`：[`scripts/common/jev_client.py`](../../scripts/common/jev_client.py) 現在一律帶 `Accept-Encoding: gzip`，所有 suite 都跟著修好。代價只是回應大一點。

## 資料與授權

**語料原文不在這個 repo 裡。** DailyDialog 是 **CC BY-NC-SA 4.0**；`data/cases.json` 與 `data/_cache/` 都 gitignored，**收據存的是每個 state 的 SHA-256**。NonCommercial 與 ShareAlike 約束的是跑這支 suite 去下載語料的人，不是本 repo 的 MIT 程式碼。

引用：Li et al., *DailyDialog: A Manually Labelled Multi-turn Dialogue Dataset*, IJCNLP 2017。

```bash
python data/build_cases.py --stats                         # 基準線（含標點捷徑），不打 API
python data/build_cases.py --verify runs/2026-09-23.json   # 3000 receipts, 0 hash mismatches
python score.py --check                                    # 從收據重算，數字對不上就 exit 1
```

## 怎麼重跑

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run
python run.py               # 3,000 次呼叫
python score.py
```

## 標籤

🔬（我們自己打 API 測的；原始回應在 [`runs/`](runs/)。標準答案是 DailyDialog 的原始標註。）

---

# Classifying what kind of utterance this is (English)

## What this measures

The three expression suites converged on one conclusion: **"what was the speaker feeling" cannot be answered from text**. [`suites/expression-japanese/`](../expression-japanese/) measured the human ceiling at **0.524** — three people reading only the text guess the writer's feeling right half the time, because the feeling is in the **voice**. For a VRChat-shaped pipeline (you speak → speech-to-text → your own avatar's face), that route deletes the answer and then asks for it.

So this suite tests the **alternative shape**: don't ask about emotion, ask **what kind of utterance this is** — inform, question, directive, commissive. Speech acts should be genuinely present in the text; if so, code can map the act onto a gesture (question → head tilt, request → lean in, agreement → nod) without touching emotion at all.

**This suite exists to falsify our own previous proposal.** If it landed in the 0.5 range, that proposal deserved to be dropped.

## The baseline matters more than the accuracy

In DailyDialog's four acts, "question" is nearly synonymous with a question mark. **A single rule — ends with "?" then question, otherwise the majority class — already scores 0.708 on these 500 items.** So overall accuracy looks good and means little.

| Baseline (computed offline, no API calls) | Value |
|---|---|
| Majority class (inform) | 0.454 |
| **Punctuation shortcut** | **0.708** |
| Of utterances that carry "?" (29.0%), share actually labelled question | 0.876 |
| **On the 355 items with no question mark, always-inform** | **0.639** |

**The real test is those 355 items.**

## Results

`jev-1.13.0`; 3,000 calls, 0 errors, 88.3 s, 1,637,448 input tokens (about $0.069). Warm-up 349.4 ms, excluded.

| Arm | All 500 | **355 without "?"** | 145 with "?" | ECE | Same answer ×3 | p50 / p95 |
|---|---|---|---|---|---|---|
| Line + 4 turns | 0.785 | **0.756** (baseline 0.639) | 0.858 (baseline 0.876) | 0.131 | 0.978 | 231 / 293 ms |
| Line only | 0.755 | **0.701** (baseline 0.639) | 0.887 (baseline 0.876) | 0.140 | 0.990 | 227 / 291 ms |
| Punctuation shortcut | 0.708 | — | — | — | — | — |

**Effect of context** (paired): overall **+0.031, 95% CI [+0.007, +0.056]** (86 won, 40 lost); on the no-question-mark subset **+0.055, 95% CI [+0.024, +0.087]** (83 won, 24 lost).

**Per-class recall** (context arm):

| Class | Recall | Most often mistaken for |
|---|---|---|
| inform | 0.856 | commissive |
| question | 0.856 | inform |
| **directive** (get the other person to act) | **0.680** | inform |
| **commissive** (commit yourself) | **0.477** | inform |

**Confidence threshold** (context arm): at 0.9 it covers 68.9% at **0.865** accuracy.

## What this means

### 1. The alternative works, but not as well as we claimed

We predicted speech-act classification would land in the **0.8 band** that Chinese expression selection reached. **It lands at 0.70–0.76** — in between.

It is genuinely **not just punctuation**, though: on the 355 items with no question mark it scores 0.756 against always-inform's 0.639, **11.7 points clear**. So "what kind of utterance is this" is **substantially more readable** than "what was the speaker feeling" (which people manage at only 0.524) — just not at the level we asserted.

### 2. The weak classes are exactly the useful ones

This is the most damaging part for our proposal. **What it does best is question (0.856) — which a regex already does.** The two classes that would drive interesting gestures are the weak ones:

- **directive** (request / instruction / invitation): **0.680**
- **commissive** (accepting / promising / offering): **0.477**

Both collapse into inform. So "question → head tilt", the easiest mapping, needs no model; "request → lean in" and "agreement → nod" need the model, and that is where the model is weakest. **The proposal should be corrected accordingly: don't treat the four acts as a gesture table — look up which act your intended gesture maps to, then look at that act's recall.**

### 3. Context bought accuracy here, for the first time

The previous suites concluded that context buys calibration rather than accuracy (both accuracy CIs nearly or actually crossed zero). Not here: **on the no-question-mark subset it is +0.055, 95% CI [+0.024, +0.087], 83 won to 24 lost — cleanly excluding zero.**

💭 A plausible reason: a speech act **is defined relative to the previous turn**. "Would tomorrow work?" is a question or an acceptance depending on whether the previous line was an invitation. Emotion isn't like that — it lives in the speaker, not in the relation between turns. So context is *required information* for this task and merely *extra evidence* for the emotion tasks. That also explains the earlier results better than we did at the time.

### 4. The threshold gate is usable here

At 0.9 it covers 68.9% at 0.865 accuracy, and it gives the same answer across all three repeats 97.8–99.0% of the time — the steadiest of our four expression-related suites. That is a shippable shape: **drive gestures from the confident 70%, and default or hold for the rest.**

## Limitations

- **No human ceiling.** DailyDialog publishes one label per utterance, not per annotator, so unlike [`suites/expression-japanese/`](../expression-japanese/) there is no way to say how far from a person this sits. Whether 0.756 is good, we **cannot judge**.
- **Four classes is too coarse to be a gesture table.** What would actually drive a face is finer acts — apology, greeting, backchannel, joke, surprise reaction — which DailyDialog does not label. Reading these numbers as "gesture classification is feasible" overstates them.
- **English, everyday scripted conversation.** VRChat speech-to-text brings recognition errors, elision and no punctuation, and **this suite does not test that** (the NPC-addressing result we cite elsewhere dropped from F1 0.96 to 0.93 on messy transcripts, but that is a different task).
- **On the question-marked subset, context is slightly worse** (0.858 against 0.887). Only 145 items, so this may be noise; we did not investigate further.
- One run date, one model build. Latency measured from Taiwan, including the network round trip.

## A trap we hit on this run (nothing to do with Jev, but it will block anyone)

At the start, **every call** died with `TypeError: process() takes no keyword arguments`, which looks like an API outage. It is a client-side decoder version clash: responses came back brotli-encoded, and `httpx2` 2.13.0's brotli path calls `decompressor.process(data, output_buffer_limit=...)` while `brotli` 1.1.0's `process()` takes no keyword arguments.

The fix is to stop advertising `br`: [`scripts/common/jev_client.py`](../../scripts/common/jev_client.py) now always sends `Accept-Encoding: gzip`, which fixes it for every suite. The only cost is slightly larger responses.

## Data and licensing

**The corpus text is not in this repository.** DailyDialog is **CC BY-NC-SA 4.0**; `data/cases.json` and `data/_cache/` are gitignored and **the receipts store the SHA-256 of each state**. The NonCommercial and ShareAlike terms bind whoever downloads the corpus by running this suite, not this repository's MIT-licensed code.

Citation: Li et al., *DailyDialog: A Manually Labelled Multi-turn Dialogue Dataset*, IJCNLP 2017.

```bash
python data/build_cases.py --stats                         # baselines incl. the punctuation shortcut, no API calls
python data/build_cases.py --verify runs/2026-09-23.json   # 3000 receipts, 0 hash mismatches
python score.py --check                                    # recomputes from receipts; exit 1 on drift
```

## Reproducing

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run
python run.py               # 3,000 calls
python score.py
```

## Tag

🔬 (our own API calls; raw responses in [`runs/`](runs/). The gold labels are DailyDialog's original annotation.)
