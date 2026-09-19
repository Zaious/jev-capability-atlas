🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：`jev-dspy-lab`——信心門檻棄權（confidence-gated abstention）/「選擇性風險」（selective risk）量測基礎設施，含一組真實 `jev-latest` 跑分結果（客服工單分派，24 題）
- **原始連結**：[jmanhype/jev-dspy-lab](https://github.com/jmanhype/jev-dspy-lab)（GitHub README）
- **整理者**：本 repo 維護者
- **整理方式**：讀原始 README 的方法論說明與其中記錄的一組真實跑分數字（覆蓋率/準確率/Brier score/ECE）

這個 repo 本質上是「量測工具」而非「跑分排行榜」——它示範的是一種方法論（信心門檻怎麼調、覆蓋率跟準確率怎麼取捨），裡面附的那組 24 題數字是一次真實記錄的執行結果，不是大規模跑分，整理時要如實反映樣本數很小這件事。

---

# Source record (English)

- **Original benchmark/dataset**: `jev-dspy-lab` — confidence-gated abstention / "selective risk" measurement infrastructure, including one real recorded `jev-latest` run (support-ticket routing, 24 cases)
- **Original link**: [jmanhype/jev-dspy-lab](https://github.com/jmanhype/jev-dspy-lab) (GitHub README)
- **Compiled by**: this repo's maintainer
- **Method**: read the original README's methodology explanation and the one real run's recorded numbers (coverage/accuracy/Brier score/ECE)

This repo is fundamentally a **measurement tool**, not a leaderboard — what it demonstrates is a methodology (how to tune a confidence gate, how coverage trades off against accuracy). The 24-case numbers included are one real recorded run, not a large-scale benchmark — this write-up is honest about that small sample size.
