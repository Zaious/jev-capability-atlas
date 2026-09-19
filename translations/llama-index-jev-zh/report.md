🇹🇼 中文｜🇬🇧 English below

# 用 Jev 幫 LlamaIndex 做重排序：有信賴區間的正面數字

## 這組測什麼

檢索系統常見的兩段式設計：先用便宜的向量檢索撈出候選段落，再用一個更貴、更準的模型重新排序，把真正相關的排到前面。這個專案讓 Jev 扮演第二段的重排序器（一段一段問「這段跟查詢的相關程度」，回傳 0-3 分），跟純向量檢索（MiniLM）做對照，用的是檢索研究常見的 BEIR 標準評測集。

## 方法論

`nfcorpus`（醫學文獻檢索）測試集，323 個查詢；先用 MiniLM 密集檢索撈前 10 名，再用 `JevRerank(mode="score", top_n=5)` 重排，模型走 OpenRouter 的 `jev-latest`。另外用同樣的流程在 `SciFact`（科學事實查核檢索）跑了 300 個查詢當第二個對照集。**重排序一段只問一題、一段一個請求**（不是把多段塞進同一個 state 一次問），理由是原作者明講的：塞太多段會有 context rot，而且 Jev 看不到問題編號、分不出哪個答案對應哪一段。

## 結果

`nfcorpus`：純 MiniLM 的 nDCG@5 是 0.340，加上 Jev 重排序後 0.396，**進步 +0.056（95% 信賴區間 0.042–0.072，不含零）**。整個測試集跑完的花費約 $0.096，換算每個查詢約 $0.0003。`SciFact`：MiniLM 0.629 → MiniLM+Jev 0.715，**進步 +0.086（95% 信賴區間 0.059–0.113）**。作者特別註明：這不是拿來對打 Cohere 那種專業重排序模型排行榜的分數，第一階段用的是 MiniLM 不是更強的檢索器，比較基準是「加不加 Jev 重排序這一步」，不是「Jev 重排序 vs 專業重排序模型」。

## 這代表什麼

**這是目前收錄的跑分裡，唯一一組帶正式信賴區間、而且兩個獨立測試集方向一致的正面結果**——跟我們已經收錄的 `jev-orderby-bench` 放在一起看特別有意思：那組測出 Jev 的機率拿來做真實商品搜尋的分級排序時，四項判準有四項不過；這組測出 Jev 拿來做段落級別的二段式重排序時，兩個資料集都測出統計上顯著的進步。差別很可能就在**問題的顆粒度跟自足性**：`llama-index-jev` 的重排序題目很窄——「這一段文字，跟這個查詢，相關程度多少」，答案完全在給定的 `state`（查詢+這一段）裡；`jev-orderby-bench` 的 ESCI 困難探針要判斷「這個商品符不符合查詢的哪些面向」，牽涉到查詢本身沒明講、需要跟其他候選比較的隱性判斷。兩組合起來，比單看任何一組都更精確地畫出這條核心軸在「排序/檢索」這個應用領域的邊界：**段落級的窄相關性判斷（自足）能贏，商品/多面向的分級相關性判斷（不自足）會輸**。

**一段一問、不批次處理，跟 `jev-orderby-bench` 測出的批次效應也對得上**——那組發現把 40 列塞進同一個 state 會讓排序判準直接不過關，這裡的重排序器設計成一段一個請求，剛好避開了那個問題，不是巧合，是同一個限制逼出的同一種設計選擇。

## 標籤

📚（第三方獨立專案自己做的跑分，我們沒有重跑，數字跟信賴區間直接引用自原始 README）

---

# Reranking for LlamaIndex with Jev: a positive result with confidence intervals (English)

## What this covers

A common two-stage retrieval design: use cheap vector retrieval to pull candidate passages, then a more expensive, more accurate model to rerank them so the genuinely relevant ones surface first. This project uses Jev as that second-stage reranker (asking, per passage, "how relevant is this to the query," returning a 0-3 score), benchmarked against plain vector retrieval (MiniLM) on the standard BEIR evaluation sets used across retrieval research.

## Methodology

The `nfcorpus` test set (medical literature retrieval), 323 queries: MiniLM dense retrieval pulls the top 10, then `JevRerank(mode="score", top_n=5)` reranks them, running `jev-latest` via OpenRouter. The same pipeline was also run on `SciFact` (scientific claim-verification retrieval), 300 queries, as a second control set. **Reranking asks one question per passage, one request per passage** (not several passages stuffed into one state and asked at once) — the author states the reason directly: too many passages in one state causes context rot, and Jev can't see question IDs to tell which answer maps to which passage.

## Results

`nfcorpus`: plain MiniLM scored 0.340 nDCG@5; adding Jev reranking brought it to 0.396, an **improvement of +0.056 (95% CI 0.042–0.072, excludes zero)**. The full test-set run cost about $0.096, roughly $0.0003 per query. `SciFact`: MiniLM 0.629 → MiniLM+Jev 0.715, an **improvement of +0.086 (95% CI 0.059–0.113)**. The author notes explicitly: this isn't a leaderboard comparison against a dedicated reranker like Cohere's — the first stage is MiniLM, not a stronger retriever; the comparison is "with vs. without this Jev reranking step," not "Jev reranking vs. a dedicated reranking model."

## What this means

**This is the only entry in this collection so far with formal confidence intervals, and a positive result consistent across two independent test sets** — worth reading alongside `jev-orderby-bench` already in this repo: that one found Jev's probability, used for graded ranking on real product-search relevance, failed four of six gate conditions; this one found Jev, used for passage-level two-stage reranking, produced a statistically significant improvement on both datasets tested. The likely difference is **question granularity and self-containment**: `llama-index-jev`'s reranking question is narrow — "how relevant is this one passage to this query" — with the answer fully contained in the given `state` (query + that one passage); `jev-orderby-bench`'s ESCI hard probe asks "does this product match which facets of the query," which involves implicit judgment not fully stated in the query and effectively requires comparison against other candidates. Read together, the two entries draw a sharper boundary for this repo's core axis within the search/ranking domain than either does alone: **narrow, passage-level relevance judgments (self-contained) win; graded, multi-facet product relevance judgments (not self-contained) lose.**

**Asking one question per passage instead of batching also lines up with `jev-orderby-bench`'s batch-size finding** — that project found packing 40 rows into one state broke the ranking gate outright; this reranker's one-request-per-passage design happens to avoid that exact problem, which isn't a coincidence — it's the same underlying constraint producing the same design choice independently.

## Tag

📚 (an independent third-party project's own benchmark; we did not re-run it, numbers and confidence intervals are quoted directly from the original README)
