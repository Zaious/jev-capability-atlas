🇹🇼 中文｜🇬🇧 English below

# 純回憶史實題：有無背景段落的對照

> **更正（2026-09-21）**：這組的舊版（2026-09-19）結論有錯，已撤回重做。舊版送出的題目有錯字，而且兩題都有算法歧義；README 開頭引用它的方式也把兩道不同的題說成同一題。錯字與配對錯誤由讀者在 [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2) 指出，算法歧義是我們複查時發現的。完整更正紀錄見本頁「舊版更正紀錄」。

## 這組測什麼

中文歷史選擇題：①常見史實、無背景段落 ②冷門史實、無背景段落 ③跟②同一題，但在 `state` 裡附上背景段落。目的是隔離出「裸記憶」跟「給定文字內的閱讀理解」這兩種不同的能力。另外附兩題**診斷用、不計分**的題目：把舊版兩題只修正錯字、其他一字不改重問，用來判斷舊版結果是錯字造成的，還是題目本身的問題。

## 為什麼測這個

能力地圖那條軸的「不自足」那一側需要具體例子——純知識回憶題沒有給任何支撐段落，答案完全取決於模型預訓練時「記得」什麼，這跟「給定文字內能不能正確判讀」是不同的能力，值得分開測、分開講清楚。

## 方法論

單一標註者（我們自己）出題兼判標準答案。這一版的出題規則是舊版錯誤換來的：

- **唯一正解**：不管用哪種慣例數、哪種稱呼，都只有一個選項說得通。「第幾任皇帝」這類題目要看從哪一任開始數，這一版改問父子、母子關係，不受數法影響。
- **選項都是真實人物**：②③ 的三個選項都是乾隆朝真實存在的皇后（乾隆第一位皇后／乾隆生母／嘉慶生母），不是一眼就能排除的假選項。
- **③ 的背景段落刻意把三個選項都提到**：要讀懂誰是誰的母親才答得對，不是只比對段落裡出現的名字。
- **送出前校字**：`python run.py --dry-run` 只印出將送出的 `state`、不打 API；收據裡也逐題存下實際送出的 `state`（舊版收據沒存，是舊版錯字沒被發現的原因之一）。
- **每題重問三次**：Jev 有隨機性，單次 `choice` 不足以下結論。

## 結果

見 `runs/2026-09-21.json`（官方收據，這份文件的數字全部對這一份）。15 次呼叫共 5,793 input tokens。

| 案例 | 題目 | 有無背景 | 三次選擇＠信心 | 機率分布（選項 1/2/3）| 對錯 |
|---|---|---|---|---|---|
| A | 乾隆的父親（常見）| 無 | 雍正＠1.00 ×3 | 0.00 / 1.00 / 0.00 | ✓ |
| B | 嘉慶的生母（冷門）| 無 | 孝儀純皇后＠0.87 ×3 | 0.01 / 0.08 / 0.91 | ✓ |
| C | 同 B，附背景段落 | 有 | 孝儀純皇后＠1.00 ×3 | 0.00 / 0.00 / 1.00 | ✓ |
| D | 舊版 A 修正錯字：「大清帝國的第二任皇帝」| 無 | 康熙＠0.50、0.51、0.46 | 約 0.65–0.68 / 0.32–0.35 / 0.00 | 不計分 |
| E | 舊版 B 修正錯字：「大清帝國的第七任皇帝」| 無 | 道光＠0.10、道光＠0.13、咸豐＠0.07 | 約 0.25–0.28 / 0.37–0.42 / 0.30–0.38 | 不計分 |

A、B、C 三次重問結果完全相同；D、E 三次之間有小幅浮動，E 甚至換了選項。

## 這代表什麼

**題目乾淨時，它的裸記憶比我們原本寫的好**：常見史實 1.00 答對，冷門史實不給背景也以 0.87 答對。**背景段落仍然有用**：同一道冷門題從 0.87 升到 1.00。但只有兩道題、一個領域，完全不足以說「它的知識很廣」——能說的只是「這兩題它知道」，以及**知不知道你事前看不出來**，需要的資料放進 `state` 仍然最保險。

**舊版「高信心答錯」的真正原因，是我們送出的題目壞了**：舊版 A 題把正確選項「康熙」打成「康燕」，它以 0.90 的信心選了雍正；只修正錯字重問（D），它三次都改選康熙。這才是這組最值得記下的教訓——**`state` 本身有錯時，它不會提醒你「這題怪怪的」，照樣很有把握地選一個**。它的判斷完全建立在你給的文字上，文字錯了，信心值不會替你把關。

**題目本身沒有唯一答案時，分布也沒有假裝有**：E 題「第七任皇帝」三種數法剛好各對一個選項——從努爾哈赤算（通行的「清朝十二帝」）是嘉慶、從 1636 年皇太極定國號算是道光、從 1644 年順治入關算是咸豐——三次重問機率都接近打平，信心 0.07–0.13。💭 這跟「不知道」在分布上長得一樣，單看這題分不出是哪一種；但同一組裡冷門的 B 題它以 0.87 答對，讓「題目歧義」這個解釋比「不知道」更說得通。D 題也一樣：數法不同，第二任可能是皇太極、順治或康熙，只有康熙在選項裡，它選康熙但信心只有 0.46–0.51。

