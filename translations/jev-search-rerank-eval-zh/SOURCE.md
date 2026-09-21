🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：`jev-search-rerank-eval`——對 Agent Skills Hub 目錄（33,047 筆技能/MCP 伺服器/coding-agent 工具）做分級相關性評測，164 個中英文/混合查詢、9,831 組人工標註的 (query, skill) 配對，比較關鍵字排序、BM25、bge-m3、text-embedding-3-small、Jev 重排序、以及多種 RRF 融合組合
- **原始連結**：
  - [Jason Zhu（@GoSailGlobal）在 X 上的貼文](https://x.com/GoSailGlobal/status/2100877682972258619) —— 本篇的觸發來源，濃縮版三個結論
  - [zhuyansen/jev-search-rerank-eval](https://github.com/zhuyansen/jev-search-rerank-eval)（GitHub README，含完整方法論、逐項數字、可重現腳本，作者本人的倉庫）
- **整理者**：本 repo 維護者
- **整理方式**：先讀貼文原文（執政官提供連結），推文文字本身像截圖轉錄、有重複亂碼段落，追到原始 GitHub repo 後改用 repo README 的精確數字為準，兩邊交叉核對過結論方向一致

## 為什麼這條特別值得信任

跟 `jev-orderby-bench` 同一等級的方法論紀律，而且多做了一件事我們還沒在其他條目看過的：**裁判循環偏誤是直接量出來的，不是用嘴巴提醒**。Jev 本身參與了資料標註（當第一個裁判），同時 Jev 重排序又是被評測的對象——這是自證循環的典型設置。作者用第二個獨立裁判（Claude Haiku）重新標註同一批資料，逐一比較「只用 Jev 標籤」「兩個裁判合併」「只用 Haiku 標籤」三種情況下同一個比較的數字，任何牽涉到 Jev 的結論只採信 Haiku 那一欄。另外還有 30 組人工逐一複核歧異超過一個等級的標註（由另一個模型讀同樣的中繼資料手動評分，18 次站 Jev、2 次站 Haiku、10 次介於兩者之間），跟 `jev-orderby-bench` 的 pre-registered gate 是同一種「先把可能的偏誤量出來，再下結論」的紀律。

## 轉載範圍

未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

---

# Source record (English)

- **Original benchmark/dataset**: `jev-search-rerank-eval` — a graded relevance evaluation over the Agent Skills Hub catalog (33,047 skills/MCP servers/coding-agent tools), 164 Chinese/English/mixed-script queries, 9,831 hand-labeled (query, skill) pairs, comparing a keyword ranker, BM25, bge-m3, text-embedding-3-small, Jev reranking, and several RRF fusion combinations
- **Original links**:
  - [Jason Zhu (@GoSailGlobal)'s post on X](https://x.com/GoSailGlobal/status/2100877682972258619) — the triggering source, a condensed three-conclusion summary
  - [zhuyansen/jev-search-rerank-eval](https://github.com/zhuyansen/jev-search-rerank-eval) (GitHub README, with full methodology, per-item numbers, and reproduction scripts — the author's own repo)
- **Compiled by**: this repo's maintainer
- **Method**: read the original post first (link supplied by the maintainer); the tweet's text itself reads like a screenshot transcription with a repeated, garbled section, so once the original GitHub repo was traced, its README's precise numbers were used as the authority — cross-checked against the tweet and consistent in direction

## Why this one earns extra trust

The same methodological caliber as `jev-orderby-bench`, plus something we hadn't seen in another entry yet: **judge circularity is directly measured, not just flagged verbally.** Jev itself participated in labeling the data (as one judge) while Jev's own reranking is simultaneously the thing being evaluated — a textbook self-grading setup. The author re-labeled the same data with an independent second judge (Claude Haiku), and reports every comparison under three conditions — Jev-only labels, merged labels, Haiku-only labels — trusting only the Haiku column for any claim involving Jev. There's also a 30-pair hand adjudication of disagreements exceeding one level (scored by a different model reading the same metadata: sided with Jev 18 times, Haiku twice, in between 10 times) — the same "measure the possible bias before drawing a conclusion" discipline as `jev-orderby-bench`'s pre-registered gate.

## Reproduction scope

No full text or paragraph-level translation of the original is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with a link to the original, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).
