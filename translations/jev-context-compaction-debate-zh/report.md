🇹🇼 中文｜🇬🇧 English below

# 用 Jev 砍掉 Agent 自己的執行紀錄：一場公開辯論，加上專案自己量出來的答案

## 這組測什麼

跟本 repo 其他條目都不一樣的一種應用：不是「給 Jev 一段內容，問它一題判斷」，而是「讓 Jev 決定 Agent 自己過去的工具呼叫紀錄，哪些可以整條刪掉」。`fast-jev-compaction` 是一個真實、開源、3,482 星的 Claude Code 外掛：取代內建的「叫大模型寫壓縮摘要」，改成對每一筆工具呼叫問 Jev 兩題 `noul`（是否該留下這次呼叫本身／是否該逐字留下這次呼叫的結果），低於門檻的直接刪，留下的一律逐字保留、不改寫。

這條目記錄三件事：①開發者 Tamara Tran 發布時的說法，以及 TypeSafe 共同創辦人 Diogo Almeida 的回應 ②獨立開發者 Theo（t3.gg）的公開反駁 ③最重要的部分——這個專案自己的 issue tracker 裡，其他使用者拿真實對話紀錄重播後量出來的數字，這些數字比任何一方的推特發言都更有說服力。

## 方法論

雙方立場都用原話核實過（見 `SOURCE.md`），不是二手轉述：
- Tamara 的主張：大模型寫摘要是有損的，一個檔案路徑、一句錯誤訊息、一條「絕對不能改某段程式碼」的硬規則都可能在摘要裡消失；Jev 一次打分、只刪不改寫，逐字保留的部分不會失真。
- Theo 的反駁四點：①壓縮不該是單純的過濾器 ②前沿模型（OpenAI/Anthropic/xAI/Google）不透過 API 分享推理過程本身、只給加密payload，中途砍掉歷史等於強迫模型在沒有推理紀錄的狀況下繼續，Anthropic 尤其嚴格 ③前沿模型這一年的訓練本身就把長對話與內建壓縮算進去，模型自己處理壓縮通常比外部規則更好 ④快取經濟學：cache write 比 cache read 貴很多，在 Claude Code／Codex 這類用法裡常佔總花費 60% 以上；從歷史 `1,2,3,4,5,6` 砍掉第 2 筆，等於逼 `3,4,5,6` 全部用最貴的價格重寫一次快取。

比對方式：不是憑感覺選邊站，是去讀這個專案自己的 issue tracker——裡面有其他使用者拿真實 Claude Code session（不是廠商的展示用 demo）重播過 `fast-jev-compaction`，逐筆記錄 Jev 的實際評分。

## 結果

**Issue #26**：8 個真實 session、256 筆工具結果，用預設設定重播，結果**0 筆的 `keepResult` 分數超過 0.3**（滿分 1.0 的「該保留」信心值），幾乎所有工具輸出都被判定可刪。根因很直白：state 給 Jev 看到的只有 `ok, 4213 chars (omitted)` 這種長度佔位字串，從來沒有給它看過工具輸出實際寫了什麼——它是在**看不到內容的情況下**回答「這個內容還需要嗎」。

**Issue #56**：一個乾淨的合成重現——modle 要修一個失敗測試，`bash go test` 的錯誤輸出（正是修復這個 bug 所需要的關鍵資訊）評分只有 0.25，在預設 `keepThreshold: 0.5` 下被判定可以砍。但關鍵發現是：**Jev 對「這幾筆該不該留」的相對排序完全正確**（該留的兩筆分數持續高於不該留的三筆，三次重跑幾乎沒有變動），問題出在 `keepResult` 跟 `keepCall` 兩題的絕對分數落在不同的量尺上，同一個門檻沒辦法同時比較兩者——這是一個外掛程式的校準串接錯誤，不是 Jev 判斷力的問題。