## 舊版更正紀錄（2026-09-19，已撤回）

舊版送出的題目保留在 `data/cases.2026-09-19-withdrawn.json`，收據保留在 `runs/2026-09-19.json`，不刪，好讓任何人對得上這段更正。

**錯了什麼**：
1. **錯字**：三題的 `state` 都把「皇帝」打成「皮帝」，A 題正確選項與 C 題背景段落把「康熙」打成「康燕」——實際送進 API 的就是這些錯字。
2. **算法歧義**：舊版只揭露了 A 題的標準答案有爭議，沒發現 B、C 題「第七任皇帝」也一樣——三個選項剛好各對應一種數法。
3. **README 引用錯配**：README 開頭寫「同一道歷史選擇題，不給背景時 0.90 答錯、給了背景後 0.97 答對」，但 0.90 是 A 題（第二任）、0.97 是 C 題（第七任），是兩道不同的題。

**舊版數字**（僅供對照，不再作為任何結論的依據）：

| 案例 | 題目（含錯字）| 選擇 | 信心 | 機率分布 |
|---|---|---|---|---|
| A | 第二任皮帝，選項 (1)康燕 | 雍正 | 0.90 | 0.04 / 0.93 / 0.03 |
| B | 第七任皮帝 | 咸豐 | 0.07 | 0.25 / 0.37 / 0.38 |
| C | 同 B，附背景段落 | 咸豐 | 0.97 | 0.00 / 0.02 / 0.98 |

**從舊版對照新版能看出什麼**：💭 E 題（只修正「皮帝」）的第三次重問，分布跟舊版 B 題一模一樣（0.25/0.37/0.38），「皮帝」這個錯字在那一題沒有看得見的影響；舊版 A 題除了「皮帝」還有「康燕」，修正後答案從雍正翻到康熙——最可能讓它答錯的是正確選項本身被打錯。舊版 B 題還有一筆寫這組收據之前、在對話裡非正式跑過的結果（未存檔）：信心 0.08、選道光，跟 E 題這次的浮動一致。

**致謝**：錯字與 README 配對錯誤由 [@MrJev](https://github.com/MrJev) 在 [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2) 指出。

## 限制

計分題只有三題、單一標註者、只測了中文歷史一個領域。每題重問三次只能看出單次呼叫之間的浮動，不能取代更多題目。這遠不足以量化「Jev 的裸記憶知識廣度」，只能支持三個定性觀察：乾淨的題目它可能知道、背景段落讓信心更集中、`state` 有錯時它照樣有把握。歡迎貢獻更大規模、跨領域的裸記憶 vs 給定背景對照測試。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# Pure-recall trivia: with vs. without a supporting passage (English)

> **Correction (2026-09-21)**: this suite's earlier version (2026-09-19) reached a wrong conclusion and has been withdrawn and redone. The prompts it sent contained typos, two of its questions had no single correct answer, and the README's headline cited it by pairing two different questions as if they were one. The typos and the pairing error were reported by a reader in [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2); the counting ambiguity we found while re-checking. Full record in "Correction record for the earlier version" below.

## What this tests

Traditional-Chinese history multiple-choice questions: (A) a commonly-known fact, no supporting passage; (B) an obscure fact, no supporting passage; (C) the same question as B, with a supporting passage included in `state`. The goal is isolating "bare memory" from "reading comprehension given supplied text." Two extra **diagnostic, unscored** items re-ask the earlier version's two questions with only the typos fixed, to tell whether the earlier result came from the typos or from the questions themselves.

## Why this task

The capability map's "not self-contained" side needs a concrete example. A pure-recall question with no supporting passage tests whatever the model happened to memorize during pretraining — a different capability from "can it correctly judge given text."

## Methodology

Single annotator (us) wrote the questions and judged ground truth. This version's rules were paid for by the earlier version's mistakes:

- **Exactly one defensible answer**, under any counting or naming convention. "Which number emperor" questions depend on where you start counting, so this version asks about parent/child relations instead.
- **All options are real people**: B and C's three options are all real Qianlong-era empresses (Qianlong's first empress / Qianlong's mother / Jiaqing's mother), not throwaway distractors.
- **C's passage deliberately mentions all three options**: answering requires understanding who is whose mother, not just matching the one name that appears.
- **Proofread before sending**: `python run.py --dry-run` prints the exact `state` strings without calling the API, and receipts now store each item's sent `state` (the earlier receipts didn't — one reason the typos went unnoticed).
- **Each item asked three times**: Jev has sampling variance, and a single `choice` isn't enough to conclude anything.

## Results

See `runs/2026-09-21.json` (the receipt of record — every number below traces to it). 15 calls, 5,793 input tokens total.

