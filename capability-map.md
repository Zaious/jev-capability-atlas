🇹🇼 中文｜🇬🇧 English below

# 能力地圖 / Capability Map

這份表格是活的——每收一組新貢獻就更新一行。判準軸見 [README](README.md)。標籤：🔬 我們/貢獻者自己測的、📚 第三方跑分、📖 TypeSafe 官方文件。

This table is living — updated with every new contribution. Axis explained in [README](README.md). Tags: 🔬 our/contributor's own test, 📚 third-party benchmark, 📖 TypeSafe's own docs.

| 任務 / Task | 軸上位置 / Axis position | 結果 / Result | 標籤 | 來源 / Source |
|---|---|---|---|---|
| AG News 主題分類 / topic classification | 訊號自足 / self-contained | 91.0% acc | 📚 | [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) |
| Banking77 意圖分類 / intent classification | 訊號自足 / self-contained | 87.0% acc | 📚 | [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) |
| DAIR Emotion 情緒分類 / emotion classification | 類別重疊（邊界案例）/ overlapping categories (edge case) | 48.0% acc, 信心 0.819 但常錯 / conf 0.819 despite frequent errors | 📚 | [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) |
| ThaiExam 混合科目 / mixed-subject exam | 混合（部分自足部分不） / mixed | 70.7% acc，111 個模型中段班 / mid-pack of 111 | 📚 | [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) |
| 引用支持度判讀 / citation support-checking | 訊號自足 / self-contained | 9/12 支持、0 反駁，低信心正確對應難例 / 9/12 supports, 0 contradicts, low confidence correctly tracked hard cases | 🔬 | [`suites/citation-support-check/`](suites/citation-support-check/) |
| 反諷偵測·同句 / sarcasm, same-clause | 訊號自足 / self-contained | 12/12 對 / correct | 🔬 | [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/) |
| 反諷偵測·跨句 / sarcasm, cross-turn | 訊號自足 / self-contained | 10/10 對 / correct | 🔬 | [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/) |
| 純回憶史實題（無背景） / pure-recall trivia (no context) | 不自足 / not self-contained | 高信心答錯常識題；冷門題低信心 / confidently wrong on a common-knowledge question; low confidence on an obscure one | 🔬 | [`suites/history-recall-context/`](suites/history-recall-context/) |
| 同題有給背景段落 / same question, with context supplied | 訊號自足 / self-contained | 答對，信心 0.97 / correct, conf 0.97 | 🔬 | [`suites/history-recall-context/`](suites/history-recall-context/) |
| 瀏覽器元素選擇路由 / browser element-selection routing | 訊號自足（DOM 快照給齊＋批次平行問）/ self-contained (DOM snapshot given, batched in parallel) | 比 Playwright MCP 快 1.5x、便宜 1.6x / 1.5x faster, 1.6x cheaper——機制解析見 README「為什麼瀏覽器自動化這麼強」/ mechanism explained in README's "why browser automation benchmarks so well" | 📚 | [jev-browser](https://github.com/MahmoudAdelbghany/jev-browser) |
| 稱讚 vs 諷刺（公開專門跑分） / praise vs. sarcasm (published dedicated benchmark) | — | 目前查無 / none found as of this writing | — | 這正是你可以貢獻的空白 / this is an open slot you could fill |

---

## 第三方跑分細節：這些數字到底代表什麼

表格只給一行數字，容易讓人誤判「70.7% 是不是很差」「48% 是不是代表 Jev 很爛」——這節把方法論跟數字背後的意思補齊，不是重複表格。

### ThaiExam：567 題真實泰國標準化考題，vs 110 個其他模型

Jev（`jev-1.13.0`）拿到 **70.7% 準確率**，**0.35 秒/題**、**$0.000029/題**，信心值與實際準確率貼合（期望校準誤差 7.5 個百分點）。

**「111 個模型中段班」不是隨口一句話，是有意義的中段班**：這份考卷混合科目，題目裡混著「答案能自足式從題幹讀出來的閱讀理解題」跟「需要 state 之外的知識回憶/推導的純考古題」——照這個 repo 的核心那條軸，這正是會產出「中等、混合分數」的題型組合，不是隨機結果，是可預測的結果。真正該看的不是「贏了幾個模型」，是**速度快 1.4 個數量級、成本低幾個數量級的情況下，準確率仍然不是墊底**——這代表拿它當一個高流量的前置篩選層（而不是取代一個完整推理模型）是站得住的策略，見 README「為什麼不是狀態機」那節的元件定位論證。

### jev-benchmarks：AG News / Banking77 / DAIR Emotion，vs 專門的本地小型分類器 GLiNER2.5

方法論本身值得稱讚：釘住模型版本、確定性抽樣、配對式 bootstrap 信賴區間、100 例/資料集的類別平衡抽樣——不是隨手跑一次就發表。