**Issue #52**：把兩題的問法從「這筆輸出是否無法復原」改成「Agent 完成目前任務是否還需要這筆輸出」，同一組資料的結果從全部砍光變成合理留下 40%。也就是說，issue #26 跟 #56 看到的災難性結果，有相當一部分是外掛程式問問題的方式本身有問題，不是 Jev 這顆模型的天花板。

**Issue #25**：一個新的、獨立於前三則的失效類型——「相關性 ≠可復原性」：一筆已經被後續程式碼改版取代的舊估值結果被判定可刪，之後真的需要回頭查那個舊值時，重新執行現在的程式碼只會算出**新的正確值，不是原本那個歷史值**。但這裡有個誠實的亮點：下游的回答模型在被問到那個歷史值時**選擇拒答，沒有編造一個假數字頂替**——這正是本 repo 一直在講的校準訊號的正面案例，只是被包在一則 bug report 裡沒有被兩造任何一方提到。

**針對 Theo 快取經濟學批評的真實工程回應**：另一個專案 fork（`jerryfane/omp-jev-compaction`）實作了「sticky reduction」——不是每次請求都重寫歷史，而是重用同一份逐字重寫過的前綴，只在成長超過 40% 或每 40 次請求時才重新打分一次。在一個真實 16,198 則訊息的 session 上量測：重寫間隔拉長確實省錢，但**真實情境下的重寫頻率（13.3 次請求一次）仍然沒有到打平的門檻（37 次請求一次）**——換句話說，這個批評有實際對策，但目前這個對策自己量出來的結果是「有幫助，還沒完全解決」，不是「已經解決」。

## 這代表什麼

**兩邊的推特發言都只對了一半，專案自己的 issue tracker 給出的答案比誰都細緻**：Tamara 說「大模型摘要會漏東西，Jev 逐字保留不會」——這句話對「留下來的部分」成立，但完全沒處理「什麼東西該被留下來」這個判斷本身可能出錯的問題；Theo 說「這是一個從根本上不理解壓縮的糟糕策略」——這句話命中了快取經濟學跟前沿模型推理payload遺失兩個真實風險，但把 issue #56/#52 顯示的「可修的校準串接錯誤」講成了架構層級的死穴，過頭了。真正該記住的教訓分成三層，而且每一層都可以直接對應到 [`README.md`](../../README.md) 已經講過的原則：

1. **State 必須包含真正要判斷的內容，不能只給長度佔位字串**——這跟本 repo 核心那條軸完全對得上：訊號不自足，判斷自然失準；issue #26 是最乾淨的證據。
2. **`keepCall` 的排序是對的，只是門檻沒有對齊**——這正好呼應 README「不是瞎猜」那節的區分：信心值本身有真實訊號（issue #56 三次重跑排序穩定），出問題的是外掛程式怎麼使用這個訊號，不是 Jev 本身在瞎猜。
3. **有些刪除是不可逆的，而且「重新執行」不保證能復原**——這是本 repo目前唯一一條在講「刪除決策」而不是「回答判斷」的案例，也是為什麼它值得單獨收錄，而不是硬塞進既有的分類/校準框架裡。

**給任何想拿 Jev 做類似用途的人的具體建議**（直接對應到 [`AGENTS.md`](../../AGENTS.md) 新增的警語）：失敗的指令、還沒被取代的計算結果、以及任何「重新執行拿到的答案可能跟原本不一樣」的工具輸出，應該用規則先保護起來，不要交給打分決定；打分用的問題要讓 Jev 看得到內容本身，不能只看到長度；如果快取成本是考量，重寫的前綴要盡量維持逐字不變，不要每次請求都重新打分。

**💭 我們自己的判斷**：現在的預設設定，答案很清楚——不行，前面的數字已經證明它幾乎等於「砍光一切、然後祈禱沒事」。就算套用社群後來抓出的修法（改問法、讓 Jev 看得到內容、規則保護不可復原的結果），我們仍然不會說它已經安全，因為兩件事校準再準也解不掉：一是「判斷錯了但沒聲音」——分類判斷錯了通常馬上看得出來，刪除判斷錯了是幾輪後才隱約浮現，而那時候能解釋原因的證據已經不在了；二是「相關≠可復原」本身就不是信心值能代表的風險類型，再高的信心值都不保證重新執行拿得回原本的答案。我們的立場：可以當成一個你自己選擇性打開、有規則守著、旁邊有人或 fallback 檢查的成本優化選項，用在低風險場景；不建議做成預設開啟、無人監督的正式生產行為——不管以後校準數字進步到什麼程度都一樣。

