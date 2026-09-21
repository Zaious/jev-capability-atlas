🇹🇼 中文｜🇬🇧 English below

# 信心門檻棄權／選擇性風險（confidence-gated abstention / selective risk）

## 這組測什麼

不是單純的「準確率多少」，而是「當模型可以選擇不回答時，表現會怎麼變」：設定一個信心門檻（例如 0.7），信心值低於門檻的題目直接棄權（轉人工或轉更重的模型），只看模型願意回答的那些題目的準確率有多高。這組量的是覆蓋率（coverage，願意回答的題目比例）跟準確率之間的取捨關係，外加兩個校準指標：Brier score（機率預測的均方誤差）與 ECE（Expected Calibration Error，預期校準誤差）。

## 方法論

`jev-dspy-lab` 本身是一套量測基礎設施（拿 DSPy 框架量測信心門檻棄權行為），repo 裡附了一組用 `jev-latest` 真實跑出來的記錄：24 題客服工單分派任務，信心門檻設在 0.7。

## 結果

24 題中，信心值 ≥ 0.7 的題目佔 95.8%（覆蓋率），也就是只有約 1 題被棄權；在願意回答的題目中，準確率 91.3%；Brier score 0.1546；ECE 0.0583。

## 這代表什麼

**這是目前收集到的資料裡，第一個示範「棄權機制」而不是單純「回答對不對」的案例**：跟我們自己在 README「實務建議」提到的「高信心自動執行／中信心先確認／低信心升級給人」的分流模式，這裡等於是把「低信心」那一段直接量出覆蓋率跟準確率的數字，而不是憑空建議。ECE 0.0583 這個數字本身不算差（越接近 0 代表信心值跟實際正確率越吻合），跟我們自己在 `suites/history-recall-context/` 觀察到的「題目有唯一答案時信心 0.87–1.00、沒有唯一答案時只剩 0.07–0.13」方向一致——都在說信心值是有實際訊號量的統計量，不是裝飾。

**但誠實地看樣本數**：24 題、棄權約 1 題，這個規模小到任何一題的結果都會大幅影響覆蓋率跟準確率的數字，Brier/ECE 這種統計量在樣本這麼小的情況下也不穩定。這條的價值不在「證明了 Jev 在客服工單分派上準確率 91.3%」，而在**它示範了一套可以套用在任何任務上的量測方法**——如果你要決定信心門檻該設在哪裡，這是一個具體可以照抄的量測框架，而不是一份可以直接引用的跑分結果。

**跟 `jev-benchmark`（工具呼叫風險分級，見同批收錄的另一條）放在一起看更有意思**：那邊是「回答錯的時候信心值會誠實下修」，這邊是「用信心門檻主動棄權能不能換到更高的準確率」——兩個獨立第三方分別從不同角度驗證了同一件事：Jev 的信心值在自足型任務（答案在給定內容裡）上，是一個真的可以拿來做工程決策的訊號，不是裝飾性的數字。

## 標籤

📚（第三方獨立測量基礎設施＋一組真實記錄的跑分，我們沒有重跑，整理自原始 README）

---

# Confidence-gated abstention / selective risk (English)

## What this covers

Not raw accuracy, but what happens when a model is allowed to abstain: set a confidence threshold (e.g. 0.7), have the model skip (route to a human or a heavier model) any case below it, and measure accuracy only on the cases it chose to answer. This measures the trade-off between coverage (share of cases answered) and accuracy, plus two calibration metrics — Brier score (mean squared error of the probability predictions) and ECE (Expected Calibration Error).

## Methodology

`jev-dspy-lab` is itself a measurement infrastructure (using the DSPy framework to measure confidence-gated abstention behavior). The repo includes one real recorded run using `jev-latest`: 24 support-ticket-routing cases, confidence threshold set at 0.7.

## Results

Of 24 cases, 95.8% had confidence ≥ 0.7 (coverage) — roughly 1 case abstained. Among the answered cases, accuracy was 91.3%. Brier score: 0.1546. ECE: 0.0583.

## What this means

**This is the first case we've collected that demonstrates an abstention mechanism rather than plain right/wrong accuracy**: it turns the "low confidence → escalate to a human" leg of our own README's practical-guidance routing pattern into an actual measured coverage/accuracy number, instead of a suggestion made on faith. The ECE of 0.0583 isn't bad on its own (closer to 0 means confidence tracks actual correctness more closely), and points in the same direction as what we saw in [`suites/history-recall-context/`](../../suites/history-recall-context/) — confidence at 0.87–1.00 on questions with a single answer, down to 0.07–0.13 on one without — both cases showing confidence carries real statistical signal, not decoration.

**But honestly, the sample size**: 24 cases with roughly 1 abstention is small enough that any single case swings the coverage/accuracy numbers substantially, and Brier/ECE are unstable at this scale. The value here isn't "proving 91.3% accuracy on support-ticket routing" — it's that **it demonstrates a measurement methodology applicable to any task**. If you're deciding where to set your own confidence threshold, this is a concrete framework to copy, not a benchmark result to cite directly.

**Worth reading alongside `jev-benchmark`'s tool-call risk classification** (collected in the same batch): that one shows "wrong answers honestly get discounted confidence"; this one shows "actively gating on confidence can trade coverage for higher accuracy" — two independent third parties verifying, from different angles, the same underlying point: on self-contained tasks (where the answer lives in the given content), Jev's confidence is a signal you can actually engineer against, not a decorative number.

## Tag

📚 (independent third-party measurement infrastructure plus one real recorded run; we did not re-run it, organized from the original README)
