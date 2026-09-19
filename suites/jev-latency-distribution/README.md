🇹🇼 中文｜🇬🇧 English below

# 延遲分布：中位數 vs 尾端

## 這組測什麼

不測準確率，測**真實呼叫的延遲分布**——中位數多少、有沒有長尾。直接動機是查證一篇第三方文章（[`translations/jev-benchmark-article-huangserva-zh/`](../../translations/jev-benchmark-article-huangserva-zh/)）的發現：作者在上海對 300 次真實呼叫量測，中位數約 0.7 秒（比官方 0.07-0.5 秒慢），但最慢一次也才 1.5 秒；同時對照一個輕量大模型 Qwen 3.8 Flash，中位數差不多，但最慢一次飆到 32 秒——作者的結論是「Jev 真正贏的不是快，是沒有長尾」。我們從自己的網路環境重跑一次同樣性質的量測。

## 為什麼測這個

這是少數幾個**不需要建立標準答案、成本又低到幾乎可以忽略**的量測——跟其他大部分需要標註、需要設計難例的 suite 不一樣，延遲分布只要真的打 API 就測得到，值得直接動手驗證別人的發現，而不是只讀過去。

## 方法論

30 則簡短的中文句子（各種主題：科技、天氣、美食、運動……刻意混雜簡單、明確的內容，降低「判斷本身很難所以想比較久」這個干擾因素），對每則問同一題 Noul：「這段文字主要是不是在講科技/軟體」。單一標註者（我們自己）出題，這組不判斷答案對不對，只記錄每次呼叫的真實耗時（`time.perf_counter()` 包住 `client.system_one()` 呼叫）。

## 結果

見 `runs/2026-09-19.json`。

| 指標 | 數值 |
|---|---|
| n | 30 |
| 最小值 | 202.3 ms |
| 中位數 | 250.4 ms |
| p95 | 298.5 ms |
| 最大值 | 667.9 ms |

**唯一的離群值是第一次呼叫**（667.9 ms），之後 29 次全部落在 202-298 ms 這個很窄的區間——第一次特別慢，最合理的解釋是連線建立/TLS 交握這類一次性成本，不是隨機出現在中間的「隱藏慢模式」。

## 這代表什麼

**獨立、從不同網路環境重現了同一個結論**：中位數（250ms）落在官方宣稱的 0.07-0.5 秒區間內，比原文章作者在上海量到的 0.7 秒中位數更快；p95 只有 298.5ms，遠遠沒有原文章對照的 Qwen 3.8 Flash 那種「中位數差不多、最慢卻飆到 32 秒」的長尾現象——這組小規模量測支持原文章「Jev 真正的優勢是延遲穩定、不是絕對速度」這個判斷。

## 限制

N=30，遠小於原文章的 300；只測了 Jev 自己，**沒有同場對照另一個便宜大模型**（我們沒有現成的 Qwen/其他模型呼叫基礎設施），所以只能驗證「Jev 本身沒有長尾」這一半，驗證不了「跟便宜大模型比誰的尾端更長」那一半；單一次執行，沒有跨時段重複測量；30 個句子都很簡短、判斷明確，沒有測試複雜輸入或接近 32K 上限的情況會不會影響延遲分布。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# Latency distribution: median vs. tail (English)

## What this tests

Not accuracy — the **real distribution of call latency**: what's the median, and is there a long tail? Direct motivation: verifying a third-party article's finding ([`translations/jev-benchmark-article-huangserva-zh/`](../../translations/jev-benchmark-article-huangserva-zh/)) that measured 300 real calls from Shanghai, finding a ~0.7s median (slower than the official 0.07-0.5s spec) but a worst case of only 1.5s; against a lightweight LLM (Qwen 3.8 Flash) with a similar median but a 32-second worst case, the author's conclusion was "Jev's real win isn't speed, it's the absence of a long tail." We re-ran the same kind of measurement from our own network environment.

## Why this task

One of the few measurements that needs **no ground truth and costs next to nothing** — unlike most suites here, which need labeling and hard-case design, a latency distribution just needs real API calls, making it worth verifying directly rather than only reading about.

## Methodology

30 short Chinese sentences (varied topics — tech, weather, food, sports — deliberately simple and unambiguous, to reduce "hard judgment takes longer to think about" as a confound), each asked the same Noul question: "is this text primarily about technology or software?" Single annotator (us) wrote the items; this suite doesn't score correctness, only records each call's real wall-clock time (`time.perf_counter()` around `client.system_one()`).

## Results

See `runs/2026-09-19.json`.

| Metric | Value |
|---|---|
| n | 30 |
| Min | 202.3 ms |
| Median | 250.4 ms |
| p95 | 298.5 ms |
| Max | 667.9 ms |

**The only outlier is the first call** (667.9 ms); all 29 subsequent calls landed in a tight 202-298 ms band. The most plausible explanation for the first call being slow is one-time connection/TLS-handshake overhead, not a hidden slow mode scattered randomly through the run.

## What this means

**An independent replication of the same conclusion, from a different network environment**: our median (250ms) falls within the official 0.07-0.5s spec, faster than the original article's 0.7s Shanghai-measured median; p95 was only 298.5ms, nowhere near the long-tail pattern the article found comparing against Qwen 3.8 Flash (similar median, but a 32-second worst case). This small-scale measurement supports the article's judgment that "Jev's real advantage is latency stability, not raw speed."

## Limitations

N=30, far smaller than the original article's 300; only Jev itself was tested — **no side-by-side comparison against another cheap LLM** (we have no ready infrastructure for calling Qwen or another model), so this only verifies "Jev itself has no long tail," not "compared to a cheap LLM's longer tail"; a single run, not repeated across different times of day; all 30 sentences were short and unambiguous — this doesn't test whether more complex input or inputs near the 32K limit would affect the latency distribution.

## Tag

🔬 Our own test, real API calls, see `runs/`.
