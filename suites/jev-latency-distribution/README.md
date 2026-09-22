🇹🇼 中文｜🇬🇧 English below

# 延遲分布：中位數 vs 尾端

## 這組測什麼

不測準確率，測**真實呼叫的延遲分布**——中位數多少、有沒有長尾。直接動機是查證一篇第三方文章（[`translations/jev-benchmark-article-huangserva-zh/`](../../translations/jev-benchmark-article-huangserva-zh/)）的發現：作者在上海對 300 次真實呼叫量測，中位數約 0.7 秒（比官方 0.07-0.5 秒慢），但最慢一次也才 1.5 秒；同時對照一個輕量大模型 Qwen 3.8 Flash，中位數差不多，但最慢一次飆到 32 秒——作者的結論是「Jev 真正贏的不是快，是沒有長尾」。我們從自己的網路環境重跑一次同樣性質的量測。

## 為什麼測這個

這是少數幾個**不需要建立標準答案、成本又低到幾乎可以忽略**的量測——跟其他大部分需要標註、需要設計難例的 suite 不一樣，延遲分布只要真的打 API 就測得到，值得直接動手驗證別人的發現，而不是只讀過去。

## 方法論

30 則簡短的中文句子（各種主題：科技、天氣、美食、運動……刻意混雜簡單、明確的內容，降低「判斷本身很難所以想比較久」這個干擾因素），對每則問同一題 Noul：「這段文字主要是不是在講科技/軟體」。單一標註者（我們自己）出題，這組不判斷答案對不對，只記錄每次呼叫的真實耗時（`time.perf_counter()` 包住 `client.system_one()` 呼叫，含網路）。

