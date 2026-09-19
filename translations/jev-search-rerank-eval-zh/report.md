🇹🇼 中文｜🇬🇧 English below

# 單獨用 Jev 重排不贏向量檢索，但融合著用會贏——連裁判循環偏誤都量出來了

## 這組測什麼

Jev 上線後一堆專案拿它做搜尋重排序（見我們自己收錄的 `jev-orderby-bench`、`llama-index-jev`），這份跑分直接測：**單獨拿 Jev 重排，真的贏得過一個好的向量檢索嗎？**而且不只測這個——它同時測了一個大部分跑分不會測的東西：如果評分標準本身有一部分是 Jev 自己標的，這個「Jev 贏了」的結論還站得住嗎？

## 方法論

Agent Skills Hub 目錄（33,047 筆技能/MCP 伺服器/工具），164 個真實查詢（中文同義詞 80、英文 45、混合語言 38），跟四種檢索器（該站自己的關鍵字排序 `ash`、BM25、bge-m3、text-embedding-3-small）各自的前 30 名聯集起來，總共 9,831 組 (query, skill) 配對進入標註池。**標註用兩個獨立裁判**：Jev（`score` 題，0-3 分級）跟 Claude Haiku（獨立溫度 0、同一個量表），兩者一致率：完全一致 53.1%、差一級以內 98.0%、加權 kappa 0.71。歧異超過一級的配對，另外由第三個模型（Claude，跟兩個裁判用同一批中繼資料）逐一手動複核。最終標籤：有人工複核用人工複核；兩個裁判一致用一致值；不一致時用**沒四捨五入的平均值**（刻意不四捨五入，避免每次五五波都自動採信比較寬鬆的裁判）。

**核心設計**：每個系統都在三種標籤集下重新評分一次——用 Jev 標的、兩個裁判合併、只用 Haiku 標的——任何牽涉到 Jev 表現的結論，只看 Haiku-only 那一欄，因為那一欄 Jev 完全沒有參與標註過程。

## 結果

**單獨用 Jev 重排（在 bge-m3 的前 30 名上重排），不贏純向量檢索**：合併標籤下只贏 +0.012 NDCG@10（95% 信賴區間 [-0.013, +0.037]，跨零，不顯著）；**拿掉 Jev 自己標註的循環偏誤，只看 Haiku 判的分數，其實是 -0.028**（信賴區間 [-0.052, -0.004]，顯著更差）。但 MRR 跟前三命中率確實明顯進步（0.872→0.953、0.768→0.862）——**Jev 很會把最相關的那一條頂到第一名，但後面幾名基本是重新洗牌，整體排序品質沒有真的變好**；在只看 Haiku 標籤時，連前三命中率的進步都消失（變成 -0.043）。

**裁判循環偏誤，數字化了**：同一個比較（`jev-score(bge-m3@30)` 對比 `bge-m3`），只用 Jev 的標籤時 Jev 領先 +0.053，兩個裁判合併時降到 +0.012，只用 Haiku 的標籤時直接變成 **-0.028**——同一組資料、同一個比較，換裁判整個符號翻過來。

**真正穩贏的是融合，不是取代**：把 Jev 的重排分數跟 bge-m3 的排序做 RRF（倒數排名融合），NDCG@10 到 0.864，比純 bge-m3 高 +0.090（合併標籤）、拿掉 Jev 自己標註的循環偏誤後仍有 +0.064（信賴區間 [+0.052, +0.077]，顯著）——三種裁判組合下全部成立，是整份跑分唯一一個在任何標籤集下都站得住的正面結論。代價：每次查詢多打一次 API，約 $0.0002。

**一個意外但重要的補充發現**：在弱的候選名單（該站自己的關鍵字排序 `ash`）上重排，Jev 反而是比 bge-m3 更好的重排器（+0.060 NDCG@10，Haiku-only 標籤下仍有 +0.037）——脈絡會反過來：候選名單本身弱的時候，Jev 重排有價值；候選名單本身已經是強語意檢索時，Jev 單獨重排加不了多少分。

