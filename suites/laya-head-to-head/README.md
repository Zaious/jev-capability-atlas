🇹🇼 中文｜🇬🇧 English below

# Jev vs Laya：同一組輸入的正面對照

## 一句話結論

**同樣的輸入、同樣的題目、同一套評分定義之下，Laya 贏過 Jev 只有一種情況：它專門微調過的版本，在自己的訓練分布上，準確率高 3 個百分點，而且校準比 Jev 差五倍。** 當成「不用訓練、直接拿來問新問題」的通用工具來比，Laya 在 typed-decisions 上低於「完全不看輸入、只猜最常見答案」的基準線；中文意圖分類上，繁中落後 Jev 32 個百分點、簡中落後 29 個百分點。

## 為什麼做這組

[Laya](https://huggingface.co/convaiinnovations/laya) 是 2026 年 9 月開源的決策模型（Apache 2.0，BERT 類編碼器加決策輸出層，題型一樣是 choice/score/noul），發布後以「開源、比 Jev 快 7 倍、準確率和校準都更好」快速爆紅。但它自己的模型說明寫明：表上 Jev 那一欄是「第三方發表、從未在這裡量過（沒有 TypeSafe API 權限），樣本數與提示都不同」。它主打的 typed-decisions 勝場，用的是**在該跑分訓練集上微調過**的版本，而這份資料集自己的說明要求：專用模型（在這些工作流程上訓練過）跟通用模型（沒看過、直接回答）的分數不能不加標注地並排，「遠高於 0.75 代表模型學到的是出題老師的怪癖，不是任務本身」。

我們有 Jev 的 API，Laya 團隊沒有。所以這組把同樣的 `state` 和題目同時送給兩邊，逐題留收據。

## 方法論

- **Part A：typed-decisions 測試集**（[LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)，400 案 × 5 題 = 2,000 個判斷，英文）。每一列本身就是 System One 的請求內容，原封不動送給兩邊。標準答案是一個未公開的約 4B 級「出題老師」模型取樣三次的平均——**衡量的是跟那個老師的一致程度，不是對錯**。
- **Part B：MASSIVE 意圖分類**（人工標註），繁中、簡中、英文各取前 100 句，20 選 1。題目組法照抄 Laya 自己的 `build_massive()`（種子 13），跟它公布的多語言掃描設定完全相同。
- **比較對象**：Jev（`jev-1.13.0`，通用模式）；Laya 英文版、多語版（通用模式，沒看過這些工作流程）；Laya typed-decisions 版（**專用模式**，在 Part A 訓練集上微調過，只跑 Part A）。
- **評分定義**：照抄 Laya 自己的評測程式（`research/scripts/bench_local.py`）——argmax 準確率、soft accuracy、對 soft 標準答案的 Brier、15 區間 ECE（以最高機率當信心）、score 題的 MAE。兩邊用同一支 `score.py` 評。
- **信賴區間**：準確率差距用 bootstrap（2,000 次，Part A 以「案」為單位重抽，因為同一案的 5 題共用同一份 state）。
- **Laya 用法**：公開 API `laya.load(...).predict(state, questions)`，出廠溫度參數、不重新調整，跑在 CPU 上（本機兩張 GPU 當時都被佔滿）。
- 所有版本（資料集、三個權重檔、SDK、套件）都釘在 `protocol.yaml`。

## 先驗證：我們重現得出 Laya 自己公布的數字嗎？

得出來。Laya 英文版 typed-decisions 0.3615、專用版五項指標（0.766 / 0.471 / 0.062 / 0.213 / 0.242）、英文版 MASSIVE 三個語言（0.46 / 0.62 / 0.82），**跟它公布的數字完全一致**；多語版在 typed-decisions 上是 0.352，它自己的文件一處寫 0.352、另一處寫 0.342。多語版的 MASSIVE 比它公布的高 0.02–0.07（繁中 0.61 對 0.54），可能是套件版本不同（它當時用 0.2.0，我們用 0.3.4），沒有進一步追查。也就是說，Laya 量它自己的那一半是誠實的——問題出在跟 Jev 的比法，不在它自己的量測。

## 結果

收據：`runs/2026-09-21-jev.json`（Jev，700 次呼叫、0 失敗、564,895 input tokens，約 0.024 美元）、`runs/2026-09-22-laya.json`（Laya，跑過午夜所以日期不同）、`runs/2026-09-21-scores.json`（評分結果）。

### Part A：typed-decisions（400 案／2,000 個判斷）

| 模型 | 模式 | 準確率 | soft acc | Brier（對 soft）| ECE | score MAE |
|---|---|---|---|---|---|---|
| **Jev** | 通用 | **0.736** | **0.538** | 0.149 | **0.041** | 0.390 |
| Laya 英文版 | 通用 | 0.362 | 0.332 | 0.316 | 0.175 | 0.694 |
| Laya 多語版 | 通用 | 0.352 | 0.328 | 0.463 | 0.314 | 0.760 |
| Laya typed-decisions 版 | **專用** | **0.766** | 0.471 | **0.062** | 0.213 | **0.242** |

參考線：不看輸入、每題猜訓練集最常見答案 = **0.484**；資料集說明的出題老師自我一致上限 = 0.735。

準確率差距（Jev 減 Laya，95% 信賴區間）：對英文版 **+0.375**（0.342 至 0.411）；對多語版 **+0.384**（0.354 至 0.414）；對專用版 **−0.030**（−0.052 至 −0.010）。

分工作流程的準確率：

| 模型 | agent trace | 客服 | 發票 | 資安事件 |
|---|---|---|---|---|
| Jev | 0.634 | 0.788 | 0.778 | 0.744 |
| Laya 英文版 | 0.388 | 0.382 | 0.360 | 0.316 |
| Laya 多語版 | 0.286 | 0.420 | 0.308 | 0.394 |
| Laya 專用版 | 0.730 | 0.764 | 0.804 | 0.766 |

### Part B：MASSIVE 意圖分類（20 選 1，每種語言 100 句，人工標註）

| 語言 | 模型 | 準確率 | ECE | 平均信心 |
|---|---|---|---|---|
| 繁中 | **Jev** | **0.93** | 0.042 | 0.93 |
| 繁中 | Laya 英文版 | 0.46 | 0.520 | 0.98 |
| 繁中 | Laya 多語版 | 0.61 | 0.266 | 0.86 |
| 簡中 | **Jev** | **0.94** | 0.047 | 0.95 |
| 簡中 | Laya 英文版 | 0.62 | 0.376 | 0.99 |
| 簡中 | Laya 多語版 | 0.65 | 0.219 | 0.86 |
| 英文 | **Jev** | **0.92** | 0.043 | 0.95 |
| 英文 | Laya 英文版 | 0.82 | 0.179 | 1.00 |
| 英文 | Laya 多語版 | 0.71 | 0.233 | 0.89 |

準確率差距（Jev 減 Laya 最好的那個版本，95% 信賴區間）：繁中 **+0.32**（0.21 至 0.43）、簡中 **+0.29**（0.19 至 0.39）、英文 **+0.10**（0.03 至 0.18）。

## 這代表什麼

**1. 「Laya 贏 Jev」只在一種條件下成立，而且贏的方式要看清楚。** 專用版在自己的訓練分布上，argmax 準確率高 3 個百分點（信賴區間不跨零，是真的差距），score 題的 MAE 跟對 soft 標準答案的 Brier 也更好——它學會了貼近出題老師的機率分布。但它的 0.766 已經高於出題老師自己的一致上限 0.735。資料集說明把 0.75 左右視為飽和，並提醒「遠高於 0.75」代表學到的是老師的怪癖——0.766 還稱不上遠高於，但已經在這條線上方，值得存疑。它的校準誤差 0.213 則是 Jev（0.041）的五倍。

**2. 當通用工具用，Laya 目前不能用。** 沒微調過的兩個版本在 typed-decisions 上只有 0.35–0.36，**低於完全不看輸入的 0.484 基準線**。Jev 沒看過這些工作流程，照樣到 0.736——剛好落在出題老師自我一致上限附近。你的任務如果是新的、沒有訓練資料的（例如我們自己的第一關篩選），能直接用的是 Jev。

**3. 中文差距最大，而且 Laya 錯的時候很有自信。** 繁中意圖分類 Jev 0.93，Laya 最好 0.61。Laya 英文版拿到繁中時，準確率 0.46、平均信心卻是 0.98——這是本 repo 一路在講的「高信心答錯」最典型的樣子，而且這次有 100 筆收據。

**4. Laya 表上引用的 Jev 數字，部分跟我們量的對得上，部分對不上。** 準確率（引用 0.727／實測 0.736）、Brier（0.148／0.149）、score MAE（0.391／0.390）幾乎一樣，看得出那些數字來自真的有人跑過這份資料；但 ECE（引用 0.144／實測 0.041）和 soft accuracy（0.580／0.538）差很多，可能是定義不同。**照 Laya 自己評測程式的 ECE 定義，Jev 的校準比 Laya 每一個版本都好**——跟「Laya 校準好三倍」的說法方向相反（那個說法用的是另一份資料、而且是 Laya 事後調過溫度的數字）。

**5. 速度這組沒有測。** Laya 說的 33ms 是在 GPU 上；我們只能在 CPU 上跑，而且機器當時有其他負載，Laya 在 typed-decisions 上每案 2–5 秒，不代表它正常的速度。Jev 走網路 API，中位數約 240–250ms，跟我們[延遲測試](../jev-latency-distribution/)的結果一致。

## 實務判斷：什麼時候該考慮 Laya

💭 Laya 真正的賣點不是「比 Jev 準」，是**自架、資料不出機器、沒有每次呼叫的成本、可以自己微調**。適合的情況是：工作流程固定、手上有足夠的標註資料可以微調、有 GPU、而且有資料不能外送的限制——這時候微調出來的專用版可以追上甚至小幅超過 Jev 的準確率，但要自己重新做溫度校準，不能直接相信它給的信心值。反過來，任務是新的、沒有訓練資料、或是中文，目前的 Laya 通用版不是 Jev 的替代品。

## 限制

- **Part A 的標準答案是一個未公開模型的輸出**，衡量的是一致程度不是對錯；如果那個出題老師跟 Jev 有血緣關係，Jev 的分數會被墊高——資料集沒有說老師是誰，我們無法排除。
- **資料汙染無法排除**：MASSIVE 是 2022 年公開的資料集，任何模型（包括 Jev 和 Laya 的底座）都可能在預訓練時看過。
- Laya 用出廠溫度參數、沒有重新調整；它自己的說明寫明重新調整溫度是「效益最高的修正」，調過以後 ECE 會變好，但準確率不變。
- 每個模型每題只跑一次；Part B 每種語言 100 句。
- Laya 跑在有其他負載的 CPU 上，延遲數字不能拿來比速度。
- 我們沒有測 Laya 的 GPU 速度，也沒有測小型通用 LLM（例如 [jevmlx](https://github.com/bnsd55/jevmlx)）或擴散模型路線。

## 怎麼重跑

```
pip install typesafe-sdk --extra-index-url https://pypi.typesafe.ai/
pip install laya==0.3.4 torch pandas pyarrow huggingface_hub
python run_jev.py            # 需要 TYPESAFE_API_KEY
python run_laya.py           # 下載三個權重檔（約 3.7GB），CPU 即可
python score.py
```

## 標籤

🔬 我們自己測的，真實 API 呼叫與本機推論，收據見 `runs/`。

---

# Jev vs Laya: a head-to-head on identical inputs (English)

## Bottom line

**With identical inputs, identical questions, and one scoring definition, Laya beats Jev in exactly one situation: its specially fine-tuned checkpoint, on its own training distribution, by 3 points of accuracy — while its calibration error is five times Jev's.** As a general tool that answers new questions without training, Laya scores below an input-blind "always guess the most common label" baseline on typed-decisions, and trails Jev by 32 points on Traditional-Chinese and 29 points on Simplified-Chinese intent classification.

## Why this suite

[Laya](https://huggingface.co/convaiinnovations/laya) is a decision model open-sourced in September 2026 (Apache 2.0, a BERT-style encoder plus a decision head, with the same choice/score/noul question types) that went viral as "open source, 7× faster than Jev, more accurate and better calibrated." But its own model card says the Jev column in its table is "third-party published, never measured here (no TypeSafe API access); sample sizes and prompts differ." Its headline typed-decisions win comes from a checkpoint **fine-tuned on that benchmark's train split** — and the dataset's own card says specialist scores (trained on these workflows) and generalist scores (never seen them) must not sit side by side unlabelled, and that "a score much above 0.75 means a model has learned the teacher's quirks rather than the task."

We have Jev API access; the Laya team doesn't. So this suite sends the same `state` and questions to both and keeps per-item receipts.

## Methodology

- **Part A: typed-decisions test split** ([LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), 400 cases × 5 questions = 2,000 decisions, English). Each row is itself a System One request body and is sent verbatim to both sides. Gold is the mean of three samples from an undisclosed ~4B-class "teacher" model — **it measures agreement with that teacher, not correctness**.
- **Part B: MASSIVE intent classification** (human labels), first 100 test utterances each for Traditional Chinese, Simplified Chinese and English, 20-way choice. Items built exactly as Laya's own `build_massive()` (seed 13), matching its published multilingual sweep.
- **Models**: Jev (`jev-1.13.0`, generalist); Laya English and multilingual checkpoints (generalist — never saw these workflows); Laya typed-decisions checkpoint (**specialist**, fine-tuned on Part A's train split, Part A only).
- **Metrics**: copied from Laya's own evaluation script (`research/scripts/bench_local.py`) — argmax accuracy, soft accuracy, Brier against the soft gold, 15-bin ECE on the max probability, MAE on score questions. Both sides scored by the same `score.py`.
- **Confidence intervals**: paired bootstrap on accuracy differences (2,000 resamples; Part A resamples whole cases, since a case's 5 questions share one state).
- **Laya usage**: public API `laya.load(...).predict(state, questions)`, shipped temperatures, no refit, on CPU (both local GPUs were occupied at the time).
- Every version (datasets, three checkpoints, SDK, package) is pinned in `protocol.yaml`.

## First: do we reproduce Laya's own published numbers?

Yes. Laya English on typed-decisions 0.3615; the specialist's five metrics (0.766 / 0.471 / 0.062 / 0.213 / 0.242); Laya English on MASSIVE for all three languages (0.46 / 0.62 / 0.82) — **all match its published figures exactly**; the multilingual checkpoint's typed-decisions score is 0.352, which its own docs give as 0.352 in one place and 0.342 in another. The multilingual checkpoint on MASSIVE comes out 0.02–0.07 higher than published (Traditional Chinese 0.61 vs 0.54), possibly a package-version difference (they used 0.2.0, we used 0.3.4); not investigated further. In other words, Laya measured its own half honestly — the problem is how it was compared to Jev, not its own measurements.

## Results

Receipts: `runs/2026-09-21-jev.json` (Jev: 700 calls, 0 errors, 564,895 input tokens, about $0.024), `runs/2026-09-22-laya.json` (Laya; the run crossed midnight, hence the date), `runs/2026-09-21-scores.json` (scores).

### Part A: typed-decisions (400 cases / 2,000 decisions)

| Model | Mode | Accuracy | Soft acc | Brier (vs soft) | ECE | Score MAE |
|---|---|---|---|---|---|---|
| **Jev** | generalist | **0.736** | **0.538** | 0.149 | **0.041** | 0.390 |
| Laya English | generalist | 0.362 | 0.332 | 0.316 | 0.175 | 0.694 |
| Laya multilingual | generalist | 0.352 | 0.328 | 0.463 | 0.314 | 0.760 |
| Laya typed-decisions | **specialist** | **0.766** | 0.471 | **0.062** | 0.213 | **0.242** |

Reference lines: input-blind, per-question train-split majority label = **0.484**; teacher self-agreement ceiling from the dataset card = 0.735.

Accuracy difference (Jev minus Laya, 95% CI): vs English **+0.375** (0.342 to 0.411); vs multilingual **+0.384** (0.354 to 0.414); vs specialist **−0.030** (−0.052 to −0.010).

Accuracy by workflow:

| Model | Agent trace | Customer service | Invoices | Security incidents |
|---|---|---|---|---|
| Jev | 0.634 | 0.788 | 0.778 | 0.744 |
| Laya English | 0.388 | 0.382 | 0.360 | 0.316 |
| Laya multilingual | 0.286 | 0.420 | 0.308 | 0.394 |
| Laya specialist | 0.730 | 0.764 | 0.804 | 0.766 |

### Part B: MASSIVE intent (20-way choice, 100 per language, human labels)

| Language | Model | Accuracy | ECE | Mean confidence |
|---|---|---|---|---|
| zh-TW | **Jev** | **0.93** | 0.042 | 0.93 |
| zh-TW | Laya English | 0.46 | 0.520 | 0.98 |
| zh-TW | Laya multilingual | 0.61 | 0.266 | 0.86 |
| zh-CN | **Jev** | **0.94** | 0.047 | 0.95 |
| zh-CN | Laya English | 0.62 | 0.376 | 0.99 |
| zh-CN | Laya multilingual | 0.65 | 0.219 | 0.86 |
| en | **Jev** | **0.92** | 0.043 | 0.95 |
| en | Laya English | 0.82 | 0.179 | 1.00 |
| en | Laya multilingual | 0.71 | 0.233 | 0.89 |

Accuracy difference (Jev minus Laya's best checkpoint per language, 95% CI): zh-TW **+0.32** (0.21 to 0.43), zh-CN **+0.29** (0.19 to 0.39), en **+0.10** (0.03 to 0.18).

## What this means

**1. "Laya beats Jev" holds under one condition, and how it wins matters.** On its own training distribution the specialist is 3 points ahead on argmax accuracy (the interval excludes zero — a real gap), and also better on score MAE and on Brier against the soft gold: it has learned to match the teacher's probability distributions. But its 0.766 already sits above the teacher's own self-agreement ceiling of 0.735. The dataset card treats about 0.75 as saturation and warns that "much above 0.75" means learning the teacher's quirks — 0.766 isn't "much above," but it is above that line, which warrants some doubt. Its calibration error, 0.213, is five times Jev's 0.041.

**2. As a general tool, Laya isn't usable yet.** Its two non-fine-tuned checkpoints score 0.35–0.36 on typed-decisions — **below the 0.484 input-blind baseline**. Jev, which has never seen these workflows either, reaches 0.736 — right at the teacher self-agreement ceiling. If your task is new and you have no training data for it (like our own stage-one triage filter), Jev is the one you can use as-is.

**3. The gap is widest in Chinese, and Laya is confident when it's wrong.** Traditional-Chinese intent classification: Jev 0.93, Laya's best 0.61. Given Traditional Chinese, Laya's English checkpoint scores 0.46 accuracy at 0.98 mean confidence — the textbook form of the "confidently wrong" pattern this repo keeps returning to, this time with 100 receipts.

**4. The Jev numbers quoted in Laya's table partly match what we measured, and partly don't.** Accuracy (quoted 0.727 / measured 0.736), Brier (0.148 / 0.149) and score MAE (0.391 / 0.390) are nearly identical, so those figures clearly come from a real run on this dataset; but ECE (quoted 0.144 / measured 0.041) and soft accuracy (0.580 / 0.538) differ a lot, possibly from different definitions. **Under the ECE definition in Laya's own evaluation script, Jev is better calibrated than every Laya checkpoint** — the opposite direction from the "3× better calibration" claim (which uses a different dataset and Laya's post-hoc temperature-fitted number).

**5. Speed wasn't tested here.** Laya's 33ms figure is on GPU; we could only run it on CPU, on a machine with other load, where it took 2–5 seconds per typed-decisions case — not representative of its normal speed. Jev through its network API had a median of about 240–250ms, consistent with our [latency suite](../jev-latency-distribution/).

## Practical judgment: when to consider Laya

💭 Laya's real selling point isn't "more accurate than Jev" — it's **self-hosted, data never leaves the machine, no per-call cost, and you can fine-tune it**. It fits when the workflow is fixed, you have enough labelled data to fine-tune, you have a GPU, and data can't leave your environment — a fine-tuned specialist can then match or slightly exceed Jev's accuracy, but you'll need to redo temperature calibration yourself rather than trust its confidence values. Conversely, for new tasks, tasks without training data, or Chinese, the current general-purpose Laya checkpoints are not a replacement for Jev.

## Limitations

- **Part A's gold is an undisclosed model's output**, measuring agreement, not correctness; if that teacher shares lineage with Jev, Jev's score is inflated — the dataset doesn't name the teacher, so we can't rule it out.
- **Contamination can't be ruled out**: MASSIVE has been public since 2022, and any model (including Jev and Laya's base encoders) may have seen it in pretraining.
- Laya ran with shipped temperatures, no refit; its own docs call refitting "the single highest-value fix," which would improve ECE but not accuracy.
- One call per model per item; Part B has 100 items per language.
- Laya ran on a loaded CPU; its latency numbers here say nothing about its speed.
- We didn't test Laya on GPU, small general LLMs (e.g. [jevmlx](https://github.com/bnsd55/jevmlx)), or the diffusion route.

## Re-running

```
pip install typesafe-sdk --extra-index-url https://pypi.typesafe.ai/
pip install laya==0.3.4 torch pandas pyarrow huggingface_hub
python run_jev.py            # needs TYPESAFE_API_KEY
python run_laya.py           # downloads three checkpoints (~3.7GB); CPU is fine
python score.py
```

## Tag

🔬 Our own test, real API calls and local inference, receipts in `runs/`.