| Case | Question | Context? | Three picks @ confidence | Probabilities (options 1/2/3) | Correct |
|---|---|---|---|---|---|
| A | Qianlong's father (common) | No | Yongzheng @ 1.00 ×3 | 0.00 / 1.00 / 0.00 | ✓ |
| B | Jiaqing's birth mother (obscure) | No | Empress Xiaoyichun @ 0.87 ×3 | 0.01 / 0.08 / 0.91 | ✓ |
| C | Same as B, with passage | Yes | Empress Xiaoyichun @ 1.00 ×3 | 0.00 / 0.00 / 1.00 | ✓ |
| D | Earlier A, typos fixed: "2nd emperor of the Great Qing" | No | Kangxi @ 0.50, 0.51, 0.46 | ~0.65–0.68 / 0.32–0.35 / 0.00 | Unscored |
| E | Earlier B, typos fixed: "7th emperor of the Great Qing" | No | Daoguang @ 0.10, Daoguang @ 0.13, Xianfeng @ 0.07 | ~0.25–0.28 / 0.37–0.42 / 0.30–0.38 | Unscored |

A, B and C returned identical results on all three repeats; D and E drifted slightly between repeats, and E even switched options.

## What this means

**With clean questions, its bare memory is better than we originally wrote**: the common fact at 1.00, the obscure fact at 0.87 with no passage at all. **The passage still helps**: the same obscure question goes from 0.87 to 1.00. But two questions in one domain says nothing about how broad its knowledge is — only that it knew these two, and that **you can't tell in advance whether it knows**. Putting the needed facts in `state` is still the safe move.

**The earlier "confidently wrong" result was caused by our own broken prompt**: the earlier item A misspelled the correct option "康熙" (Kangxi) as "康燕", and Jev picked Yongzheng at 0.90 confidence; with only the typos fixed (D), it picked Kangxi on all three repeats. That's the lesson worth keeping from this suite — **when `state` itself is wrong, it doesn't flag that something's off; it still picks confidently**. Its judgment rests entirely on the text you hand it, and the confidence value won't catch your input errors for you.

**When a question has no single answer, the distribution doesn't pretend otherwise**: for E, "7th emperor," each of the three options matches one counting convention — Jiaqing counting from Nurhaci (the common "twelve Qing emperors" list), Daoguang counting from Hong Taiji's 1636 founding of the Qing name, Xianfeng counting from Shunzhi's 1644 entry into Beijing — and all three repeats came back near-flat, confidence 0.07–0.13. 💭 On its own that looks identical to not knowing; but in the same suite it answered the obscure item B at 0.87, which makes "the question is ambiguous" a more plausible reading than "it doesn't know." D is similar: depending on convention the 2nd emperor is Hong Taiji, Shunzhi or Kangxi, only Kangxi is offered, and it picks Kangxi at just 0.46–0.51.

## Correction record for the earlier version (2026-09-19, withdrawn)

The earlier prompts are preserved in `data/cases.2026-09-19-withdrawn.json` and the receipt in `runs/2026-09-19.json`, not deleted, so anyone can check this record against them.

**What was wrong**:
1. **Typos**: all three `state` strings misspelled 皇帝 ("emperor") as 皮帝, and item A's correct option plus item C's passage misspelled 康熙 (Kangxi) as 康燕 — these typos are what was actually sent to the API.
2. **Counting ambiguity**: the earlier version disclosed that item A's ground truth was contested, but missed that B and C ("7th emperor") had the same problem — each of the three options matches one counting convention.
3. **Mismatched README citation**: the README headline said "the same history question answered wrong at 0.90 with no passage, then correctly at 0.97 with it," but 0.90 was item A (2nd emperor) and 0.97 was item C (7th emperor) — two different questions.

**Earlier numbers** (kept for reference only; no longer the basis for any conclusion):

| Case | Question (with typos) | Choice | Confidence | Probabilities |
|---|---|---|---|---|
| A | 2nd emperor, option (1) misspelled | Yongzheng | 0.90 | 0.04 / 0.93 / 0.03 |
| B | 7th emperor | Xianfeng | 0.07 | 0.25 / 0.37 / 0.38 |
| C | Same as B, with passage | Xianfeng | 0.97 | 0.00 / 0.02 / 0.98 |

**What comparing old and new shows**: 💭 E (only the 皮帝 typo fixed) returned, on its third repeat, exactly the earlier B distribution (0.25/0.37/0.38), so that typo had no visible effect on that question. Earlier A also had the misspelled option, and fixing it flipped the answer from Yongzheng to Kangxi — the most likely cause of the wrong answer is that the correct option itself was misspelled. Earlier B also had one informal run in conversation before the receipt was written (not saved): confidence 0.08, picking Daoguang — consistent with the drift E shows now.

**Thanks**: the typos and the README pairing error were reported by [@MrJev](https://github.com/MrJev) in [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2).

## Limitations

Three scored items, single annotator, one domain (Chinese history) only. Three repeats per item show call-to-call drift; they don't substitute for more items. Nowhere near enough to quantify how broad Jev's bare-recall knowledge is — only enough to support three qualitative observations: it may know a clean question's answer, a passage concentrates its confidence, and a wrong `state` doesn't dent its confidence. Larger, cross-domain bare-recall-vs-context suites are a welcome contribution.

## Tag

🔬 Our own test, real API calls, see `runs/`.
