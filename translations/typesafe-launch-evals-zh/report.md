🇹🇼 中文｜🇬🇧 English below

# TypeSafe 官方發布評測＋Vercel 獨立驗證＋社群方法論批評

## 這組測什麼

三條線交織：①TypeSafe 自己在發表 Jev 時公布的「workflow evals」（客服、agent trace 可觀測性、資安事件、發票處理四個工作流，對照 GPT-5.6 Luna/Terra/Sol 與 Claude Sonnet 5/Opus 5）②Vercel 把 Jev 換掉自家 `fx` 工具的指令安全審查器（原本用 GPT Luna）後的獨立生產環境結果 ③獨立部落客 Anthony Maio 對整套校準宣稱的方法論批評。dev.to 這篇文章把三條線放在一起、逐條質疑，是目前查到對 Jev 首發數字做得最完整的第三方檢視。

## 方法論

TypeSafe 自己的評測方法：九個模型，對四個工作流打分；**參考答案是 GPT-6 Astra 與 Claude Fable 5.1 兩個模型回答的平均值，不是人工標註**。TypeSafe 自己在發表文裡承認評測「可能帶有一些偏誤」、示範查詢「高度簡化」，也預期首頁那句「193.6x 更快、444.6x 更便宜」的橫幅數字會落在「真實世界收益的高端」——這句自我坦承值得記一筆。

Vercel 的獨立驗證沒有公開資料集或案例數，只有 CEO Guillermo Rauch 跟工程師 Pranit Kumar 在 X 上的貼文：拿 Jev 對照自家 `fx` 工具的指令安全審查器（原本用 GPT-5.6 Luna），結果「快 5-18 倍、更準確」，2026-09-16 起已上線 Vercel AI Gateway。

## 結果

TypeSafe 自己公布的彙整數字（九個模型部分節錄）：

| 模型 | 準確率 | 成本/案例 | 延遲 |
|---|---|---|---|
| Jev | 67.8% | $0.0004 | 0.4 秒 |
| GPT-5.6 Luna | 66.8% | $0.0033 | 12.9 秒 |
| GPT-5.6 Terra | 67.9% | $0.0304 | 10.1 秒 |
| Claude Sonnet 5 | 67.8% | $0.1174 | 78.1 秒 |
| GPT-5.6 Sol | 74.1% | $0.0836 | 23.3 秒 |
| Claude Opus 5 | 73.1% | $0.1761 | 37.8 秒 |

拆到工作流層級，Jev 跟該工作流最強模型的差距從 2.3 分（客服）到 17.3 分（發票處理）不等；聽起來最像「指令安全審查」的資安事件工作流，Jev 是四項裡分數最低的（61.7%），但只落後 Claude Opus 5 4.5 分。

## 這代表什麼

**參考答案本身是兩個 LLM 的平均值，不是人工標註**——這件事直接決定了這整組數字在量什麼：量的是「跟 GPT-6 Astra／Claude Fable 5.1 的共識有多接近」，不是「跟人類判斷有多接近」。兩個前沿模型共同的盲點，任何模型答對反而會被扣分；兩者共同答錯，跟著錯的模型反而加分。對「一個指令安全審查器該擋下什麼」這種問題，真正重要的參考答案是「你團隊裡的人會怎麼判」，不是兩個 LLM 的平均意見。

**分解任務本身就大幅拉高分數，不只是 Jev 的優勢**：把一個大提示詞拆成一串小 Choice/Score/Noul 問題，Luna 的整體分數從 51.9% 衝到 66.8%——這件事套用在你自己現有的審查器上，換不換模型都有效，這正好呼應我們自己在 README「實務建議」那節講的「把判斷拆成獨立原子化問題」。

**「零幻覺」的真正意思，TypeSafe 自己講得很白**：Maio 引用 TypeSafe 官方原話——「我們的數字不是實證出來的。型別匹配是有保證的。」這跟我們自己在 README「不是瞎猜」那節做的區分幾乎一模一樣：型別保證≠正確性保證，連廠商自己都用同一句話承認。Maio 也指出一個我們還沒講過的層次：「個別校準過的判斷，串進 threshold/weight/分支之後，不會自動組成一個校準過的工作流」——這對我們自己建議的複合評分模式（先拆成原子問題，程式碼自己組合權重）是一條重要但書，值得在 README 補一筆。

**信心值不是萬靈丹，但也不是空話**：Maio 指出「訓練程序、獎勵函數、架構、校準方法論全部未公開」（截至 2026-09-15），呼籲要有獨立測試；同時引用 Nathan Flurry 那句「jev 就是一台很聰明的 switch 陳述式」——這正好是我們花了一整節在 README 講清楚的同一種直覺，第三方獨立地講出同一句話，值得記一筆當佐證這個比喻有多自然、又有多容易被誤解成內部運作。