- **AG News（4 類新聞主題）**：Jev 91.0% vs GLiNER 70.0%，信賴區間 `[+0.130, +0.290]`，Jev 明顯領先且有統計支持。
- **Banking77（72 類銀行意圖）**：Jev 87.0% vs GLiNER 61.0%，信賴區間 `[+0.220, +0.300]`。72 選一是遠比 4 選一難的區辨任務，Jev 不只準確率贏，端到端延遲（246ms）還些微快過本地 CPU 推論的 GLiNER（296ms）——這組是整份報告裡對 Jev 最有利的結果。
- **DAIR Emotion（6 類情緒）**：Jev 48.0% vs GLiNER 44.0%，信賴區間**含零**，統計上分不出高下。**但信心值的落差才是重點**：Jev 平均信心 0.819，GLiNER 只有老實的 0.438；Jev 有 16% 的題目給「正解」的機率剛好是零，GLiNER 是 0%。

**這三筆合起來的意思**：準確率的勝負，取決於類別本身區隔清不清楚（新聞主題、銀行意圖都是相對乾淨的類別；情緒天生會重疊）——這一半的結果，Jev 沒有明顯輸給一個專門設計的小型分類器，甚至在難的那組（Banking77）贏得更多。但 DAIR Emotion 揭露一個**準確率相近時才看得出來的問題**：Jev 的信心機制在這種類別模糊的任務上失準了，而且失準的方向是「顯得比實際上更有把握」——單看準確率會漏掉這個風險，這也是我們把「型別保證 ≠ 正確性保證」寫進 README 主要論證的原因。

**還沒有人測過、歡迎貢獻的方向**：多模態（Jev 目前只吃文字，官方文件如此記載）、多維度複合評分在真實產品場景的表現、非英語語系（除泰文外）的表現、跨句以上（三輪＋）脈絡的反諷/隱含意圖偵測。

---

## Third-party benchmark details: what these numbers actually mean (English)

A single table row invites the wrong question — "is 70.7% bad?", "does 48% mean Jev is terrible?" This section fills in the methodology and what the numbers actually mean; it doesn't just repeat the table.

### ThaiExam: 567 real Thai standardized-exam questions, vs. 110 other models

Jev (`jev-1.13.0`) scored **70.7% accuracy**, at **0.35s/question** and **$0.000029/question**, with confidence tracking actual accuracy closely (expected calibration error of 7.5 percentage points).

**"Mid-pack of 111 models" isn't a throwaway line — it's a meaningful mid-pack.** This is a mixed-subject exam, blending questions whose answers are self-contained readable comprehension against questions needing knowledge recall/derivation from outside the given state — per this repo's core axis, that exact mix is what predicts a middling, blended score; it isn't a random result, it's an expected one. The number worth focusing on isn't "how many models it beat" — it's that **accuracy holds up as not-last-place while running an order of magnitude faster and multiple orders of magnitude cheaper**. That supports using it as a high-volume pre-filter layer rather than a replacement for a full reasoning model — see the "component, not agent" argument in README's "not a state machine" section.

### jev-benchmarks: AG News / Banking77 / DAIR Emotion, vs. a specialized local classifier (GLiNER2.5)

The methodology itself deserves credit: pinned model versions, deterministic sampling, paired bootstrap confidence intervals, class-balanced sampling at 100 examples per dataset — not a one-off run written up casually.

- **AG News (4-class news topic)**: Jev 91.0% vs. GLiNER 70.0%, CI `[+0.130, +0.290]` — Jev clearly ahead, interval-supported.
- **Banking77 (72-class banking intent)**: Jev 87.0% vs. GLiNER 61.0%, CI `[+0.220, +0.300]`. 72-way discrimination is a much harder task than 4-way; Jev doesn't just win on accuracy — its end-to-end latency (246ms) was slightly faster than GLiNER's local CPU inference (296ms) too. This is the single most favorable result in the whole comparison.
- **DAIR Emotion (6-class emotion)**: Jev 48.0% vs. GLiNER 44.0%, CI **includes zero** — statistically indistinguishable. **But the confidence gap is the real finding**: Jev's mean confidence was 0.819 against GLiNER's honest 0.438; Jev assigned exactly zero probability to the correct answer on 16% of items, versus 0% for GLiNER.

**What the three together mean**: accuracy wins or loses depending on whether the categories themselves are cleanly separated — news topics and banking intents are relatively clean categories, emotions genuinely overlap. On the cleaner half, Jev didn't just hold its own against a purpose-built small classifier, it won more decisively on the harder task (Banking77). DAIR Emotion surfaces a problem **only visible once accuracy is roughly tied**: Jev's confidence mechanism breaks down on this category of task, and breaks down in the direction of appearing more certain than it should — a risk that looking at accuracy alone would miss entirely. This is exactly why README's main argument keeps the "type guarantee ≠ correctness guarantee" distinction front and center.
