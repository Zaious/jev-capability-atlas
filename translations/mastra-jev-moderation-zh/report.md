🇹🇼 中文｜🇬🇧 English below

# 生產環境的內容審核：9/9 抓到、49 則真實訊息 0 誤判

## 這組測什麼

Mastra 這個 agent 框架內建的審核處理器，做法是問一個大模型「這則訊息該不該擋」，再從模型寫的自由文字裡解析出結論——這個專案指出一個具體的失效模式：**碰到真正惡意的輸入時，小模型有時候恰好回不出能解析的格式**，這種時候處理器選擇放行（fail open），剛好在最需要擋下來的時候失靈。這個專案拿 Jev 換掉這一段：問一題型別化的是非（該不該擋）加一題分類（哪一類，只做記錄用，不影響判斷），一次請求解決，沒有文字要解析，這種失效模式直接不存在。

## 方法論

兩題在同一次 Jev 請求裡問完：`blocking`（是非題，擋不擋）、`category`（分類，純記錄用）。判定門檻是 `P(擋) ≥ 0.7`。刻意的工程設計：**逾時或任何請求失敗一律放行**（5 秒逾時、串接斷路器，連續失敗三次後 60 秒內直接放行不再嘗試），失敗時只記一行 log，不記訊息內容本身——這是一個明確的取捨：寧可漏放一則該擋的訊息，也不要因為審核服務掛掉就讓整個對話卡住。

實測資料：一個正式上線的客服 agent（俄語使用者訊息），58 筆真實案例，9 筆刻意的惡意輸入＋49 筆真實使用者問題，同一批資料另外跑一次 Mastra 內建的 `ModerationProcessor`（底層用 `gpt-oss-120b`）當對照。

## 結果

Jev 版本：9/9 惡意訊息全部擋下、49 則真實問題 0 則被誤判、中位數延遲 0.39-0.44 秒、每次請求約 920 個輸入 token。內建版本（`gpt-oss-120b`）：9 筆惡意輸入裡擋下 8-9 筆（有時漏一筆）、49 則真實問題同樣 0 誤判、中位數延遲 1.97 秒、價格約 4 倍。

## 這代表什麼

**這是目前收錄的跑分裡，第一個附上乾淨對照組的生產環境內容審核案例**——不是合成資料、是同一批真實客服訊息，兩套系統同場測試。0/49 的誤判率（不管哪個系統）代表這批真實訊息本身可能不算特別刁鑽，作者自己在文末老實寫「你的資料不是我們的資料，自己量」——**這句話值得認真看待，別把 9/9 跟 0/49 當成能套用到你自己場景的普適數字，這是這一批 58 筆資料量出來的結果**。

**「型別化輸出讓某一種失效模式直接消失」這件事，這裡有一個具體、可對照的說明**：內建版本靠解析大模型的自由文字，遇到模型輸出不了乾淨結論的情況（原文說「在真正需要判斷的困難輸入上，小模型有時候剛好答不出能解析的格式」）就只能放行；Jev 回傳的是型別化答案，不存在「答不出能解析的格式」這種失效模式——這不是說 Jev 判斷力比較強，是說**這一整類因為輸出格式解析失敗而放行的風險，換成型別化輸出後從架構上就不存在了**，跟我們在 README「不是瞎猜」那節講的「型別保證≠正確性保證」是同一個區分的另一面：這裡型別保證解決的正是一種特定的失效模式（解析失敗），不是保證判斷永遠正確。

**逾時就放行、斷路器保護**是一個值得抄的工程模式：把「審核服務本身掛了」跟「這則訊息該不該擋」兩件事分開處理，不要讓前者拖垮整個對話——這條可以直接補進 `AGENTS.md` 或 `browser-automation.md` 這類實作指南的通用建議裡。

## 標籤

📚（第三方獨立專案自己在生產環境量測的結果，我們沒有重跑；作者自己也提醒這是單一場景的資料，不是普適跑分）

---

# Content moderation in production: 9/9 caught, 0 false positives on 49 real messages (English)

## What this covers

Mastra's built-in moderation processor works by asking a large model "should this be blocked," then parsing the verdict out of its free-text response — this project points out a concrete failure mode: **on genuinely hostile input, a small model sometimes fails to return anything parsable**, and the processor's response in that case is to fail open, exactly when blocking matters most. This project replaces that step with Jev: one typed yes/no question (block or not) plus one classification question (category, logging only, doesn't affect the decision), answered in one request, with no text to parse — so that failure mode simply doesn't exist.

## Methodology

Two questions asked in one Jev request: `blocking` (yes/no, the gate) and `category` (classification, logging only). The threshold is `P(block) ≥ 0.7`. A deliberate engineering choice: **any timeout or failed request fails open** (5-second timeout, a circuit breaker that opens after 3 consecutive failures for 60 seconds), logging only one line on failure, never the message content itself — an explicit tradeoff: better to occasionally let through a message that should've been blocked than to have the whole conversation stall because the moderation service is down.

Measured data: one production customer-support agent (Russian-language user messages), 58 real cases — 9 deliberately hostile inputs plus 49 real user questions — the same set run a second time through Mastra's built-in `ModerationProcessor` (backed by `gpt-oss-120b`) as a control.

## Results

Jev version: blocked 9/9 hostile messages, 0 of 49 real questions blocked, median latency 0.39-0.44s, about 920 input tokens per call. Built-in version (`gpt-oss-120b`): blocked 8-9 of 9 hostile inputs (occasionally missing one), also 0 of 49 real questions blocked, median latency 1.97s, roughly 4x the price.

## What this means

**This is the first entry in this collection with a clean control group in a production content-moderation setting** — not synthetic data, the same batch of real support messages, two systems tested side by side. The 0/49 false-positive rate (for either system) suggests this batch of real messages may not be especially tricky, and the author states plainly at the end: "your domain is not ours — measure on your own messages." **Worth taking seriously — don't treat 9/9 and 0/49 as universal numbers that transfer to your own scenario; they're what this specific 58-case batch measured.**

**"Typed output eliminates one entire class of failure" gets a concrete, comparable illustration here**: the built-in version depends on parsing the large model's free text, and when the model can't produce a parsable answer on hard, genuinely-hostile input (the article's words), it can only fail open; Jev returns a typed answer, so "couldn't produce a parsable answer" isn't a failure mode that can occur — this isn't a claim that Jev judges better, it's that **the whole risk category of failing open due to output-parsing failure structurally doesn't exist once the output is typed.** This is the flip side of the type-guarantee-vs-correctness-guarantee distinction our README's "not blind guessing" section already draws: here the type guarantee solves one specific failure mode (parse failure), not a guarantee the judgment is always right.

**Fail-open-on-timeout plus a circuit breaker** is an engineering pattern worth copying: keep "the moderation service itself is down" separate from "should this message be blocked," so the former never stalls the whole conversation — worth folding directly into the general guidance in implementation guides like `AGENTS.md` or `browser-automation.md`.

## Tag

📚 (an independent third-party project's own production measurement; we did not re-run it; the author themselves flags this as single-scenario data, not a universal benchmark)
