🇹🇼 中文｜🇬🇧 English below

# 拆解判斷會拉高準確率，但也可能讓誤判率暴增：一份量出代價的跑分

## 這組測什麼

我們一路都在建議「把一個大判斷拆成好幾個窄的、原子化的問題，用程式碼組合結果」——這條也是 TypeSafe 官方 workflow evals 裡讓分數大幅跳升的主因（見 `translations/typesafe-launch-evals-zh/`）。這份跑分直接測這個建議：拿同一批任務，一種問法是「一題問到底」（單一 Jev Choice/Score，直接給結論），另一種是拆成 12-14 個窄問題，每題各自打分，再用程式碼在本地擬合權重組合成最終判斷，比較準確率、成本，還有一個大部分人不會想到要測的東西：**兩種問法各自的誤判模式長得完全不一樣**。

## 方法論

四組任務，樣本數由小到大：合成 B2B 業務回信（200 列）、刻意設計成訊號薄弱的任務（300 列）、真實記帳分類（4,907 筆訓練／2,101 筆測試）、日文自然語言推論 JNLI（8,000 筆訓練／2,434 筆測試，三分類）。每組都先跑免費基準線（字元 n-gram、詞彙二元組、多數類別）打底，再比較單題 Jev 跟拆解版本；顯著性用 McNemar 精確檢定跟兩萬次配對拔靴法驗證，不是看一次跑分的差異就下結論。額外用 339 筆刻意找出來的「困難良性案例」（安全文件、紅隊筆記——內容看起來危險但其實無害）測誤判率。

## 結果

四組任務裡三組拆解版本準確率較高：弱訊號任務從 64.7% 進步到 74.0%（+9.0 個百分點，p=0.0050，但字元二元組基準線同樣測到 74.0%——免費的方法打平了要花錢的拆解版本）；真實記帳分類單題只有 0.3998（12 選項單題判斷本身就是弱項，原文特別強調「絕對不要用一題問十二個選項」），拆解版本進步到 0.9105，但詞彙二元組基準線就有 0.9491，疊加拆解分數跟基準線的堆疊模型才到 0.9695；日文 JNLI 單題 0.837，拆解版本 0.9076（+7.03 個百分點，95% 信賴區間 [+5.67, +8.38]，p<1e-4）——這是拆解版本唯一一組明顯、乾淨贏過免費基準線（多數類別基準只有 0.553）的任務。

**代價在困難良性案例上出現**：339 筆安全文件/紅隊筆記，單題 Jev 的誤判率 1.5%，拆解版本 37.2%，字元二元組基準線 43.4%——**拆解版本誤判率是單題的約 25 倍，而且退化到接近免費基準線的水準**。原因是拆出來的維度裡，「是否混淆編碼」「是否藏在內容裡」這類子問題，對真正的惡意文字跟合法的安全文件給出同樣高的分數——分不清楚意圖，只看得到表面特徵。作者試過四種修法（增加訓練資料、調整門檻、把單題 Jev 的機率也當一個特徵加進去、拿掉表面特徵型的維度），全部失敗或讓結果更差。

**成本**：單題約 444-619 token／列（每千列 $0.019-0.026）；拆解版本約 1,010-1,154 token／列（每千列 $0.042-0.048），貴 1.6-2.3 倍。整個實驗共打了 25,174 次 Jev 請求，花費約 $1.43。

## 這代表什麼

**拆解這個建議本身沒有錯，但「拆解一定比較準」這句話錯了**——正確的講法是「拆解能不能贏，取決於單題判斷是不是真的弱」。作者自己整理的優先順序，我們認為值得直接搬進 README：先試免費的 n-gram/TF-IDF 基準線；單題 Jev 夠強就停在這裡；只有在單題判斷真的弱的地方才拆解；拆解出來的維度可以跟便宜模型的機率疊加成堆疊模型，前提是兩者的錯誤不重疊；要做安全把關（guardrail），用單題 Jev 配嚴格門檻當主判斷，拆解版本只能當第二意見，不能單獨扛主判斷。

**多分類問題不要一題問到底**——記帳分類那組單題 12 選項只有 0.3998，是全部任務裡最差的結果，這條原本我們沒特別強調過，值得補進去。

**作者自己也誠實承認一個校準上的誤判**：一開始以為「信心 ≥0.9 的案例應該有九成準」，重新分組驗證後發現只有 72.2%——**這跟我們在 README「不是瞎猜」那節反覆講的「校準是母體層級的統計性質，不保證任何單一案例」是同一個教訓，這次是連做這份跑分的人自己都先信錯了一次，再自己抓出來**，某種程度上比我們自己講這句話更有說服力。