- **暖機**：正式量測前先打一次呼叫。它要付 TLS 交握與建立連線的成本，不是推論延遲，所以照樣計時、記進收據（`stats.warmup_ms`），但不算進統計。這個做法是讀者在 [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2) 建議、在 [PR #3](https://github.com/Zaious/jev-capability-atlas/pull/3) 實作的。
- **p95 的算法**：排序後取最近秩、不內插。n=30 時落在第 29 個樣本，也就是只比最大值小一名——這個樣本數下它是尾端的指示，不是穩定的估計。

## 結果

正式收據：`runs/2026-09-22.json`（暖機排除後）。舊的 `runs/2026-09-19.json` 是加入暖機排除之前跑的，保留作對照。

| 指標 | 2026-09-22（正式，排除暖機）| 2026-09-19（舊版，第一次呼叫算在內）|
|---|---|---|
| n | 30 | 30 |
| 最小值 | 208.2 ms | 202.3 ms |
| 中位數 | 247.0 ms | 250.4 ms |
| p95 | 280.8 ms | 298.5 ms |
| 最大值 | 313.5 ms | 667.9 ms |
| 暖機呼叫 | 699.3 ms（不計入）| 沒有另外打 |

**舊版唯一的離群值，就是暖機造成的。** 舊版的 667.9ms 是第一次呼叫；這次把第一次呼叫獨立出來，它是 699.3ms，而其餘 30 次全部落在 208–314ms，一個離群值都沒有。當初「第一次特別慢是連線建立的一次性成本」這個推測，這次得到直接證實。

兩次跑出的判斷結果也很穩定：同一句話在兩天的機率最多只差 0.02，沒有任何一題在 0.5 兩側翻轉。

## 這代表什麼

**獨立、從不同網路環境重現了同一個結論**：中位數約 250ms，落在官方宣稱的 0.07-0.5 秒區間內，比原文章作者在上海量到的 0.7 秒更快；排除暖機後最慢一次也只有 313.5ms，遠遠沒有原文章對照的 Qwen 3.8 Flash 那種「中位數差不多、最慢卻飆到 32 秒」的長尾——支持原文章「Jev 真正的優勢是延遲穩定、不是絕對速度」這個判斷。

實務上要注意的是：**第一次呼叫會慢 2–3 倍**。服務剛啟動、或長時間閒置後的第一次請求，應該預期多出幾百毫秒；對延遲敏感的系統可以在啟動時先打一次暖機。

## 限制

- N=30，遠小於原文章的 300；兩次執行分別在 2026-09-19 和 2026-09-22，沒有系統性地跨時段量測。
- 只測了 Jev 自己，**沒有同場對照另一個便宜大模型**，所以只能驗證「Jev 本身沒有長尾」這一半。
- 30 個句子都很簡短、判斷明確，沒有測複雜輸入或接近 32k tokens 上限的情況。
- `get_client()` 只設定了 API key 和逾時，SDK 內部如果有自動重試，重試的時間會被算進那次呼叫的延遲，而且收據裡分辨不出來（這點也是 issue #2 指出的）。這兩次執行都沒有出現失敗，但無法排除個別呼叫曾經重試過。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# Latency distribution: median vs. tail (English)

## What this tests

Not accuracy — the **real distribution of call latency**: what's the median, and is there a long tail? Direct motivation: verifying a third-party article's finding ([`translations/jev-benchmark-article-huangserva-zh/`](../../translations/jev-benchmark-article-huangserva-zh/)) that measured 300 real calls from Shanghai, finding a ~0.7s median (slower than the official 0.07-0.5s spec) but a worst case of only 1.5s; against a lightweight LLM (Qwen 3.8 Flash) with a similar median but a 32-second worst case, the author's conclusion was "Jev's real win isn't speed, it's the absence of a long tail." We re-ran the same kind of measurement from our own network environment.

## Why this task

One of the few measurements that needs **no ground truth and costs next to nothing** — unlike most suites here, which need labeling and hard-case design, a latency distribution just needs real API calls, making it worth verifying directly rather than only reading about.

## Methodology

30 short Chinese sentences (varied topics — tech, weather, food, sports — deliberately simple and unambiguous, to reduce "hard judgment takes longer to think about" as a confound), each asked the same Noul question: "is this text primarily about technology or software?" Single annotator (us) wrote the items; this suite doesn't score correctness, only records each call's real wall-clock time (`time.perf_counter()` around `client.system_one()`, network included).

- **Warm-up**: one call is made before measuring. It pays for the TLS handshake and connection setup, which isn't inference latency, so it's still timed and recorded in the receipt (`stats.warmup_ms`) but excluded from the statistics. A reader suggested this in [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2) and implemented it in [PR #3](https://github.com/Zaious/jev-capability-atlas/pull/3).
- **p95 method**: nearest rank on the sorted sample, no interpolation. At n=30 that's the 29th sample, one rank below the maximum — at this sample size, an indication of the tail rather than a stable estimate.

## Results

Receipt of record: `runs/2026-09-22.json` (warm-up excluded). The older `runs/2026-09-19.json`, run before warm-up exclusion was added, is kept for comparison.

| Metric | 2026-09-22 (of record, warm-up excluded) | 2026-09-19 (older, first call included) |
|---|---|---|
| n | 30 | 30 |
| Min | 208.2 ms | 202.3 ms |
| Median | 247.0 ms | 250.4 ms |
| p95 | 280.8 ms | 298.5 ms |
| Max | 313.5 ms | 667.9 ms |
| Warm-up call | 699.3 ms (excluded) | not made separately |

**The older run's only outlier was the warm-up.** Its 667.9ms was the first call; this time the first call was split out at 699.3ms, and the other 30 all landed in 208–314ms with no outlier at all. The original guess — that the slow first call was a one-time connection-setup cost — is now directly confirmed.

The decisions themselves were stable across the two runs: the same sentence's probability differed by at most 0.02 between the two days, and nothing flipped across 0.5.

## What this means

**An independent replication of the same conclusion, from a different network environment**: a median of about 250ms, within the official 0.07-0.5s spec and faster than the article's 0.7s Shanghai median; with the warm-up excluded, the slowest call was only 313.5ms — nowhere near the long tail the article found comparing against Qwen 3.8 Flash (similar median, but a 32-second worst case). This supports the article's judgment that "Jev's real advantage is latency stability, not raw speed."

The practical caveat: **the first call is 2–3× slower**. Expect a few hundred extra milliseconds on the first request after a service starts or sits idle; latency-sensitive systems can fire a warm-up call at startup.

## Limitations

- N=30, far smaller than the article's 300; the two runs were on 2026-09-19 and 2026-09-22, not a systematic across-time-of-day measurement.
- Only Jev itself was tested — **no side-by-side comparison against another cheap LLM** — so this verifies only the "Jev itself has no long tail" half.
- All 30 sentences are short and unambiguous; complex inputs or inputs near the 32k-token limit weren't tested.
- `get_client()` sets only the API key and timeout, so if the SDK retries internally, the retry time is folded into that call's latency and can't be told apart in the receipt (also raised in issue #2). Neither run had a failure, but a retried individual call can't be ruled out.

## Tag

🔬 Our own test, real API calls, see `runs/`.