## 標籤

📚（第三方公開辯論＋第三方專案 issue tracker 裡的真實複現數據；我們沒有自己重跑，但逐條核對過原始英文推文與 issue 全文，且對轉貼內容做了兩處更正，見 `SOURCE.md`。上面「💭 我們自己的判斷」那段是我們自己疊加的綜合結論，不是轉述任何一方的說法）

---

# Using Jev to prune an agent's own execution history: a public debate, and the answers the project's own data gave (English)

## What this covers

An application unlike anything else in this repo: not "give Jev some content, ask it one judgment," but "let Jev decide which of an agent's own past tool calls can be permanently deleted." `fast-jev-compaction` is a real, open-source, 3,482-star Claude Code plugin: instead of asking an LLM to write a compaction summary, it asks Jev two `noul` questions per tool call (should this call stay, should its result stay verbatim) — anything below threshold gets dropped, anything kept stays byte-for-byte unchanged.

This entry records three things: ① developer Tamara Tran's launch claim and TypeSafe co-founder Diogo Almeida's response; ② independent developer Theo (t3.gg)'s public rebuttal; ③ the most important part — real measurements other users posted to the project's own issue tracker after replaying it against real conversation logs, which carry more weight than either side's tweets.

## Methodology

Both sides' positions were verified against their original words (see `SOURCE.md`), not secondhand retellings:
- Tamara's claim: LLM-written summaries are lossy — a file path, an exact error, a hard constraint like "never touch this file" can vanish; Jev scores once and never rewrites, so whatever survives is verbatim.
- Theo's four-point rebuttal: ① compaction shouldn't be a plain filter; ② frontier models (OpenAI/Anthropic/xAI/Google) don't share reasoning traces over the API, only encrypted payloads — truncating history mid-stream forces the model to continue without reasoning continuity, and Anthropic is especially strict about this; ③ frontier labs have already trained this past year's models around long-running sessions and their own compaction, usually outperforming external rule-based approaches; ④ cache economics: cache writes cost far more than cache reads, often over 60% of total spend in Claude Code/Codex-style usage — deleting item 2 from history `1,2,3,4,5,6` forces `3,4,5,6` to be rewritten to cache at full price.

Comparison method: not picking a side by feel, but reading the project's own issue tracker, where other users replayed `fast-jev-compaction` against real Claude Code sessions (not the vendor's own demo) and recorded Jev's actual scores.

## Results

**Issue #26**: replaying default settings against 8 real sessions / 256 tool results found **zero results scored above 0.3** on `keepResult` (out of a 1.0 "should keep" confidence). The root cause is plain: the state Jev sees only shows a length placeholder like `ok, 4213 chars (omitted)` — it has never once seen what the tool output actually said. It's answering "is this still needed" **without being able to see the content**.

**Issue #56**: a clean synthetic reproduction — a model fixing a failing test sees the `bash go test` error output (the exact information needed to fix the bug) scored only 0.25, dropped under the default `keepThreshold: 0.5`. But the key finding is that **Jev's relative ranking of what should stay was entirely correct** (the two "needed" items consistently scored higher than the three "stale" ones across three repeated runs) — the bug is that `keepResult` and `keepCall` return on different scales, so one threshold can't compare both. This is a calibration-wiring bug in the plugin, not a judgment failure in Jev.

**Issue #52**: rewording the two questions from "is this output impossible to recover" to "does the agent still need this to finish the current task" turned a total wipeout into a defensible 40% reduction on the same data. In other words, a substantial share of what issues #26 and #56 saw as catastrophic is how the plugin phrases its questions, not a ceiling on the model itself.

