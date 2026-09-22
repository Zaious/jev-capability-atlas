🇹🇼 中文｜🇬🇧 [English below](#expressions-across-a-whole-dialogue-english)

# 整段對話裡的表情：聆聽表情與跨句換臉

## 這組測什麼

[`suites/expression-selection/`](../expression-selection/) 量的是「一句話配一個表情」。做 AI VTuber 或虛擬角色的人接著會撞到的是另外兩件事，而那兩件只有在**一整段對話**裡才看得到：

1. **聆聽表情**：A 說了這句，**聽的人 B** 該擺什麼臉？（AnimeAct Engine 的宣傳特別提到它同時決定說話表情與聆聽表情。）
2. **跨句換臉的頻率**：同一個角色連續講好幾句，表情換太頻繁在畫面上比選錯還明顯。

所以這組改抽**整段對話、照順序全拿**：MELD 測試集裡 192 段至少 6 句的對話，抽 30 段，357 句全部跑過，**六臂**、每題重問 3 次，兩批共 4,566 次呼叫（前四臂 3,516 次；後兩臂「給聽者狀態」1,050 次，另存一份收據）。說話者那兩臂的問法跟前一組**一字不差**，兩邊才比得起來。

**聆聽表情沒有現成的標準答案**——MELD 標的是說話者的情緒，不是聽者的表情。我們用的代理答案是：**聽者自己緊接著那一句的情緒標籤**（只取換人說話的相鄰配對）。那是別人標的、不是我們編的，但它是代理，限制寫在下面。

## 結果

`jev-1.13.0`，兩批合計 4,566 次呼叫、0 次錯誤、151.3 秒、3,092,046 input tokens（約 0.13 美元）。兩次暖機（845.8 與 775.9 毫秒）都不計入。

**這組是自然分布**（標準答案有 45.9% 是 neutral），不是前一組的平衡抽樣。所以該對照的是「一律中性」那條基準線，不是亂猜的 1/7。

| 臂 | 準確率 | 一律中性 | ECE | 平均信心 | 預測中性的比例 | 三次都一樣 |
|---|---|---|---|---|---|---|
| 說話者＋前四句 | **0.669** | 0.459 | **0.050** | 0.687 | 0.550 | 0.978 |
| 說話者，只給這一句 | 0.639 | 0.459 | 0.119 | 0.755 | 0.631 | 0.964 |
| **聆聽＋前四句** | **0.431** | **0.437** | 0.179 | 0.573 | 0.498 | 0.934 |
| **聆聽，只給這一句** | **0.403** | **0.437** | 0.249 | 0.652 | 0.684 | 0.961 |
| 聆聽＋前四句＋**聽者的完美情緒追蹤** | **0.432** | 0.429 | 0.220 | 0.632 | — | — |
| 聆聽＋前四句＋聽者說過的話（不給情緒） | 0.404 | 0.429 | 0.203 | 0.562 | — | — |

延遲六臂都在 p50 約 256 毫秒、p95 約 320–334 毫秒。

後兩列只跑得了「聽者在這段對話裡已經說過話」的 175 題（229 題中的 76%），所以同一批題目上 `聆聽＋前四句` 是 0.432、「一律中性」是 0.429——三者實質打平。

**跨句換臉**（同一段對話、同一個角色，連續兩句之間換掉表情的比例，273 次機會）：

| | 換臉率 |
|---|---|
| 標準答案（這 30 段對話） | 0.509 |
| 說話者＋前四句 | **0.492** |
| 說話者，只給這一句 | **0.498** |

**脈絡的效果**（配對比較，只算真的有前文的題目）：說話者 **+0.038，95% CI [−0.003, +0.075]**（86 勝 49 敗）；聆聽 +0.031，95% CI [−0.039, +0.093]（80 勝 61 敗）。**兩個信賴區間都跨過零。**

**把聽者狀態加進去的效果**（同一批 175 題配對比較）：

| 比較 | 準確率差 | 95% CI | 逐題 |
|---|---|---|---|
| 完美情緒追蹤 vs 只有脈絡 | **+0.000** | [−0.069, +0.067] | 61 勝 61 敗 |
| 完美情緒追蹤 vs 只給聽者說過的話 | +0.029 | [−0.027, +0.084] | 51 勝 36 敗 |
| 只給聽者說過的話 vs 只有脈絡 | −0.029 | [−0.074, +0.017] | 23 勝 38 敗 |

## 這代表什麼

### 一、聆聽表情不成立——這推翻了我們自己先前的判斷

我們原本預期聆聽表情會落在核心軸**自足**的那一側，理由聽起來很合理：觸發它的線索就在對方剛說的那句話裡，而那句話就在 `state` 裡。**實測是反的**：兩臂都**打不過「一律中性」**（0.403 與 0.431 對上 0.437），而且校準很差（ECE 0.179–0.249）。

行為層面的解釋比分數更清楚：**它有 50.8%（無脈絡）到 53.6%（有脈絡）的時候，直接回答說話者自己的情緒**——也就是**照鏡子**。這個觀察不依賴我們的代理答案，是直接從回答數出來的。

為什麼？因為**聽者的反應不是那句話的函數，是那句話對那個聽者的意義的函數**——而那需要聽者的目標、兩人的關係、之前發生過什麼。那些不在 `state` 裡。同一句「你昨天為什麼沒來」，對欠人情的人和對被放鴿子的人，表情完全不同。**這是核心那條軸，不是模型不行。**

**要做聆聽表情，解法不是換問法，是把聽者的狀態放進 `state`**——聽者當下的情緒、關係階段、在意什麼。這正是 [jingx8885/lov-evo](https://github.com/jingx8885/lov-evo) 那個實作在做的事（它把角色自己的 `self_emotion` 與關係帳本組進去），而且它有一條設計註記值得抄：**「使用者的情緒是輸入，不是她要鏡像的目標」**——我們這組數字正好量出了不這樣做會發生什麼：它就是會去鏡像。

### 一之二、給它一個完美的角色情緒追蹤器，一分都沒有進步

上面那節的結論是「要做聆聽表情就得把聽者的狀態放進 `state`」。**我們直接測了這句話，而它是錯的。**

作法是給它一個**比任何產品都好的**聽者狀態：聽者在這段對話裡自己說過的最後兩句，**連同人工標註的情緒標籤**。那等於模擬一個**完美的**角色情緒追蹤器——真實系統只會比這差。結果：

- **準確率 0.432，對上同一批題目的「一律中性」0.429 與「只有脈絡」的 0.432——三者實質打平。**
- 配對比較 **+0.000，95% CI [−0.069, +0.067]，逐題 61 勝 61 敗。** 不是效果小，是剛好零。
- 只給聽者說過的話、不給情緒標籤，反而略低（0.404）。

**但真正說明問題的是它的行為變化**：

| | 回答＝說話者的情緒 | 回答＝聽者自己上一句的情緒 |
|---|---|---|
| 只有脈絡 | 53.6% | — |
| 加上完美情緒追蹤 | 43.8% | **72.0%** |

**它沒有開始推理，它只是換了一個東西抄。** 沒給聽者狀態時抄說話者的情緒，給了之後就抄聽者的情緒（72%）——而「照抄聽者上一句的情緒」這條啟發式本身在整個語料上只有 0.4145，**比「一律中性」的 0.4739 還差**。所以把狀態放進 `state` 不但沒救，還把它錨在一個更差的捷徑上。

💭 這件事的推論不是「角色情緒追蹤沒用」，而是**追蹤到的狀態應該由你的程式直接驅動表情，不是丟進 state 再問模型**。[jingx8885/lov-evo](https://github.com/jingx8885/lov-evo) 正好是這樣做的——它的 `avatar.DriveWithRelationship` 是**程式**把角色自己的情緒、steering mode 與關係階段映射成表情，Jev 只負責判斷使用者那一輪的情緒。我們這組數字是那個設計的獨立佐證：**你手上已經有的那個狀態，直接用；不要再問模型一次「那他現在該是什麼表情」。**

### 二、說話者的表情在自然分布上站得住

0.639 到 0.669，比「一律中性」的 0.459 高 18 到 21 分。這跟前一組的 0.436 不衝突：**那一組是每類 40 句的平衡抽樣**（中性只佔 14%），這一組是自然分布（中性佔 46%），兩個數字量的是不同的東西，不能互相取代。

### 三、跨句換臉不是問題——至少不是模型造成的

它的換臉率 0.492–0.498，**比標準答案的 0.509 還低一點**。也就是說「AI 虛擬人會每句換一張臉」這個擔心，在這份資料上不成立。

但要把話講完整：**MELD 的標準答案本身就每兩句換一次臉**（0.509），因為那是情境喜劇。所以「跟標準答案一致」的意思是「大約每兩句換一次」——那在一個 VTuber 身上看起來仍然是忙碌的。**要更穩不是模型的事，是你自己要加遲滯。** 另外模型本身的抖動另計：同一題重問三次給同一答案的比例是 0.964–0.978，所以重複詢問同一句大約有 2–4% 的機率換答案。

### 四、脈絡買到的是校準，不是準確率——兩組獨立樣本都這樣

前一組量到脈絡讓準確率 +0.049（CI 剛好不含零）、ECE 從 0.239 降到 0.121。這一組在完全不同的抽樣下：準確率 +0.038（**CI 跨零**）、ECE 從 0.119 降到 **0.050**。

把兩組合起來讀，誠實的結論是：**脈絡對準確率的效果很小、而且不穩定到無法可靠地跟零區分；對校準的效果大且兩次都複現。** 它同時也把「過度預測中性」拉回來（0.631 → 0.550，標準答案是 0.459）。要一句話的話：**加上前文，它主要不是變得更準，是變得比較誠實。**

## 限制

- **聆聽表情的標準答案是代理答案**：聽者下一句話的情緒，受到的影響不只是他剛聽到的那句。真正的聆聽表情標註不存在，我們沒有自己標。所以「打不過一律中性」這句話要連著代理答案一起讀；但「53.6% 直接回答說話者的情緒」那個觀察不受代理答案影響。
- **「完美情緒追蹤」那兩臂用的是人工標註的 gold 情緒標籤**，所以量到的是上界：真實系統的追蹤器只會更差。上界都拿不到分數，是這個結論之所以強的原因；但反過來說，這組沒有測「一個更豐富的角色狀態（關係、目標、長期記憶）會不會有救」。
- **樣本是 30 段對話、357 句**，全部來自同一部情境喜劇。情境喜劇的情緒波動遠高於日常對話（標準答案每兩句就換一次臉）。
- **MELD 的標籤是標註者看著影片、聽著聲音標的**，所以一部分答案不在文字裡——前一組已經量過這個落差，這一組沒有再拆開。
- **自然分布的準確率會被中性的比例撐高**：模型預測中性的比例（0.55–0.63）高於標準答案（0.459），所以它靠中性賺到一部分分數。「一律中性」那條基準線就是為了讓這件事看得見。
- 單一 run date、單一模型版本（`jev-latest` 當天回 `jev-1.13.0`）。延遲從台灣量，含網路往返。

## 資料與授權

**語料原文不在這個 repo 裡**：MELD 上游是 GPL-3.0，內容衍生自受版權保護的影集台詞。`data/cases.json` 與 `data/_cache/` 都 gitignored，**收據存的是每個 state 的 SHA-256**。

```bash
python data/build_cases.py --stats                         # 語料層級的基準線，不打 API
python data/build_cases.py --verify runs/2026-09-23.json                # 3516 receipts, 0 mismatches
python data/build_cases.py --verify runs/2026-09-23-listener-state.json # 1050 receipts, 0 mismatches
python score.py --check                                    # 從收據重算，數字對不上就 exit 1
```

## 怎麼重跑

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # 印出各臂實際會送出的 state
python run.py --arms=self_no_context,self_context,listening_no_context,listening_context
python run.py --arms=listening_tracked,listening_tracked_nolabel --out=listener-state
python score.py             # 重算並寫出 runs/<日期>-scores.json
```

## 標籤

🔬（我們自己打 API 測的；原始回應在 [`runs/`](runs/)。標準答案是第三方的，聆聽那一臂是我們從第三方標籤推出來的代理答案。）

---

# Expressions across a whole dialogue (English)

## What this measures

[`suites/expression-selection/`](../expression-selection/) measured one line, one expression. Anyone building an AI VTuber or a virtual character then hits two more questions, and both are only visible across **a whole dialogue**:

1. **The listening expression**: A says this line — what face should **B, the person hearing it**, wear? (AnimeAct Engine's pitch specifically claims it decides both the speaking and the listening expression.)
2. **How often the face changes between lines**: switching too often is more visible on screen than picking wrong.

So this suite samples **whole dialogues in order**: 30 of the 192 MELD test dialogues with at least 6 utterances, all 357 of their lines, **six arms**, 3 repeats, 4,566 calls in two batches (3,516 for the first four arms; 1,050 for the two listener-state arms, in a second receipt file). The speaker arms reuse the previous suite's wording **verbatim** so the two compare.

**There is no ready-made oracle for a listening expression** — MELD labels the speaker's emotion, not the listener's face. The proxy used here is **the emotion label of the listener's own immediately following utterance**, over adjacent pairs where the speaker changes. It is somebody else's label rather than one we invented, but it is a proxy; see the limitations.

## Results

`jev-1.13.0`; 4,566 calls across two batches, 0 errors, 151.3 s, 3,092,046 input tokens (about $0.13). Both warm-up calls (845.8 and 775.9 ms) are excluded.

**This sample has MELD's natural distribution** (45.9% of the speaker arm's gold is neutral), unlike the previous suite's balanced 40-per-class. So the baseline to read against is always-neutral, not 1-in-7 chance.

| Arm | Accuracy | Always-neutral | ECE | Mean conf. | Share predicted neutral | Same answer ×3 |
|---|---|---|---|---|---|---|
| Speaker + 4 turns | **0.669** | 0.459 | **0.050** | 0.687 | 0.550 | 0.978 |
| Speaker, line only | 0.639 | 0.459 | 0.119 | 0.755 | 0.631 | 0.964 |
| **Listener + 4 turns** | **0.431** | **0.437** | 0.179 | 0.573 | 0.498 | 0.934 |
| **Listener, line only** | **0.403** | **0.437** | 0.249 | 0.652 | 0.684 | 0.961 |
| Listener + 4 turns + **a perfect tracker of their state** | **0.432** | 0.429 | 0.220 | 0.632 | — | — |
| Listener + 4 turns + their prior lines (no emotions) | 0.404 | 0.429 | 0.203 | 0.562 | — | — |

Latency is p50 around 256 ms and p95 between 320 and 334 ms across all six arms.

The last two rows only run on the 175 items (76% of 229) where the listener has already spoken in that dialogue; on that same subset `Listener + 4 turns` scores 0.432 and always-neutral is 0.429 — all three are effectively tied.

**Switching between lines** (same dialogue, same character, consecutive utterances; 273 opportunities):

| | Switch rate |
|---|---|
| Gold, on these 30 dialogues | 0.509 |
| Speaker + 4 turns | **0.492** |
| Speaker, line only | **0.498** |

**Effect of context** (paired, over items that actually have a preceding turn): speaker **+0.038, 95% CI [−0.003, +0.075]** (86 won, 49 lost); listener +0.031, 95% CI [−0.039, +0.093] (80 won, 61 lost). **Both intervals cross zero.**

**Effect of adding the listener's state** (paired over the same 175 items):

| Comparison | Accuracy diff | 95% CI | Per item |
|---|---|---|---|
| Perfect tracker vs context only | **+0.000** | [−0.069, +0.067] | 61 won, 61 lost |
| Perfect tracker vs their prior lines only | +0.029 | [−0.027, +0.084] | 51 won, 36 lost |
| Their prior lines only vs context only | −0.029 | [−0.074, +0.017] | 23 won, 38 lost |

## What this means

### 1. The listening expression does not hold up — and this overturns our own earlier call

We expected the listening expression to sit on the **self-contained** side of the core axis, on what sounded like solid reasoning: the trigger is in the line the other person just said, and that line is in the `state`. **The measurement says otherwise.** Both arms **fail to beat always-neutral** (0.403 and 0.431 against 0.437), with poor calibration (ECE 0.179–0.249).

The behavioural explanation is clearer than the scores: **50.8% (no context) to 53.6% (with context) of its answers are simply the speaker's own emotion** — it **mirrors**. That observation doesn't depend on our proxy oracle at all; it is counted directly from the answers.

Why? Because **a listener's reaction is not a function of the line, it is a function of what the line means to that listener** — which needs their goals, the relationship, and what happened earlier. None of that is in the `state`. "Why didn't you show up yesterday" lands completely differently on someone who owes a favour and someone who was stood up. **This is the core axis, not a model failure.**

**To build a listening expression, the fix isn't a better question, it's putting the listener's state into the `state`** — their current mood, the relationship, what they care about. That is exactly what [jingx8885/lov-evo](https://github.com/jingx8885/lov-evo) does (it assembles the character's own `self_emotion` and a relationship ledger), and it carries a design note worth copying: **"the user's emotion is the input, not the thing she should mirror."** These numbers measure what happens when you don't do that: it mirrors.

### 1b. Handing it a perfect character-emotion tracker gains exactly nothing

The section above concludes that building a listening expression means putting the listener's state into the `state`. **We tested that sentence directly, and it is wrong.**

We gave it a listener state **better than any product could have**: the listener's own last two turns in this dialogue, **with their human-annotated emotion labels attached**. That simulates a *perfect* character-emotion tracker; a real system can only do worse. The result:

- **Accuracy 0.432, against 0.429 for always-neutral and 0.432 for context-only on the same items — a three-way tie.**
- Paired: **+0.000, 95% CI [−0.069, +0.067], 61 items won and 61 lost.** Not a small effect; exactly zero.
- Giving the listener's prior lines *without* the emotion labels is slightly worse (0.404).

**The behavioural shift is what actually explains it**:

| | Answer = speaker's emotion | Answer = listener's own prior emotion |
|---|---|---|
| Context only | 53.6% | — |
| With a perfect tracker | 43.8% | **72.0%** |

**It didn't start reasoning; it just changed what it copies.** Without a listener state it copies the speaker's emotion; with one it copies the listener's (72%) — and "repeat the listener's previous emotion" is itself only 0.4145 across the corpus, **worse than always-neutral's 0.4739**. So putting the state in the `state` doesn't rescue it, it anchors it to a worse shortcut.

💭 The implication is not that character-emotion tracking is useless. It is that **the state you track should drive the face from your own code, not be handed to the model to ask again**. [jingx8885/lov-evo](https://github.com/jingx8885/lov-evo) does exactly that: its `avatar.DriveWithRelationship` is *code* mapping the character's own emotion, steering mode and relationship stage onto expressions, while Jev only judges the user's turn. These numbers are independent support for that design: **use the state you already hold; don't ask the model what face it implies.**

### 2. The speaker's expression holds up on the natural distribution

0.639 to 0.669, 18 to 21 points above always-neutral at 0.459. This does not contradict the previous suite's 0.436: **that was a balanced 40-per-class sample** (neutral 14%), this is the natural distribution (neutral 46%). They measure different things and neither replaces the other.

### 3. Flicker isn't the problem — at least not the model's share of it

Its switch rate is 0.492–0.498, **slightly below the gold rate of 0.509**. So "an AI avatar will pull a new face every line" is not borne out here.

But to finish the thought: **MELD's own gold changes expression every other line** (0.509), because it is a sitcom. So "matching gold" means "changing about every other line", which on a VTuber still looks busy. **Making it calmer is not the model's job, it's your hysteresis.** Model jitter is separate and small: the same item gives the same answer across all three repeats 96.4–97.8% of the time, so re-asking an identical line changes the answer about 2–4% of the time.

### 4. Context buys calibration, not accuracy — now replicated on a second sample

The previous suite measured context at +0.049 accuracy (CI only just excluding zero) with ECE falling 0.239 → 0.121. On this quite different sample: +0.038 accuracy (**CI crosses zero**) with ECE falling 0.119 → **0.050**.

Read together, the honest conclusion is: **context's effect on accuracy is small and not reliably distinguishable from zero; its effect on calibration is large and replicated twice.** It also pulls back the over-prediction of neutral (0.631 → 0.550, against gold 0.459). In one sentence: **give it the preceding turns and it mostly doesn't get more accurate, it gets more honest.**

## Limitations

- **The listening oracle is a proxy**: a listener's next line is shaped by more than what they just heard. Real listening-expression annotation does not exist and we did not create it. So "fails to beat always-neutral" must be read together with the proxy — though "53.6% of answers are the speaker's own emotion" does not depend on it.
- **The two "perfect tracker" arms use human-annotated gold emotion labels**, so they measure an upper bound: a real tracker can only be worse. That the upper bound gains nothing is what makes the conclusion strong; conversely, this suite does not test whether a richer character state (relationship, goals, long-term memory) would rescue it.
- **The sample is 30 dialogues and 357 lines**, all from one sitcom. Sitcom emotion is far more volatile than ordinary conversation (gold changes face every other line).
- **MELD's labels were assigned with video and audio available**, so part of the answer isn't in the text. The previous suite measured that gap; this one does not separate it again.
- **Natural-distribution accuracy is propped up by neutral**: the model predicts neutral more often (0.55–0.63) than gold does (0.459), so some of the score is free. The always-neutral baseline is there to make that visible.
- One run date, one model build (`jev-latest` answered as `jev-1.13.0`). Latency measured from Taiwan, including the network round trip.

## Data and licensing

**The corpus text is not in this repository**: MELD is GPL-3.0 upstream and derived from copyrighted TV dialogue. `data/cases.json` and `data/_cache/` are gitignored, and **the receipts store the SHA-256 of each state**.

```bash
python data/build_cases.py --stats                         # corpus-level baselines, no API calls
python data/build_cases.py --verify runs/2026-09-23.json                # 3516 receipts, 0 mismatches
python data/build_cases.py --verify runs/2026-09-23-listener-state.json # 1050 receipts, 0 mismatches
python score.py --check                                    # recomputes from receipts; exit 1 on drift
```

## Reproducing

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # print the exact states each arm would send
python run.py --arms=self_no_context,self_context,listening_no_context,listening_context
python run.py --arms=listening_tracked,listening_tracked_nolabel --out=listener-state
python score.py             # recompute and write runs/<date>-scores.json
```

## Tag

🔬 (our own API calls; raw responses in [`runs/`](runs/). The gold labels are third-party; the listening arm's oracle is our proxy derived from them.)
