🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **主題**：用 Jev 幫 Agent 做「上下文壓縮」（刪掉逐字歷史，不是叫大模型寫摘要）——社群一場公開辯論，加上該專案自己 issue tracker 裡的真實複現數據
- **原始連結**：
  - [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction)（開源專案本體，MIT，3,482 星）
  - [Tamara Tran 原貼（X）](https://x.com/tamarajtran/status/2100694549362553153)：「找到 Jev 的完美用例：2026 年了為什麼壓縮還在用大模型寫摘要」
  - Diogo Almeida（TypeSafe 共同創辦人／CEO，X 帳號 [@CompleteSkeptic](https://x.com/CompleteSkeptic)）在同串下的回覆：「YES! free coding agents from designing around the KV cache」——只查得到轉述文字，查無穩定可連結的回覆推文直鏈，且**這是一則回覆，不是我們能獨立確認的「轉推＋按讚」**
  - [Theo（t3.gg）的反駁串（X）](https://x.com/theo/status/2100762304862384257)：「這是一個從根本上不理解壓縮與上下文管理原理的糟糕策略」
  - 專案本身 issue tracker 的四則真實複現／量測報告：[#56](https://github.com/tamaratran/fast-jev-compaction/issues/56)、[#26](https://github.com/tamaratran/fast-jev-compaction/issues/26)、[#52](https://github.com/tamaratran/fast-jev-compaction/issues/52)、[#25](https://github.com/tamaratran/fast-jev-compaction/issues/25)
  - 針對快取失效批評的真實工程回應：[jerryfane/omp-jev-compaction Issue #1「Sticky reduction」](https://github.com/jerryfane/omp-jev-compaction/issues/1)及其實作結果（[PR 對應 commit `f7d1b91`](https://github.com/jerryfane/omp-jev-compaction/issues/1)）
- **整理者**：本 repo 維護者
- **整理方式**：先讀執政官轉貼的兩則中文 X 貼文摘要，逐句去查原始英文推文與帳號身分；找到 `fast-jev-compaction` 後直接讀該專案完整 README 與 issue tracker 裡的複現實驗，交叉比對雙方說法與專案自己量出來的數字

## 對轉貼內容的更正

轉貼的中文貼文把 `@CompleteSkeptic` 講得像是跟「`@typesafeai` 的共同創辦人 Diogo Almeida」是兩個不同的人分別背書——**查證後這是同一個人**：Diogo Almeida 就是 `@CompleteSkeptic`，TypeSafe 的共同創辦人兼 CEO。查得到的是他在 Tamara 那則貼文下的**一則回覆**（"YES! free coding agents from designing around the KV cache"），查無法獨立確認「親自下場轉發點讚」這個動作本身，只確認了回覆文字。

另外，轉貼內容裡「一親自實測、刪掉報錯後 Agent 重跑同一條失敗指令」這段個人測試**查無來源**（沒有帳號、沒有連結），這條沒有收進 `report.md`；但同一種失效模式（預設參數會把失敗測試的錯誤訊息判定為可刪除）在專案自己的 issue #56 裡有版本號、可重跑腳本與三次重複量測的真實複現，我們改用這個有收據的版本。

## 轉載範圍

未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

---

# Source record (English)

- **Topic**: using Jev to do "context compaction" for coding agents — deleting verbatim history instead of asking an LLM to write a summary. A public community debate, plus the project's own issue-tracker data.
- **Original links**:
  - [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) (the open-source project itself, MIT, 3,482 stars)
  - [Tamara Tran's original post (X)](https://x.com/tamarajtran/status/2100694549362553153): "found the perfect use case for @typesafeai Jev: instant compaction in 2026, why is compaction still a summarization prompt?"
  - Diogo Almeida (TypeSafe co-founder/CEO, X handle [@CompleteSkeptic](https://x.com/CompleteSkeptic))'s reply in the same thread: "YES! free coding agents from designing around the KV cache" — only the relayed text was findable, no stable direct permalink to the reply itself, and **this is a reply, not an independently confirmable "retweet + like."**
  - [Theo (t3.gg)'s rebuttal thread (X)](https://x.com/theo/status/2100762304862384257): "This is a terrible compaction strategy that fundamentally doesn't understand how compaction and context management work."
  - Four real reproduction/measurement reports from the project's own issue tracker: [#56](https://github.com/tamaratran/fast-jev-compaction/issues/56), [#26](https://github.com/tamaratran/fast-jev-compaction/issues/26), [#52](https://github.com/tamaratran/fast-jev-compaction/issues/52), [#25](https://github.com/tamaratran/fast-jev-compaction/issues/25)
  - A real engineering response to the cache-invalidation critique: [jerryfane/omp-jev-compaction Issue #1 "Sticky reduction"](https://github.com/jerryfane/omp-jev-compaction/issues/1) and its shipped result (commit `f7d1b91`, reported in the same issue)
- **Compiled by**: this repo's maintainer
- **Method**: started from two Chinese X-post summaries the maintainer pasted in, traced every claim back to the original English tweets and account identities; once `fast-jev-compaction` was found, read its full README and the issue-tracker reproductions directly, cross-checking both sides' claims against the project's own measured numbers.

## Corrections to the pasted content

The pasted Chinese posts framed `@CompleteSkeptic` as if he were a separate co-founder from "`@typesafeai`'s co-founder Diogo Almeida" — **verification found they are the same person**: Diogo Almeida is `@CompleteSkeptic`, TypeSafe's co-founder and CEO. What's findable is **one reply** of his under Tamara's post ("YES! free coding agents from designing around the KV cache"); the claim that he personally "retweeted and liked" it could not be independently confirmed — only the reply text was.

Separately, the pasted content's personal-test anecdote ("deleted the error, then the agent re-ran the same failing command") **has no traceable source** — no handle, no link. It was not carried into `report.md`. The same failure mode (default settings judge a failing test's error message as safe to delete) is, however, reproduced with a version number, a runnable script, and three repeated measurements in the project's own issue #56 — that's the version used instead.

## Reproduction scope

No full text or paragraph-level translation of the original is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with a link to the original, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).