**Vercel 的驗證是目前最有分量的獨立生產環境訊號**，但也要誠實講限制：沒有公開資料集、沒有案例數，只是公司高層跟工程師的社群貼文，不是可重現的跑分——方向上支持 TypeSafe 的數字，但不能當成獨立重跑的證據。

## 標籤

📚（這是我們對第三方文章的批判性整理；文章裡引用的 TypeSafe 原始數字本身是 📖 性質，Vercel 那段是未附資料的獨立生產訊號，三者合起來標一個 📚，細節見上文拆解）

---

# TypeSafe's launch evals + Vercel's independent validation + community methodology critique (English)

## What this covers

Three threads woven together: ① TypeSafe's own "workflow evals" published at Jev's launch (customer service, agent-trace observability, security incidents, invoice processing, against GPT-5.6 Luna/Terra/Sol and Claude Sonnet 5/Opus 5); ② Vercel's independent production result after swapping Jev in for GPT Luna as their `fx` tool's command safety reviewer; ③ independent blogger Anthony Maio's methodology critique of the calibration claims. The dev.to article ties all three together with a critical read — the most complete third-party examination of Jev's launch-day numbers we found.

## Methodology

TypeSafe's own eval scores nine models across four workflows. **Reference labels are the average of GPT-6 Astra and Claude Fable 5.1's responses — not human-labeled.** TypeSafe's own launch post admits the evals "may carry some bias," calls its demo query "highly simplified," and expects the "193.6x faster, 444.6x cheaper" homepage banner to sit at "the higher end of real-world gains" — a disclosure worth noting on its own.

Vercel's independent validation has no public dataset or case count — just posts on X from CEO Guillermo Rauch and engineer Pranit Kumar: Jev tested against their `fx` tool's command safety reviewer (previously GPT-5.6 Luna), found "5-18x faster and more accurate," live on Vercel AI Gateway since 2026-09-16.

## Results

TypeSafe's own published aggregate (selected rows of nine models):

| Model | Accuracy | Cost/case | Latency |
|---|---|---|---|
| Jev | 67.8% | $0.0004 | 0.4s |
| GPT-5.6 Luna | 66.8% | $0.0033 | 12.9s |
| GPT-5.6 Terra | 67.9% | $0.0304 | 10.1s |
| Claude Sonnet 5 | 67.8% | $0.1174 | 78.1s |
| GPT-5.6 Sol | 74.1% | $0.0836 | 23.3s |
| Claude Opus 5 | 73.1% | $0.1761 | 37.8s |

At the workflow level, the gap between Jev and the best model on that workflow ranges from 2.3 points (customer service) to 17.3 (invoice processing). Security incidents — the workflow that sounds closest to "command safety review" — is Jev's lowest raw score (61.7%), but only 4.5 points behind Claude Opus 5.

## What this means

**The reference labels are themselves an average of two LLMs, not human-labeled** — this single fact determines what the whole comparison actually measures: closeness to GPT-6 Astra/Claude Fable 5.1 consensus, not closeness to human judgment. Where both frontier models share a blind spot, a model that's actually right gets marked down; where they share a mistake, a model that shares it gets rewarded. For a question like "what should a command safety reviewer block," the label that actually matters is what a person on your team would say — not the average opinion of two LLMs.

**Decomposition alone drives a large share of the gain — not just a Jev-specific advantage**: splitting one big prompt into a series of small Choice/Score/Noul questions took Luna's aggregate from 51.9% to 66.8%. Applying that to your own existing reviewer helps regardless of which model runs it — which directly echoes our own README guidance to decompose judgments into atomic questions.

**What "zero hallucinations" actually means, in TypeSafe's own words**: Maio quotes TypeSafe's launch post directly — "Our number is not empirical. Schema matching is guaranteed." This is nearly identical to the distinction our own README draws in "not blind guessing": type guarantee ≠ correctness guarantee, stated by the vendor itself in almost the same words. Maio also raises a layer we hadn't covered: "individually calibrated judgments do not automatically compose into a calibrated workflow once you run them through thresholds, weights, and branches" — a real caveat for our own composite-scoring guidance (decompose into atomic questions, combine weights in code) that's worth adding to the README.

**Confidence isn't a cure-all, but it isn't empty either**: Maio notes "the reward function, architecture, training procedure, and calibration methodology are all undisclosed" (as of 2026-09-15) and calls for independent testing; he also quotes Nathan Flurry's "jev is just a really smart switch statement" — exactly the intuition our README spends a whole section unpacking, independently voiced by a third party, worth recording as evidence for how natural (and how easy to over-read) that comparison is.

**Vercel's validation is the strongest independent production signal we currently have**, but honestly: no public dataset, no case count, just executive and engineer social posts, not a reproducible benchmark. It supports TypeSafe's direction but isn't evidence of an independent re-run.

## Tag

📚 (this is our critical organization of a third-party article; the TypeSafe figures it quotes are 📖 in nature, and the Vercel data point is an independent but undocumented production signal — the whole entry is tagged 📚, with the breakdown above making clear which part is which)