**Issue #25**: a new failure class, independent of the first three — "relevance ≠ reproducibility": a stale valuation result, since superseded by revised code, was judged safe to delete; when that historical value was needed again later, re-running the current code produced **today's correct answer, not the original historical one**. The honest bright spot: the downstream answering model, asked for that historical value, **chose to abstain rather than fabricate a number** — exactly the kind of calibration signal this repo has been tracking throughout, just buried inside a bug report that neither side of the debate mentioned.

**A real engineering response to Theo's cache-economics critique**: a fork of the project (`jerryfane/omp-jev-compaction`) implemented "sticky reduction" — instead of rewriting history on every request, it reuses the same byte-identical rewritten prefix, re-scoring only when growth exceeds 40% or every 40 requests. Measured on a real 16,198-message session: longer rewrite intervals do save money, but **the real-world rewrite frequency achieved (1 per 13.3 requests) still falls short of the break-even point (1 per 37 requests)** — the critique has a real countermeasure, and that countermeasure's own numbers say "helps, not yet solved," not "solved."

## What this means

**Both sides' tweets were half right, and the project's own issue tracker gave a more careful answer than either**: Tamara's "LLM summaries lose things, Jev keeps things verbatim" is true of whatever survives — but says nothing about whether the *decision* of what survives can itself be wrong. Theo's "a strategy that fundamentally doesn't understand compaction" correctly flags two real risks (cache economics, lost reasoning continuity on frontier models) but overreaches by treating what issues #56/#52 show to be a fixable calibration-wiring bug as an architectural dead end. The real lesson has three layers, and each one maps directly onto a principle this repo's [`README.md`](../../README.md) already makes:

1. **The state must include the actual content being judged, not just a length placeholder** — this is exactly this repo's core axis: when the signal isn't self-contained, judgment quality degrades; issue #26 is the cleanest evidence of it.
2. **`keepCall`'s ranking was right; only the threshold wasn't aligned to it** — this echoes the README's "not blind guessing" distinction directly: the confidence number carries real signal (stable ranking across three replay runs in issue #56); what failed was how the plugin used that signal, not the model guessing blindly.
3. **Some deletions are irreversible, and "just re-run it" doesn't guarantee recovery** — this is the only case in this repo so far about a *deletion* decision rather than an *answering* judgment, which is exactly why it earns its own entry instead of being squeezed into the existing classification/calibration framing.

**Concrete guidance for anyone considering Jev for a similar use** (mirrored directly into the new caution added to [`AGENTS.md`](../../AGENTS.md)): failed commands, not-yet-superseded computed results, and any tool output where "just re-run it" might not reproduce the original should be protected by a rule before scoring, not left to a probability threshold; the scoring questions need to show Jev the actual content, not just its length; and if cache cost matters, keep the rewritten prefix as close to byte-identical as possible instead of re-scoring on every request.

**💭 Our own verdict**: with today's default settings, the answer is clear — no. The numbers above already show it's close to "delete almost everything and hope for the best." Even with the community's fixes applied (reworded questions, giving Jev visibility into content, rule-based protection for irreproducible results), we still wouldn't call it safe, because two things don't go away no matter how good the calibration gets: first, a bad deletion fails silently — a wrong classification usually surfaces immediately, a wrong deletion surfaces vaguely several turns later, by which point the evidence that would explain it is already gone; second, "relevance ≠ reproducibility" isn't a risk category confidence values can represent at all — no confidence number guarantees re-running will recover the original answer. Our position: fine as an opt-in, rule-guarded, human-or-fallback-checked cost optimization for low-stakes work; not something we'd recommend running as a default-on, unsupervised production behavior, regardless of how much the calibration numbers improve later.

## Tag

📚 (a third-party public debate plus real reproduction data from a third-party project's issue tracker; we did not re-run this ourselves, but verified every claim against the original English tweets and full issue text, and made two corrections to the pasted content — see `SOURCE.md`. The "💭 Our own verdict" paragraph above is our own synthesis layered on top, not a relay of either side's position)
