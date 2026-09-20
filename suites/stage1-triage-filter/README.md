🇹🇼 中文｜🇬🇧 English below

# 第一關過濾器：兩階段管線裡，Jev 該扛哪一段

## 這組測什麼

一個真實運作中的個人知識管線：每晚自動抓取一批內容（依既有的監看清單），逐件判斷要「立刻交給 LLM agent 深入處理」、「丟掉」、還是「先擱著」。第一關目前是靠 agent 逐件讀過去判斷，成本跟延遲都壓在這一關。這組測的是：**把第一關換成 Jev，行為會長什麼樣子**——不是測「Jev 能不能重現既有判斷」，是測「這個分流設計本身合不合理」。

這組的真正產出不是命中率，是**三輪問題設計的迭代過程**，每一輪都因為不同的理由失敗，而每次失敗的原因都不是模型判斷力。

## 為什麼測這個

這是能力地圖那條軸上一個典型的候選：判斷所需的訊號（內容本身＋為什麼監看這個主題）可以完全放進 `state`，答案空間窄（三選一或是非），而且**量大、要快、現在用大模型做太貴**——符合 [`AGENTS.md`](../../AGENTS.md) 掃描清單第 1 與第 3 條。

## 方法論

**資料**：15 筆真實歷史案例，從管線自己的登記簿撈出來（真實標題、真實 URL、真實歷史判定與 0-100 內部分數；分數 ≥70＝立即處理、40-69＝擱置、<40＝丟棄）。標籤分布：2 筆立即處理、7 筆擱置、6 筆丟棄——**注意這個 4.3% 的「立即處理」基準率**，是後面第一輪失敗的關鍵。

**內容重建的限制先講**：原始擷取當下的快照存在管線自己的機器上，這次測試拿不到，改用**重新抓取同一個公開網址的現在內容**當 `state`。對變動型頁面（changelog 之類）這代表內容可能已經跟當初擷取時不同，這是本組最大的方法論缺口，下面的結果要帶著這個折扣讀。

**三輪迭代**：

| 輪次 | 設計 | 結果 | 診斷 |
|---|---|---|---|
| 1 | 單題三選一 Choice，判準照規則的書面描述寫 | 15 筆對 7 筆；Jev 判「立即處理」7/15（47%），真實基準率只有 4.3% | 判準描述寫成「高價值＋契合專家＋內容紮實」，聽起來像在描述任何一份正經的技術內容——**基準率完全沒有被問題設計傳達出去** |
| 2 | 同上，但把「這個主題當初為什麼被列入監看」的真實理由放進 `state` | 還是 7 筆；但兩筆真實「立即處理」全部答對、6 筆「丟棄」對 5 筆——**兩端顯著變好**；代價是中間的「擱置」**15 筆裡被選 0 次** | 監看理由是缺的那塊 retrieval，補上去兩端就準了。但兩端判準寫得具體有畫面、中間那項寫得抽象，三選一時抽象的那項會被擠掉 |
| 3 | 放棄三選一。改成**兩題獨立 Noul**（「清楚達到立即處理門檻嗎」「清楚是樣板/無實質內容嗎」），門檻 0.75，兩題都沒過的一律進批次複查 | 見下 | 中間項不需要自己的判準描述——它本來就該是「兩個決斷都不夠有把握」的剩餘集合 |

**第三輪為什麼這樣設計**：三種結果的犯錯代價根本不對稱。「立即處理」判錯＝浪費人的注意力（貴）；「丟棄」判錯＝永久失去，且數個月內擋住重新抓取（也貴，方向相反）；「擱置」判錯＝幾乎零成本，之後會被重新評估。把三個代價完全不同的決定塞進同一題三選一，是在要求模型同時閃避三種不同的錯誤。拆成兩題各自守住一個昂貴的極端、剩下全部交給便宜的人工批次複查，才對得上實際代價結構。

## 結果

見 `runs/2026-09-20.json`（15 筆真實 API 呼叫，共 10,330 input token，約 $0.0004）。

| 分流 | 筆數 | 跟歷史標籤一致 |
|---|---|---|
| 觸發「立即處理」 | 2/15 | 0/2 |
| 觸發「丟棄」 | 1/15 | 1/1 |
| 進批次複查（兩題都沒過門檻） | 12/15 | — |

**兩次觸發「立即處理」的案例，都不是歷史標籤的「立即處理」，但兩筆都值得細看**：

- 一筆是某上游服務宣布**棄用**某個既有機制的 RFC（p=0.85）——完全符合「受監看上游的棄用公告」這個判準，歷史上卻被評成擱置（53 分）。
- 一筆是某協定的**重大版本規格變更**（四個官方 SDK 全部更新、12 個月淘汰期，p=0.92）——歷史分數 69，**距離 70 分的門檻只差 1 分**。

