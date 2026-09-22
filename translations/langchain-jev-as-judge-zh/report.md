🇹🇼 中文｜🇬🇧 English below

# 把 Jev 當 agent 評審：LangChain 的實驗，與三個要打折扣的地方

## 這組測什麼

agent 的評測目前只有兩種做法：寫死的程式，或用大模型當評審。前者只能處理能用邏輯寫死的行為，後者慢、貴，而且同一個回合重跑兩次可能給不同分數。LangChain 想知道 Jev 這種「System One」模型能不能當第三種評審。

做法是：用他們自己的 Deep Agents 做一個查天氣的 agent，定義五個測試案例（西雅圖的目前天氣、奧斯汀的週末預報、都柏林要不要帶傘、東京的長期預報、地名有歧義的 Springfield）。**每個案例只跑一次 agent，把完整輸出凍結起來**，之後所有評審看的都是同一批固定的回合，只有評審換人。每個評審對這五個凍結的回合各評 100 次，給兩種分數：`quality`（0 到 1 的連續分數）與 `does_pass`（通過或不通過）。另外由一位人工標註者對這五份回應標出標準答案，用來算準確率。

## 結果

| 評審 | 通過與否的準確率 | 連續分數的平均變異數 | 相對 Jev | 每次呼叫成本 | 平均延遲 | 總評測成本 |
|---|---|---|---|---|---|---|
| **Jev** | **100.0%** | **0.0000149** | 1× | **0.00035 美元** | **0.44 秒** | **0.34 美元** |
| GPT-5.6 Terra | 99.8% | 0.01364 | 913× | 0.00289 美元 | 2.83 秒 | 2.90 美元 |
| GPT-5.6 Luna | 96.4% | 0.00647 | 433× | 0.00039 美元 | 2.50 秒 | 0.39 美元 |
| Claude Sonnet 4.6 | 80.0% | 0.00137 | 92× | 0.02811 美元 | 2.16 秒 | 28.17 美元 |

兩邊的分數是這樣組成的：Jev 用三題是非題（答案有沒有根據、搜尋行為符不符合預期、有沒有用）的機率取平均當 `quality`，另外一題是非題給 `does_pass`，還有一題選擇題判斷這次搜尋的結果屬於哪一類；大模型評審則是用結構化輸出（json_schema）回傳同樣三個 0 到 1 的浮點數再平均。

## 這個數字代表什麼、可信到什麼程度

**做得對的地方，值得照抄**：把 agent 的回合凍結成固定資料集，讓不同評審在**同一批輸入**上各跑 100 次，並且把「跟人一致」（準確率）與「自己穩不穩」（變異數）分開量。文章也明講低變異不等於準，評審可能穩定地錯。這正是我們一路在講的同輸入對照。

**三個要打折扣的地方**：

1. **樣本是五題，不是五百題。** 「500 次判斷」是 5 個案例 × 100 次重複。重複只增加穩定度的樣本，不增加題目的多樣性，而標準答案只有一位人工標註者。repo 的 README 自己寫得很清楚：「This is a small corpus with five agent runs and one human reviewer. The result describes this experiment; it is not a general ranking of judge accuracy.」文章的摘要沒有這麼保留。
2. **對照組沒有關掉隨機性。** 我們去讀了程式：`src/evals/model.py` 的 `create_chat_model` 只設定了模型、網址、金鑰與逾時，**沒有設 temperature**，所以三個大模型評審都跑在供應商的預設取樣設定上。文章在「Reproducibility」一節誠實揭露了這件事，但沒有把它跟變異數的結論連起來——92 到 913 倍的差距，有一部分是取樣設定造成的，把溫度設成 0 再比才是對照。
3. **沒有記錄 Jev 的版本。** 文章自述「The Jev service version was not available in the experiment metadata」。同一份測試日後要重跑，會不知道當時對上的是哪一版。

**另外，文章有一處寫反了**：它把 Choice 與 Noul 的例子對調——「答案有沒有根據」這種是非題被標成 Choice，「三種搜尋結果選一個」被標成 Noul。repo 的 README 與程式裡都是正確的，所以是文章的筆誤，不是實作有問題。

**跟本 repo 既有結論的關係**：評審一個 agent 回合，需要的證據（使用者的問題、agent 的最終回答、工具呼叫與檢索到的資料）都在給它的 state 裡，屬於核心那條軸「訊號自足」的那一側，本來就是它的強項——這個結果方向上完全吻合，但它證明的範圍比文章標題聽起來窄得多。低成本也有它自己的風險，文章自己有寫：**一個穩定地錯的評審，會用很低的成本大量產生錯誤回饋**。

