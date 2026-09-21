🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：`jev-orderby-bench`——獨立測量「拿 Jev 的機率做 SQL `ORDER BY` 排序，這個順序站不站得住腳」，涵蓋校準（ECE/Brier）、排序（Spearman/inversion rate）、不變性檢驗（否定對稱、改述控制、量表鏡像）三個家族，外加一組 Amazon ESCI 真人分級商品相關性的高難度測試
- **原始連結**：[yodablocks/jev-orderby-bench](https://github.com/yodablocks/jev-orderby-bench)（GitHub README，方法論、逐項數字、原始碼都公開）
- **整理者**：本 repo 維護者
- **整理方式**：通篇讀過原始 README（含 20 Newsgroups 主測試、request-shape 批次大小對照、ESCI 高難度測試三個部分），核對每個數字跟它對應的判準門檻

## 為什麼這條特別值得信任

跟我們目前收錄的其他第三方跑分比，這條的方法論紀律明顯更高，值得說明原因：**判準門檻是跑之前就定好的（pre-registered gate）**，不是看到結果之後才決定「算不算過」；**三個不需要標註答案的不變性檢驗**（否定對稱、改述控制、量表鏡像）拿來當獨立於標籤品質之外的交叉驗證；**標籤來源直接寫明並且承認弱點**（20 Newsgroups 的負例只是「作者選了別的板」，不是「人工判定不相關」，作者自己算過大概 2-5% 的污染率並且用逐列排除處理，不是整組刪除）；**批次大小對數字的影響**是專門另外測的一節，不是事後補充。作者也明講：TypeSafe 官方自己發布的 67.8% 是跟兩個前沿模型的平均意見比對、不是校準指標，這條的數字完全獨立於那個數字。

## 轉載範圍

未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

---

# Source record (English)

- **Original benchmark/dataset**: `jev-orderby-bench` — an independent measurement of whether sorting rows by a Jev probability via SQL `ORDER BY` produces a defensible order, covering calibration (ECE/Brier), ranking (Spearman/inversion rate), and invariant checks (negation symmetry, paraphrase control, rubric mirroring), plus a hard-probe test on Amazon ESCI's human-graded product relevance data
- **Original link**: [yodablocks/jev-orderby-bench](https://github.com/yodablocks/jev-orderby-bench) (GitHub README — methodology, per-metric numbers, and source code are all public)
- **Compiled by**: this repo's maintainer
- **Method**: read the full original README (the main 20 Newsgroups test, the request-shape/batch-size comparison, and the ESCI hard-probe section), cross-checked every number against its stated gate threshold

## Why this one earns extra trust

Compared to the other third-party benchmarks already in this repo, this one's methodological discipline is noticeably higher, worth spelling out: **gate thresholds were fixed before any results were seen** (pre-registered), not decided after the fact based on what looked good; **three invariant checks that need no ground-truth labels at all** (negation symmetry, paraphrase control, rubric mirroring) are used as cross-validation independent of label quality; **label provenance is stated explicitly, including its own weaknesses** (20 Newsgroups' negative labels are just "the author posted somewhere else," not "a human judged this unrelated" — the author estimates roughly 2-5% contamination per group and handles it with per-row exclusion, not blanket group removal); **the effect of batch size on the numbers gets its own dedicated section**, not an afterthought. The author also states plainly: TypeSafe's own published 67.8% is agreement against two frontier models' average opinion, not a calibration metric — this project's numbers are entirely independent of that figure.

## Reproduction scope

No full text or paragraph-level translation of the original is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with a link to the original, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).