兩筆真實「立即處理」的案例則落在 p=0.51 與 0.60，沒跨過 0.75 門檻——但這兩筆正是最受「重新抓取≠原始快照」影響的類型（變動型頁面），原始擷取當下的觸發點今天可能已經不在頁面顯眼處。

**穩定性**：同一份設計隔天重跑一次，15 筆的分流結果完全相同，機率值差異在 ±0.03 以內。

## 這代表什麼

**三輪失敗，沒有一輪的原因是模型判斷力**：第一輪敗在判準沒有傳達基準率、第二輪敗在中間選項描述太抽象、第三輪的「不一致」則多半來自歷史標籤本身該不該當成正解、以及內容重建的落差。這跟我們在 [`translations/jev-context-compaction-debate-zh/`](../../translations/jev-context-compaction-debate-zh/) 記錄過的第三方案例是同一課：那個專案的 issue #52 發現「改問法讓同一批資料從全部砍光變成合理留下 40%」——**問題設計的槓桿，遠大於模型本身的差異**。

**歷史標籤不該當成正解**：這批標籤是既有政策跑出來的結果，不是獨立的真理。上面那兩筆「誤觸發」看起來更像是抓到了舊政策偏嚴的盲點，不是失手。真要驗收這種任務，比較該問的是「觸發時精準度夠不夠」跟「人看過之後同不同意」，而不是「跟舊系統的標籤對不對得上」。

**不對稱代價應該寫進分流設計，不是塞進判準文字裡**：這是本組最可以帶走的一條。什麼時候該讓模型下決斷、什麼時候該把不確定交還給人，取決於各個結果犯錯的代價，而這件事用程式碼裡的門檻表達，比用判準描述去暗示要可靠得多。

**不確定時的去處要是有界的**：本組第一版設計曾打算把「兩題都沒過」的案例丟進冷凍庫擱置，後來改成進**有界、排程好的人工批次複查**——因為無界的擱置區會長大、會變成沒人再真的看第二眼的地方，而管線本身還有「待裁件過多就停止抓取」的背壓規則，擱置區塞爆等於把整條線停掉。不確定性要導向「盡快用便宜的方式讓人看一眼」，不是導向「假裝解決了」。

## 限制

N=15，遠低於正式驗收所需；`state` 用的是**重新抓取的現在內容**，不是原始擷取快照，對變動型頁面有實質落差（兩筆真實「立即處理」案例正屬此類）；**沒有跟任何便宜大模型（Haiku/Qwen 之類）做同場對照**，所以這組完全無法支持「Jev 比某個小模型更好或更便宜」這類結論；「批次複查」那條路線本身沒有被測到（只測了會不會被正確導向那裡）；門檻 0.75 是憑代價結構挑的起始值，沒有做過門檻搜索；歷史標籤來自單一既有政策，非獨立標註。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# A stage-one filter: which half of a two-stage pipeline should Jev own (English)

## What this tests

A real, running personal knowledge pipeline: every night it captures a batch of content (driven by an existing watchlist) and decides, per item, whether to hand it straight to an LLM agent for deep processing, discard it, or park it. Stage one is currently an agent reading each item — which is where the cost and latency sit. This suite tests **what happens when Jev takes over stage one** — not "can Jev reproduce the existing judgments," but "is this routing design sound at all."

The real output of this suite isn't a hit rate. It's **three rounds of question-design iteration**, each of which failed for a different reason — and not one of those reasons was the model's judgment.

## Why this task

A textbook candidate on this repo's core axis: everything the judgment needs (the content itself, plus *why* this topic is watched) can go into `state`, the answer space is narrow (three-way or yes/no), and it's **high-volume, latency-sensitive, and currently too expensive with a full LLM** — matching items 1 and 3 of [`AGENTS.en.md`](../../AGENTS.en.md)'s scanning checklist.

## Methodology

**Data**: 15 real historical cases pulled from the pipeline's own registry (real titles, real URLs, real historical dispositions and 0-100 internal scores; ≥70 = handle immediately, 40-69 = park, <40 = discard). Label distribution: 2 immediate, 7 parked, 6 discarded — **note that 4.3% base rate for "handle immediately"**, which is what round one failed on.

**A methodology gap, stated up front**: the original capture-time snapshots live on the pipeline's own machine and weren't reachable for this test, so `state` was built from **a fresh fetch of the same public URL today**. For living pages (changelogs and the like) that means the content may differ from what was originally captured. This is the biggest weakness here, and the results below should be read with that discount applied.

**Three rounds**:

| Round | Design | Result | Diagnosis |
|---|---|---|---|
| 1 | One three-way Choice, criteria written from a plausible reading of the documented rules | 7/15 matched; Jev chose "handle immediately" 7/15 (47%) against a real base rate of 4.3% | The criteria read as "high value + good specialist fit + substantive," which describes basically any serious piece of technical content — **the base rate was never conveyed by the question design** |
| 2 | Same, but with the real per-topic "why is this watched at all" reason added to `state` | Still 7/15; but both real "immediate" cases now correct and 5 of 6 discards correct — **both ends improved clearly**; the cost was the middle option being chosen **0 times out of 15** | The watch reason was the missing retrieval piece, and supplying it fixed both ends. But with two concrete, example-laden option descriptions and one vague one, the vague option gets squeezed out |
| 3 | Drop the three-way Choice. **Two independent Noul questions** ("is this clearly over the immediate-handling bar," "is this clearly boilerplate/empty"), threshold 0.75, anything that trips neither goes to batch review | Below | The middle needs no description of its own — it should just be the leftover set where neither decisive answer was confident |

**Why round three is shaped that way**: the three outcomes have wildly asymmetric costs of being wrong. A wrong "handle immediately" burns scarce human attention. A wrong "discard" loses the item permanently and blocks re-capture of that source for months — expensive in the opposite direction. A wrong "park" costs almost nothing, since it gets re-evaluated later anyway. Packing three differently-priced decisions into one three-way question asks the model to dodge three different kinds of error at once. Splitting it into two questions that each guard one expensive extreme, and routing everything else to a cheap human batch review, matches the actual cost structure.

## Results

See `runs/2026-09-20.json` (15 real API calls, 10,330 input tokens total, about $0.0004).

| Routing | Count | Agreed with historical label |
|---|---|---|
| Triggered "handle immediately" | 2/15 | 0/2 |
| Triggered "discard" | 1/15 | 1/1 |
| Routed to batch review (neither trigger fired) | 12/15 | — |

**Neither "handle immediately" trigger matched the historical label, but both are worth a second look**:

- One is an RFC announcing the **deprecation** of an existing mechanism in a watched upstream service (p=0.85) — exactly what "a deprecation notice on a tracked upstream" is supposed to mean, yet historically scored as park-it (53).
- One is a **major protocol version change** (all four official SDKs updated, a 12-month deprecation window; p=0.92) — historically scored 69, **one point below the 70 threshold**.

The two genuine "handle immediately" cases came back at p=0.51 and 0.60, under the 0.75 threshold — but those are precisely the case type most affected by "fresh fetch ≠ original snapshot," since whatever was prominent at capture time may no longer be on the page today.

**Stability**: re-running the same design a day later produced identical routing for all 15, with probabilities within ±0.03.

## What this means

**Three rounds of failure, not one of them about model judgment**: round one failed because the question never conveyed the base rate; round two failed because the middle option's description was too abstract next to two concrete ones; round three's "disagreements" come mostly from whether the historical labels should count as truth at all, plus the content-reconstruction gap. This is the same lesson recorded from a third-party project in [`translations/jev-context-compaction-debate-zh/`](../../translations/jev-context-compaction-debate-zh/), whose issue #52 found that rewording two questions turned a total wipeout into a defensible 40% reduction on identical data — **question design has far more leverage than model choice**.

**The historical labels shouldn't be treated as ground truth**: they're the output of one existing policy, not independent truth. The two "false" triggers above look more like catching that policy's conservative blind spots than like mistakes. The right acceptance questions for this task are "is precision good when it does fire" and "does a human agree on review," not "does it match the old system's labels."

**Asymmetric cost belongs in the routing design, not in the criteria prose**: the most portable finding here. When a model should decide versus when uncertainty should go back to a human depends on what each kind of error costs — and a threshold in code expresses that far more reliably than criteria wording trying to imply it.

**Uncertainty needs a bounded destination**: an earlier version of this design sent "neither trigger fired" cases to cold storage. That got changed to a **bounded, scheduled human batch review**, because an unbounded parking lot grows into a place nothing gets a genuine second look — and this pipeline also has a backpressure rule that halts capture entirely once too many items sit undecided, so flooding the parking lot would stall the whole line. Uncertainty should route to "let a human glance at this cheaply, soon," not to "pretend it's handled."

## Limitations

N=15, far below what a real acceptance test needs; `state` used **freshly re-fetched current content**, not the original capture snapshot, which materially matters for living pages (and both genuine "handle immediately" cases are exactly that type); **no side-by-side comparison against any cheap LLM (Haiku/Qwen-class)**, so nothing here supports a claim that Jev is better or cheaper than a small model at this task; the batch-review path itself was not tested (only whether items get routed there); the 0.75 threshold was chosen from the cost structure, with no threshold search; historical labels come from a single existing policy, not independent annotation.

## Tag

🔬 Our own test, real API calls, see `runs/`.