## 標籤

📚（第三方獨立跑分，方法論、逐項數字、統計檢定方式全部公開；我們沒有重跑，通篇核對過原文的樣本數與統計方法）

---

# Decomposition raises accuracy but can blow up false positives: a benchmark that measured the cost (English)

## What this covers

We've been recommending, throughout this repo, breaking one large judgment into several narrow, atomic questions and combining the results in code — this is also the main driver behind the score jump in TypeSafe's own launch workflow evals (see `translations/typesafe-launch-evals-zh/`). This benchmark tests that recommendation directly: on the same tasks, one approach asks "one question, straight to the conclusion" (a single Jev Choice/Score), the other decomposes into 12-14 narrow questions, each scored separately, combined via locally fitted weights — comparing accuracy, cost, and something most people wouldn't think to test: **the two approaches fail in completely different ways.**

## Methodology

Four tasks, increasing in sample size: synthetic B2B business replies (200 rows), a deliberately weak-signal task (300 rows), real bookkeeping classification (4,907 train / 2,101 test), and Japanese NLI/JNLI (8,000 train / 2,434 test, 3-class). Each starts with a free baseline (character n-grams, word bigrams, majority class) before comparing single-question Jev against the decomposed version; significance is verified with McNemar's exact test and a 20,000-sample paired bootstrap, not a conclusion drawn from a single run's difference. A separate set of 339 deliberately chosen "hard benign" cases (security documentation, red-team notes — content that reads as dangerous but isn't) tests false-positive rate.

## Results

Decomposition won on accuracy for three of the four tasks: the weak-signal task went from 64.7% to 74.0% (+9.0 points, p=0.0050) — but the character-bigram baseline also scored 74.0%, a free method matching the paid decomposed one; real bookkeeping classification scored only 0.3998 single-question (a 12-option single call is itself a weak setup, and the article stresses "never ask one question with twelve choices"), improving to 0.9105 decomposed, but the word-bigram baseline alone scored 0.9491, and only a stacked ensemble of decomposition scores plus the baseline reached 0.9695; Japanese JNLI scored 0.837 single-question, 0.9076 decomposed (+7.03 points, 95% CI [+5.67, +8.38], p<1e-4) — the only task where decomposition clearly and cleanly beat the free baseline (majority-class baseline: 0.553).

**The cost shows up on hard benign cases**: across 339 security-documentation/red-team-notes rows, single-question Jev's false-positive rate was 1.5%, the decomposed version's was 37.2%, and the character-bigram baseline's was 43.4% — **the decomposed version's false-positive rate is roughly 25x worse than the single question, degrading to near the free baseline's level.** The cause: sub-questions like "is this obfuscated encoding" or "is this hidden in the content" scored equally high for genuinely malicious text and legitimate security documentation alike — they catch surface features, not intent. The author tried four fixes (more training data, threshold calibration, adding the single-question Jev probability as a feature, dropping the surface-feature dimensions) — all failed or made results worse.

**Cost**: single-question runs about 444-619 tokens/row ($0.019-0.026 per 1,000 rows); the decomposed version about 1,010-1,154 tokens/row ($0.042-0.048 per 1,000 rows), 1.6-2.3x more expensive. The full experiment made 25,174 Jev requests total, costing about $1.43.

## What this means

**The decomposition recommendation itself isn't wrong — but "decomposition is always more accurate" is.** The correct statement is "whether decomposition wins depends on whether the single-question judgment is genuinely weak." The author's own stated priority order is worth carrying directly into this repo's README: try a free n-gram/TF-IDF baseline first; stop there if single-question Jev is already strong; decompose only where the single call is genuinely weak; decomposed dimensions can be stacked with a cheap model's probability, but only where their errors don't overlap; for guardrails, use single-question Jev with a strict threshold as the primary judgment and treat the decomposed version as a secondary opinion only, never the sole gate.

**Don't ask one question with many options for multi-class problems** — the bookkeeping task's 12-option single call scored 0.3998, the worst result across every task here. We hadn't specifically flagged this before; worth adding.

**The author's own honest admission about calibration is worth keeping**: an initial belief that "≥0.9 confidence cases should be about 90% accurate" turned out, after regrouped validation, to be only 72.2% — **the exact same lesson our README's "not blind guessing" section repeats (calibration is a population-level property, not a guarantee for any single case), except here it's the person running the benchmark who believed it wrong first and caught it themselves** — arguably more persuasive than us stating the same line ourselves.

## Tag

📚 (an independent third-party benchmark; methodology, per-item numbers, and statistical methods are all public; we did not re-run it, but read the full article and cross-checked its sample sizes and statistical methods)