## 標籤

📚（第三方發表的實驗；我們沒有重跑它的測試，但自己讀過它的可複現 repo，數字與程式細節都在那裡核對過）

---

# Jev as an agent judge: LangChain's experiment, and three discounts to apply (English)

## What this covers

Agent evaluation today comes in two forms: hand-written code, or an LLM as judge. Code only handles behavior you can express as explicit logic; LLM judges are slow, expensive, and can score the same run differently twice. LangChain wanted to know whether a "System One" model like Jev could be a third kind of evaluator.

Their setup: a weather agent built with their own Deep Agents, and five test cases (current conditions in Seattle, weekend forecast in Austin, an umbrella decision in Dublin, an extended forecast in Tokyo, and an ambiguous location, Springfield). **The agent was run once per case and its complete output frozen**, so every judge saw the same fixed runs and only the judge changed. Each judge scored those five frozen runs 100 times on two signals: `quality` (a continuous 0-to-1 score) and `does_pass` (a binary decision). One human reviewer labelled the five responses as the oracle for accuracy.

## Results

| Judge | Pass-or-fail accuracy | Mean quality variance | Relative to Jev | Cost per call | Average latency | Total evaluator cost |
|---|---|---|---|---|---|---|
| **Jev** | **100.0%** | **0.0000149** | 1× | **$0.00035** | **0.44 s** | **$0.34** |
| GPT-5.6 Terra | 99.8% | 0.01364 | 913× | $0.00289 | 2.83 s | $2.90 |
| GPT-5.6 Luna | 96.4% | 0.00647 | 433× | $0.00039 | 2.50 s | $0.39 |
| Claude Sonnet 4.6 | 80.0% | 0.00137 | 92× | $0.02811 | 2.16 s | $28.17 |

How each side's score is assembled: Jev averages three yes/no probabilities (is the answer grounded, does the search behavior match expectations, is it useful) into `quality`, with another yes/no for `does_pass` and a choice question classifying the search outcome; the LLM judges return the same three 0-to-1 floats through structured output (json_schema) and average them.

## What it means, and how much to trust it

**What it gets right, and worth copying**: freezing the agent runs into a fixed dataset so that every judge is scored on **identical inputs**, running each 100 times, and keeping "agrees with the human" (accuracy) separate from "agrees with itself" (variance). The post also says plainly that low variance doesn't imply accuracy — a judge can be consistently wrong. That's the identical-input comparison this repo keeps asking for.

**Three discounts to apply**:

1. **The sample is five items, not five hundred.** The "500 repeated decisions" are 5 cases × 100 repeats. Repetition adds samples for stability, not variety of items, and the oracle is a single human reviewer. The repo's README says so directly: "This is a small corpus with five agent runs and one human reviewer. The result describes this experiment; it is not a general ranking of judge accuracy." The post's summary is less guarded.
2. **The control group's randomness was never turned off.** We read the code: `create_chat_model` in `src/evals/model.py` sets only the model, base URL, API key and timeout — **no temperature** — so all three LLM judges ran on their providers' default sampling settings. The post discloses this honestly under "Reproducibility" but doesn't connect it to the variance result; part of that 92-to-913× gap comes from sampling settings, and the controlled comparison is against temperature 0.
3. **The Jev version wasn't recorded.** The post states that "The Jev service version was not available in the experiment metadata," so a future re-run can't know which build it was measured against.

**One thing the post gets backwards**: it swaps the Choice and Noul examples — "is the final answer grounded in the retrieved evidence?" (a yes/no) is labelled Choice, and "which search outcome best describes this run?" (one of three) is labelled Noul. The repo's README and code have them the right way round, so it's a slip in the post, not in the implementation.

**How it relates to this repo's existing findings**: judging an agent run needs evidence — the user's question, the agent's final answer, its tool calls and what it retrieved — that all sits in the state you hand it, which is the "self-contained" side of the core axis and where Jev is strongest. So the direction fits exactly; the scope proven is just much narrower than the headline suggests. Low cost also carries its own risk, which the post states itself: **a consistently wrong evaluator produces bad feedback cheaply, at scale**.

## Tag

📚 (a third-party experiment; we didn't re-run it, but we read its reproducibility repo ourselves and checked the figures and implementation details there)
