🇹🇼 中文｜🇬🇧 English below

# 工具呼叫風險分級跑分（readonly/destructive/privileged/exfiltration）

## 這組測什麼

Agent 在執行工具呼叫前，要不要先攔一道風險分級：這次呼叫是唯讀（readonly）、會改資料（destructive）、需要提權（privileged）、還是可能外洩資料（exfiltration）？這是一個典型「該不該讓 Agent 自己按下去」的守門判斷，60 題全部人工標註，刻意分成三種難度：clear（明顯）、ambiguous（模稜兩可）、adversarial（刻意誤導/偽裝）。

## 方法論

60 個工具呼叫案例，人工標註四級風險分類當標準答案，依難度分三組；用 Jev 的 Choice 問答對每一題做分類，同時記錄每題的信心值分布，逐一比對信心值跟「這題有沒有答對」的關係，不是只看總準確率。

## 結果

整體準確率 91.7%（60 題中 55 題正確）。**關鍵不在準確率本身，而在信心值的行為**：README 原文重點強調——「每一個答錯的案例都伴隨著保守的信心值；模型從來沒有在答錯的時候給出 1.000。」也就是說，答錯的題目信心值明顯偏低，沒有出現「錯得很有把握」的案例。難度分組上，adversarial（刻意誤導）組的錯誤率高於 clear 組，符合直覺——但即使在最難的一組，信心值依然跟著往下修正，沒有假裝有把握。

## 這代表什麼

**這是目前收集到的資料裡，信心值行為最漂亮的一個反例**：跟 [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) 的 DAIR Emotion 案例（平均信心 0.819、實際準確率只有 48%，16% 的題目給正確答案 0 機率）恰好相反——這裡展示的是「校準機制正常運作」的樣子：答錯的題目信心值會誠實下修，不會自信滿滿地錯。兩相對照，說明我們在 README「不是瞎猜」那節講的但書（校準是母體層級的統計性質，不是每一題都保證）在實務上真的會**因任務而異**：工具呼叫風險分級這種「答案通常寫在呼叫內容本身裡」的自足型任務（跟我們核心那條軸完全吻合——風險等級這種東西，只要工具名稱、參數、上下文都給了，答案就在給定內容裡，不需要外部知識），信心值就表現得比 DAIR Emotion 這種語意模糊、類別本身就會混淆的任務可靠得多。

**對想拿 Jev 做安全審查前置分類的人是一個直接可用的參考點**：91.7% 準確率加上「錯的時候會自己降信心值」，代表你可以放心把低信心值的案例路由給人工複核或更重的模型——這正是 README「實務建議」那節建議的高/中/低信心分流模式，這裡是一個真的量出來符合這個模式預期行為的獨立案例。**但要誠實提醒**：60 題的樣本數不大，adversarial 組本身多大、平均信心值分別是多少，原始 README 沒有列出逐題明細表，我們只整理了它文字敘述給出的結論，還沒有看到可重新驗證的原始資料檔。

## 標籤

📚（第三方獨立跑分，我們沒有重跑，整理自原始 README 的方法論與結果敘述）

---

# Tool-call risk classification benchmark (readonly/destructive/privileged/exfiltration) (English)

## What this covers

Whether an agent should gate a tool call behind a risk classification before executing it: is this call read-only, destructive (changes data), privileged (needs elevated access), or exfiltration (potential data leak)? This is a classic "should the agent be allowed to press the button itself" gating judgment. All 60 cases are hand-labeled, deliberately split into three difficulty tiers: clear, ambiguous, and adversarial (deliberately misleading/disguised).

## Methodology

60 tool-call cases, hand-labeled with a four-tier risk classification as ground truth, split by difficulty into the three groups above. Jev classifies each case via a Choice question, with confidence recorded per case and compared against whether that case was answered correctly — not just aggregate accuracy.

## Results

Overall accuracy: 91.7% (55/60 correct). **The interesting part isn't the accuracy — it's the confidence behavior**: the original README states plainly — "every incorrect answer came with hedged confidence; the model never returned 1.000 and was wrong." In other words, wrong answers reliably came with lower confidence; there were no confidently-wrong cases. By difficulty tier, the adversarial group had a higher error rate than the clear group, as expected — but even there, confidence adjusted downward accordingly rather than staying falsely high.

## What this means

**This is the cleanest positive counter-example to calibration failure we've collected so far**: it's the mirror image of [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)' DAIR Emotion result (0.819 mean confidence against 48% actual accuracy, with 16% of items assigned zero probability for the correct answer) — here calibration is working exactly as intended: wrong answers get honestly discounted confidence instead of false certainty. Read together, they show the caveat in our README's "not blind guessing" section (calibration is a population-level property, not a per-item guarantee) actually **varies by task type in practice**: for a self-contained task like tool-call risk classification — where the answer is essentially derivable from the call itself (tool name, arguments, context), squarely matching our core axis — confidence behaves far more reliably than on a task like DAIR Emotion, where the categories themselves genuinely blur.

**A directly usable reference point for anyone considering Jev as a pre-filter for security review**: 91.7% accuracy plus "confidence honestly drops when wrong" means you can route low-confidence cases to human review or a heavier model with reasonable trust — exactly the high/medium/low confidence-routing pattern our README's practical-guidance section recommends, and this is an independent case where that expected behavior actually measured out. **Honest caveat**: the sample is only 60 cases, and the original README doesn't publish a per-case breakdown or raw data file — we're relaying its stated conclusions, not an independently re-verifiable dataset.

## Tag

📚 (independent third-party benchmark; we did not re-run it, this is organized from the original README's methodology and results narrative)
