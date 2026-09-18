🇹🇼 中文｜🇬🇧 English below

# 純回憶史實題:有無背景段落的對照

## 這組測什麼

三道中文歷史選擇題:①常見史實、無背景段落 ②冷門史實、無背景段落 ③跟②同一題,但在 `state` 裡附上背景段落。目的是隔離出「裸記憶」跟「給定文字內的閱讀理解」這兩種完全不同的能力。

## 為什麼測這個

能力地圖那條軸的「不自足」那一側,目前最需要具體反例——純知識回憶題沒有給任何支撐段落,答案完不完全取決於模型預訓練時「記得」什麼,這跟這條軸原本測的「給定文字內能不能正確判讀」是不同的能力,值得分開測、分開講清楚。

## 方法論

三題,單一標註者(我們自己)出題兼判標準答案。**案例 A 的標準答案本身有算法爭議**:若從順治入關(1644)算第 1 任,第 2 任是康熙;若嚴格從「大清」國號 1636 年確立算起,第 2 任其實是順治,三個選項裡沒有一個是嚴格正解。我們採用前者(較常見的通俗算法)當標準答案,但在 report 裡誠實列出這個爭議,不是我們藏起來的瑕疵。

## 結果

見 `runs/2026-09-19.json`(官方收據,這份文件的數字全部對這一份)。

| 案例 | 題目 | 有無背景 | 選擇 | 信心 | 機率分布 | 對錯(依常見算法)|
|---|---|---|---|---|---|---|
| A | 大清帝國第二任皇帝 | 無 | 雍正 | 0.90 | 1:0.04 / 2:0.93 / 3:0.03 | ✗(標準答案康熙)|
| B | 大清帝國第七任皇帝(冷門)| 無 | 咸豐 | 0.07 | 1:0.25 / 2:0.37 / 3:0.38 | ✓(但信心幾乎打平三選項,答對更接近運氣而非把握)|
| C | 同 B,附背景段落 | 有 | 咸豐 | 0.97 | 1:0.00 / 2:0.02 / 3:0.98 | ✓ |

**案例 B 的一個誠實補充**:我們在寫這組正式收據之前,已經口頭跟執政官對話裡先跑過一次同一題(未存檔,不算這組的官方數據),那一次信心 0.08、選到**錯誤**答案(道光)。兩次都是接近三選一打平的低信心,只是剛好一次矇對一次矇錯——這正好印證低信心的意思是「真的沒把握」,不是「偏向錯誤」,再次呼應案例 C 給了背景後機率直接衝到 0.98 集中度的對比。

## 為什麼這組重要

案例 A 是**高信心答錯**——不是低信心答錯(那還算誠實),是連一般認為的「常識題」都用 0.90 的信心給錯答案。案例 B/C 對照顯示:同一題沒給背景時信心誠實地趴在打平線附近(0.07,三個選項機率 0.25/0.37/0.38 幾乎沒有領先),給了背景後不只答對、機率也集中到 0.98。**結論不是「Jev 不可靠」,是「它的裸記憶不可靠,但給定文字內的閱讀理解很可靠」——這兩者是不同的能力,混在一起講會讓人錯估風險在哪裡。**

## 限制

N=3,單一標註者,只測了中文歷史一個領域,案例 A 的標準答案本身有爭議。模型有隨機性,同一題重跑不保證同一結果(案例 B 就是活生生的例子)——這也是為什麼收據要存 `probabilities` 全分布,不能只看單一次的 `choice`。這遠不足以量化「Jev 的裸記憶知識廣度」,只能證明「裸記憶存在真實風險,給背景可以修正」這個定性結論。歡迎貢獻更大規模、跨領域的裸記憶 vs. 給定背景對照測試。

## 標籤

🔬 我們自己測的,真實 API 呼叫,見 `runs/`。

---

# Pure-recall trivia: with vs. without a supporting passage (English)

## What this tests

Three Traditional-Chinese history multiple-choice questions: (A) a commonly-known fact, no supporting passage; (B) an obscure fact, no supporting passage; (C) the same question as B, but with a supporting passage included in `state`. The goal is isolating "bare memory" from "reading comprehension given supplied text" — two genuinely different capabilities.

## Why this task

The capability map's "not self-contained" side needed a concrete counter-example. A pure-recall question with no supporting passage tests whatever the model happened to memorize during opaque pretraining — a different capability from "can it correctly judge given text," which is what the rest of this project mostly tests.

## Methodology

Three items, single annotator (us) both wrote the questions and judged ground truth. **Case A's ground truth is itself historically contested**: counting from the Shunzhi emperor entering Beijing in 1644 as the 1st emperor, the 2nd is Kangxi; counting strictly from when the "Great Qing" name was adopted in 1636, the 2nd is actually Shunzhi, and none of the three offered options would be strictly correct. We use the more common popular convention as ground truth, and disclose the ambiguity here rather than hiding it.

## Results

See `runs/2026-09-19.json` (the receipt of record — every number below traces to it).

| Case | Question | Context given? | Choice | Confidence | Probabilities | Correct (by common convention) |
|---|---|---|---|---|---|---|
| A | 2nd Qing emperor | No | Yongzheng | 0.90 | 1:0.04 / 2:0.93 / 3:0.03 | ✗ (standard answer: Kangxi) |
| B | 7th Qing emperor (obscure) | No | Xianfeng | 0.07 | 1:0.25 / 2:0.37 / 3:0.38 | ✓ (but confidence was near-flat across all three — correct by luck more than conviction) |
| C | Same as B, with context | Yes | Xianfeng | 0.97 | 1:0.00 / 2:0.02 / 3:0.98 | ✓ |

**An honest addendum on Case B**: before writing this suite's official receipt, we'd already asked the same question once earlier, informally, in conversation (not saved, not part of this suite's official data) — that run landed on confidence 0.08 and picked the **wrong** answer (Daoguang). Both runs were near-flat, low-confidence three-way guesses; one happened to land right, one wrong. That's exactly what "low confidence" should mean — genuine uncertainty, not a bias toward being wrong — and it sharpens the contrast with Case C, where supplying context pushed the distribution to a real 0.98 concentration.

## Why this suite matters

Case A is **confidently wrong** — not low-confidence-wrong, which would at least be honest, but 0.90 confidence on a question most people would call common knowledge. The B/C contrast shows the same question going from an honestly near-flat distribution with no context (0.07 confidence, 0.25/0.37/0.38 across the three options) to a correct, sharply concentrated answer (0.98 on the right option) once context is supplied. **The conclusion isn't "Jev is unreliable" — it's "its bare memory is unreliable, but its reading comprehension over supplied text is reliable." Conflating the two misjudges where the actual risk sits.**

## Limitations

N=3, single annotator, one domain (Chinese history) only, and Case A's ground truth is itself contested. The model has real sampling variance — re-running the same question is not guaranteed to reproduce the same pick (Case B is a live example of this), which is exactly why the receipt stores the full `probabilities` distribution, not just the single `choice`. Nowhere near enough to quantify "how broad is Jev's bare recall knowledge" — only enough to establish the qualitative point that bare recall carries real risk and supplying context corrects it. Larger, cross-domain bare-recall-vs-context suites are a welcome contribution.

## Tag

🔬 Our own test, real API calls, see `runs/`.