**暴露自家系統的真正瓶頸**：該站上線的關鍵字排序，召回率（相關項目有沒有進入候選名單）只有 0.497，bge-m3 有 0.708——重排序救不了進不了候選池的結果；用 bge-m3 重排關鍵字排序的前 30 名甚至讓結果變差（-0.026），因為候選池本身就是錯的，怎麼重排都是矮子裡挑將軍。中文同義詞查詢是關鍵字排序最弱的地方（0.539 對比 bge-m3 的 0.756），英文查詢差距小很多。

## 這代表什麼

**跟本 repo 已收錄的搜尋/排序條目放在一起，畫出一個更完整、更實用的圖**：`jev-orderby-bench` 測出 Jev 的機率在困難、多面向的商品相關性排序上校準會垮；`llama-index-jev` 測出窄、段落級的相關性重排序有統計顯著的進步；這篇補上第三種、也是最貼近實務的模式——**在一個強的候選名單上，單獨用 Jev 重排幾乎不會贏，但把它的分數當一個額外訊號、用 RRF 這類簡單融合方式跟既有排序合起來用，會穩定贏，而且贏的幅度扣掉自證循環之後依然顯著**。這跟我們一路在講的「Jev 是元件不是主角」完全吻合，這裡多了一個具體、量化過的融合公式可以直接抄。

**裁判循環偏誤這件事，值得回頭連結我們自己對 TypeSafe 官方發布評測的質疑**（見 `translations/typesafe-launch-evals-zh/`：TypeSafe 自己的參考答案是兩個前沿模型的平均值，不是人工標註）——這篇是目前收錄裡把同一種風險**量化得最乾淨的一次**：同一個比較，換一個跟被評測系統無關的裁判，結論從「贏」變成「輸」。任何拿 Jev（或任何模型）自己的判斷去產生評測標籤、又同時評測那個模型表現的場景，都該問一句「拿掉這個模型自己的標註，結論還站得住嗎」——這篇給了一個可以直接照抄的驗證流程。

**成本效益很清楚**：融合方案每次查詢多花約 $0.0002，換到 +0.064 到 +0.090 的 NDCG@10 進步，而且三種裁判組合下都成立——這是我們目前收錄裡少數幾個「代價小、效果穩、經得起自證循環質疑」的正面案例之一。

## 標籤

📚（第三方獨立跑分，方法論、原始碼、逐項數字全部公開；我們沒有自己重跑，但通篇核對過原始 repo README 跟觸發這條的原始貼文，兩者結論方向一致）

---

# Jev alone doesn't beat vector retrieval for reranking, but fusing it does — with judge circularity measured (English)

## What this covers

Once Jev launched, a lot of projects started using it for search reranking (see our own `jev-orderby-bench` and `llama-index-jev` entries). This benchmark tests directly: **does Jev alone, as a reranker, actually beat a good vector retriever?** And it tests something most benchmarks don't: if part of the scoring rubric is itself labeled by Jev, does the "Jev wins" conclusion survive?

## Methodology

