🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：一篇中文長文，整理 Jev 發布一週內社群上「真的跑通」的落地案例（依用途分類，附引用連結），加上作者自己動手做的四次失敗整合嘗試，以及兩輪自製測試（217 個 Jev 專案的可用性自評、100 則中文新聞的信心值校準檢查）
- **原始連結**：[huangserva（@servasyy_ai）在 X 上的貼文](https://x.com/servasyy_ai/status/2101132667056185544)
- **整理者**：本 repo 維護者
- **整理方式**：讀完整篇貼文原文（使用者逐字轉貼提供），逐條核對文中引用的具體數字是否跟我們自己已經收錄、獨立查證過的條目一致（`translations/typesafe-launch-evals-zh/` 的 67.8% 準確率、`capability-map.md` 的 jev-ultrafast 9.450→7.092 秒、`translations/jev-context-compaction-debate-zh/` 的 state 截斷根因），另外針對文中「延遲沒有長尾」這個具體、低成本可驗證的發現，自己跑了一組 30 筆的真實延遲量測（見 [`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/)）

## 查證限制

X 平台內容同樣沒有工具能直接自動抓取核對——原文由 repo 維護者本人在對話中親自轉貼、逐字提供，不是我們自己爬到的。

## 為什麼這條特別值得信任

這篇文章本身的方法論紀律，在我們查證過的所有第三方來源裡數一數二：明確排除「純觀點、教程、上架公告、沒有運行證據的構想」；誠實列出四次失敗案例（不是只報喜不報憂）；兩輪自製測試各自附上樣本數限制與可信度但書；文中引用的每一個具體數字，我們核對後都跟自己獨立查出來的結果一致——這種跨來源收斂程度，在這整批收錄裡是最高的一次。

---

# Source record (English)

- **Original benchmark/dataset**: a long-form Chinese article organizing which real-world Jev applications had actually shipped within Jev's first week (categorized by use case, with citations), plus the author's own four failed integration attempts and two self-run tests (a self-assessment of 217 Jev projects' real usability, and a confidence-calibration check on 100 Chinese news items)
- **Original link**: [a post by huangserva (@servasyy_ai) on X](https://x.com/servasyy_ai/status/2101132667056185544)
- **Compiled by**: this repo's maintainer
- **Method**: read the full original post (pasted in verbatim by the maintainer), cross-checked every specific number cited against entries we've already independently verified and collected (`translations/typesafe-launch-evals-zh/`'s 67.8% accuracy figure, `capability-map.md`'s jev-ultrafast 9.450→7.092s figures, `translations/jev-context-compaction-debate-zh/`'s state-truncation root cause), and separately ran our own 30-item real latency measurement (see [`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/)) to check the article's "no long tail" finding, which was concrete, low-cost, and independently testable.

## Verification limitation

No tool currently available to us can fetch and independently verify X/Twitter content directly. The source text here was pasted in verbatim by the repo's maintainer during conversation, not scraped by us.

## Why this one earns extra trust

This article's own methodological discipline is among the best of any third-party source we've verified: it explicitly excludes "pure opinion, tutorials, launch announcements, and ideas with no running evidence"; it honestly reports four failed attempts, not just successes; both self-run tests state their own sample-size limits and confidence caveats; and every specific number it cites, once we checked it, matched what we'd independently found ourselves. That level of cross-source convergence is the highest of anything collected in this repo so far.
