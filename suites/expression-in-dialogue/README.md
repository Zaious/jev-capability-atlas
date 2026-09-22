🇹🇼 中文｜🇬🇧 [English below](#expressions-across-a-whole-dialogue-english)

# 整段對話裡的表情：聆聽表情與跨句換臉

## 這組測什麼

[`suites/expression-selection/`](../expression-selection/) 量的是「一句話配一個表情」。做 AI VTuber 或虛擬角色的人接著會撞到的是另外兩件事，而那兩件只有在**一整段對話**裡才看得到：

1. **聆聽表情**：A 說了這句，**聽的人 B** 該擺什麼臉？（AnimeAct Engine 的宣傳特別提到它同時決定說話表情與聆聽表情。）
2. **跨句換臉的頻率**：同一個角色連續講好幾句，表情換太頻繁在畫面上比選錯還明顯。

所以這組改抽**整段對話、照順序全拿**：MELD 測試集裡 192 段至少 6 句的對話，抽 30 段，357 句全部跑過，四臂、每題重問 3 次、3,516 次呼叫。說話者那兩臂的問法跟前一組**一字不差**，兩邊才比得起來。

**聆聽表情沒有現成的標準答案**——MELD 標的是說話者的情緒，不是聽者的表情。我們用的代理答案是：**聽者自己緊接著那一句的情緒標籤**（只取換人說話的相鄰配對）。那是別人標的、不是我們編的，但它是代理，限制寫在下面。

## 結果

`jev-1.13.0`，3,516 次呼叫、0 次錯誤、116.5 秒、2,272,575 input tokens（約 0.095 美元）。暖機 845.8 毫秒不計入。

**這組是自然分布**（標準答案有 45.9% 是 neutral），不是前一組的平衡抽樣。所以該對照的是「一律中性」那條基準線，不是亂猜的 1/7。

| 臂 | 準確率 | 一律中性 | ECE | 平均信心 | 預測中性的比例 | 三次都一樣 |
|---|---|---|---|---|---|---|
| 說話者＋前四句 | **0.669** | 0.459 | **0.050** | 0.687 | 0.550 | 0.978 |
| 說話者，只給這一句 | 0.639 | 0.459 | 0.119 | 0.755 | 0.631 | 0.964 |
| **聆聽＋前四句** | **0.431** | **0.437** | 0.179 | 0.573 | 0.498 | 0.934 |
| **聆聽，只給這一句** | **0.403** | **0.437** | 0.249 | 0.652 | 0.684 | 0.961 |

延遲四臂都是 p50 約 257 毫秒、p95 約 330 毫秒。

**跨句換臉**（同一段對話、同一個角色，連續兩句之間換掉表情的比例，273 次機會）：

| | 換臉率 |
|---|---|
| 標準答案（這 30 段對話） | 0.509 |
| 說話者＋前四句 | **0.492** |
| 說話者，只給這一句 | **0.498** |

**脈絡的效果**（配對比較，只算真的有前文的題目）：說話者 **+0.038，95% CI [−0.003, +0.075]**（86 勝 49 敗）；聆聽 +0.031，95% CI [−0.039, +0.093]（80 勝 61 敗）。**兩個信賴區間都跨過零。**

## 這代表什麼

### 一、聆聽表情不成立——這推翻了我們自己先前的判斷

我們原本預期聆聽表情會落在核心軸**自足**的那一側，理由聽起來很合理：觸發它的線索就在對方剛說的那句話裡，而那句話就在 `state` 裡。**實測是反的**：兩臂都**打不過「一律中性」**（0.403 與 0.431 對上 0.437），而且校準很差（ECE 0.179–0.249）。

行為層面的解釋比分數更清楚：**它有 50.8%（無脈絡）到 53.6%（有脈絡）的時候，直接回答說話者自己的情緒**——也就是**照鏡子**。這個觀察不依賴我們的代理答案，是直接從回答數出來的。

為什麼？因為**聽者的反應不是那句話的函數，是那句話對那個聽者的意義的函數**——而那需要聽者的目標、兩人的關係、之前發生過什麼。那些不在 `state` 裡。同一句「你昨天為什麼沒來」，對欠人情的人和對被放鴿子的人，表情完全不同。**這是核心那條軸，不是模型不行。**

**要做聆聽表情，解法不是換問法，是把聽者的狀態放進 `state`**——聽者當下的情緒、關係階段、在意什麼。這正是 [jingx8885/lov-evo](https://github.com/jingx8885/lov-evo) 那個實作在做的事（它把角色自己的 `self_emotion` 與關係帳本組進去），而且它有一條設計註記值得抄：**「使用者的情緒是輸入，不是她要鏡像的目標」**——我們這組數字正好量出了不這樣做會發生什麼：它就是會去鏡像。

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
- **樣本是 30 段對話、357 句**，全部來自同一部情境喜劇。情境喜劇的情緒波動遠高於日常對話（標準答案每兩句就換一次臉）。
- **MELD 的標籤是標註者看著影片、聽著聲音標的**，所以一部分答案不在文字裡——前一組已經量過這個落差，這一組沒有再拆開。
- **自然分布的準確率會被中性的比例撐高**：模型預測中性的比例（0.55–0.63）高於標準答案（0.459），所以它靠中性賺到一部分分數。「一律中性」那條基準線就是為了讓這件事看得見。
- 單一 run date、單一模型版本（`jev-latest` 當天回 `jev-1.13.0`）。延遲從台灣量，含網路往返。

## 資料與授權

**語料原文不在這個 repo 裡**：MELD 上游是 GPL-3.0，內容衍生自受版權保護的影集台詞。`data/cases.json` 與 `data/_cache/` 都 gitignored，**收據存的是每個 state 的 SHA-256**。

```bash
python data/build_cases.py --stats                         # 語料層級的基準線，不打 API
python data/build_cases.py --verify runs/2026-09-23.json   # 3516 receipts, 0 hash mismatches
python score.py --check                                    # 從收據重算，數字對不上就 exit 1
```

## 怎麼重跑

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # 印出四臂實際會送出的 state
python run.py               # 3,516 次呼叫
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

So this suite samples **whole dialogues in order**: 30 of the 192 MELD test dialogues with at least 6 utterances, all 357 of their lines, four arms, 3 repeats, 3,516 calls. The speaker arms reuse the previous suite's wording **verbatim** so the two compare.

**There is no ready-made oracle for a listening expression** — MELD labels the speaker's emotion, not the listener's face. The proxy used here is **the emotion label of the listener's own immediately following utterance**, over adjacent pairs where the speaker changes. It is somebody else's label rather than one we invented, but it is a proxy; see the limitations.

## Results

`jev-1.13.0`; 3,516 calls, 0 errors, 116.5 s, 2,272,575 input tokens (about $0.095). Warm-up 845.8 ms, excluded.

**This sample has MELD's natural distribution** (45.9% of the speaker arm's gold is neutral), unlike the previous suite's balanced 40-per-class. So the baseline to read against is always-neutral, not 1-in-7 chance.

| Arm | Accuracy | Always-neutral | ECE | Mean conf. | Share predicted neutral | Same answer ×3 |
|---|---|---|---|---|---|---|
| Speaker + 4 turns | **0.669** | 0.459 | **0.050** | 0.687 | 0.550 | 0.978 |
| Speaker, line only | 0.639 | 0.459 | 0.119 | 0.755 | 0.631 | 0.964 |
| **Listener + 4 turns** | **0.431** | **0.437** | 0.179 | 0.573 | 0.498 | 0.934 |
| **Listener, line only** | **0.403** | **0.437** | 0.249 | 0.652 | 0.684 | 0.961 |

Latency is p50 around 257 ms and p95 around 330 ms on all four arms.

**Switching between lines** (same dialogue, same character, consecutive utterances; 273 opportunities):

| | Switch rate |
|---|---|
| Gold, on these 30 dialogues | 0.509 |
| Speaker + 4 turns | **0.492** |
| Speaker, line only | **0.498** |

**Effect of context** (paired, over items that actually have a preceding turn): speaker **+0.038, 95% CI [−0.003, +0.075]** (86 won, 49 lost); listener +0.031, 95% CI [−0.039, +0.093] (80 won, 61 lost). **Both intervals cross zero.**

## What this means

### 1. The listening expression does not hold up — and this overturns our own earlier call

We expected the listening expression to sit on the **self-contained** side of the core axis, on what sounded like solid reasoning: the trigger is in the line the other person just said, and that line is in the `state`. **The measurement says otherwise.** Both arms **fail to beat always-neutral** (0.403 and 0.431 against 0.437), with poor calibration (ECE 0.179–0.249).

The behavioural explanation is clearer than the scores: **50.8% (no context) to 53.6% (with context) of its answers are simply the speaker's own emotion** — it **mirrors**. That observation doesn't depend on our proxy oracle at all; it is counted directly from the answers.

Why? Because **a listener's reaction is not a function of the line, it is a function of what the line means to that listener** — which needs their goals, the relationship, and what happened earlier. None of that is in the `state`. "Why didn't you show up yesterday" lands completely differently on someone who owes a favour and someone who was stood up. **This is the core axis, not a model failure.**

**To build a listening expression, the fix isn't a better question, it's putting the listener's state into the `state`** — their current mood, the relationship, what they care about. That is exactly what [jingx8885/lov-evo](https://github.com/jingx8885/lov-evo) does (it assembles the character's own `self_emotion` and a relationship ledger), and it carries a design note worth copying: **"the user's emotion is the input, not the thing she should mirror."** These numbers measure what happens when you don't do that: it mirrors.

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
- **The sample is 30 dialogues and 357 lines**, all from one sitcom. Sitcom emotion is far more volatile than ordinary conversation (gold changes face every other line).
- **MELD's labels were assigned with video and audio available**, so part of the answer isn't in the text. The previous suite measured that gap; this one does not separate it again.
- **Natural-distribution accuracy is propped up by neutral**: the model predicts neutral more often (0.55–0.63) than gold does (0.459), so some of the score is free. The always-neutral baseline is there to make that visible.
- One run date, one model build (`jev-latest` answered as `jev-1.13.0`). Latency measured from Taiwan, including the network round trip.

## Data and licensing

**The corpus text is not in this repository**: MELD is GPL-3.0 upstream and derived from copyrighted TV dialogue. `data/cases.json` and `data/_cache/` are gitignored, and **the receipts store the SHA-256 of each state**.

```bash
python data/build_cases.py --stats                         # corpus-level baselines, no API calls
python data/build_cases.py --verify runs/2026-09-23.json   # 3516 receipts, 0 hash mismatches
python score.py --check                                    # recomputes from receipts; exit 1 on drift
```

## Reproducing

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # print the exact states the four arms would send
python run.py               # 3,516 calls
python score.py             # recompute and write runs/<date>-scores.json
```

## Tag

🔬 (our own API calls; raw responses in [`runs/`](runs/). The gold labels are third-party; the listening arm's oracle is our proxy derived from them.)