The Agent Skills Hub catalog (33,047 skills/MCP servers/tools), 164 real queries (80 Chinese synonyms, 45 English, 38 mixed-script), pooled from the top-30 of four retrievers (the site's own keyword ranker `ash`, BM25, bge-m3, text-embedding-3-small) into 9,831 (query, skill) pairs for labeling. **Two independent judges label the pool**: Jev (a `score` question, 0-3 scale) and Claude Haiku (independent, temperature 0, same scale) — agreement: exact 53.1%, within one level 98.0%, weighted kappa 0.71. Pairs disagreeing by more than one level get hand-adjudicated by a third model (Claude, reading the same metadata as the two judges). The final label: hand adjudication where present; the shared value where judges agree; otherwise the **un-rounded mean** (deliberately not rounded, to avoid always crediting the more generous judge on a coin-flip disagreement).

**Core design**: every system is re-scored under three label sets — Jev-only, merged, Haiku-only — and any conclusion involving Jev's own performance is read only from the Haiku-only column, since Jev had no part in producing those labels.

## Results

**Jev alone, reranking bge-m3's top-30, does not beat plain vector retrieval**: +0.012 NDCG@10 under merged labels (95% CI [-0.013, +0.037], crosses zero, not significant); **removing the circularity of Jev labeling its own comparison, using Haiku-only scores, it's actually -0.028** (CI [-0.052, -0.004], significantly worse). But MRR and top-3 hit rate do improve clearly (0.872→0.953, 0.768→0.862) — **Jev is good at promoting the single most relevant result to first place, but the rest get reshuffled without genuinely improving** — and under Haiku-only labels, even the top-3 gain disappears (becomes -0.043).

**Judge circularity, quantified**: the same comparison (`jev-score(bge-m3@30)` vs. `bge-m3`) reads +0.053 under Jev-only labels, drops to +0.012 under merged labels, and flips to **-0.028** under Haiku-only labels — same data, same comparison, the sign reverses depending purely on who's judging.

**What actually wins reliably is fusion, not replacement**: RRF-fusing Jev's rerank score with bge-m3's ranking reaches 0.864 NDCG@10, +0.090 over plain bge-m3 (merged labels), and still +0.064 (CI [+0.052, +0.077], significant) after removing Jev's own labeling circularity — holding under all three judge configurations, the only positive finding in this benchmark that survives every label set. Cost: one extra API call per query, about $0.0002.

**An unexpected but important addendum**: reranking a weak candidate list (the site's own keyword ranker, `ash`) with Jev actually beats reranking the same list with bge-m3 (+0.060 NDCG@10, still +0.037 under Haiku-only labels) — the context flips: Jev's rerank adds value when the base candidate list is weak; it adds little when the base list is already strong semantic retrieval.

**Exposes the real bottleneck in their own shipped system**: the keyword ranker's recall (whether relevant items even enter the candidate pool) is only 0.497, versus bge-m3's 0.708 — no reranker can rescue results that never made the pool; reranking the keyword ranker's top-30 with bge-m3 even makes results worse (-0.026), because the candidate pool itself is wrong, so reranking is just picking the best of a bad set. Chinese synonym queries are the keyword ranker's weakest spot (0.539 vs. bge-m3's 0.756); English queries are much closer.

## What this means

**Read alongside this repo's other search/ranking entries, this draws a more complete, more practical picture**: `jev-orderby-bench` found Jev's probability breaks down on hard, multi-facet graded product relevance; `llama-index-jev` found narrow, passage-level reranking improves significantly. This adds a third, more practically relevant pattern — **on top of a strong candidate list, Jev alone as a reranker barely wins, but treating its score as one additional signal and fusing it with the existing ranking via something as simple as RRF wins reliably, and the margin survives removing the self-grading circularity.** This lines up exactly with this repo's recurring "component, not agent" framing — this entry adds a concrete, quantified fusion formula worth copying directly.

**The judge-circularity finding is worth linking back to our own skepticism of TypeSafe's own launch evals** (see `translations/typesafe-launch-evals-zh/`: TypeSafe's own reference labels are an average of two frontier models, not human-labeled) — this is the **cleanest quantification of that exact risk** in this collection so far: the same comparison, with the judge switched to one unrelated to the system under test, flips from "wins" to "loses." Any scenario where a model's own judgments help produce the eval labels that then evaluate that same model's performance deserves the question "does the conclusion survive removing this model's own labels" — this benchmark hands you a copyable procedure for asking it.

**The cost-benefit is clean**: the fusion approach costs about $0.0002 extra per query for a +0.064 to +0.090 NDCG@10 gain, holding under all three judge configurations — one of the few positive findings in this collection that's both cheap and survives circularity scrutiny.

## Tag

📚 (an independent third-party benchmark; methodology, source code, and every number are public; we did not re-run it, but read the full repo README and the original triggering post, both consistent in direction)
