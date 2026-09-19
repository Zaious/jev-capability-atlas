🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：〈Jev 單題判斷 vs 拆成多維度分數〉——四組分類任務（合成 B2B 回信、弱訊號任務、真實記帳分類、日文自然語言推論 JNLI），對照「一題問到底」跟「拆成 12-14 個窄問題、本地擬合權重」兩種問法
- **原始連結**：[Jev judge call vs dimension scores（agentjournal.dev）](https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/)
- **整理者**：本 repo 維護者
- **整理方式**：通篇讀過原文，核對四組任務各自的樣本數、統計檢定方式（McNemar 精確檢定＋兩萬次配對拔靴法）跟成本數字

## 為什麼特別記這條

我們自己在 README「實務建議」跟其他多處都建議「把判斷拆成獨立的原子化問題」，這條是第一個**測出這個建議有真實代價**的來源——拆解在三個任務上確實拉高了準確率，但在「困難的良性案例」（看起來像攻擊、其實無害的安全文件/紅隊筆記）上，誤判率從單題的 1.5% 惡化到拆解版本的 37.2%，差了約 25 倍。這條但書值得跟原本的建議放在一起看，不是要推翻它。

---

# Source record (English)

- **Original benchmark/dataset**: "Jev judge call vs. dimension scores" — four classification tasks (synthetic B2B replies, a weak-signal task, real bookkeeping classification, Japanese NLI/JNLI), comparing a single end-to-end question against 12-14 narrow questions with locally fitted weights
- **Original link**: [Jev judge call vs dimension scores (agentjournal.dev)](https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/)
- **Compiled by**: this repo's maintainer
- **Method**: read the full original article, cross-checked each task's sample size, statistical testing method (McNemar's exact test plus a 20,000-sample paired bootstrap), and the cost figures

## Why this one earned its own entry

Our own README's practical-guidance section (and elsewhere) recommends decomposing a judgment into independent, atomic questions. This is the first source we've found that **measures a real cost of that recommendation**: decomposition did raise accuracy on three of the four tasks, but on "hard benign" cases (security documentation or red-team notes that look like attacks but aren't), the false-positive rate worsened from 1.5% with a single question to 37.2% with the decomposed version — roughly 25x worse. This caveat is worth reading alongside the original recommendation, not as a reason to abandon it.
