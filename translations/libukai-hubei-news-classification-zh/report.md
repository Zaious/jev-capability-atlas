🇹🇼 中文｜🇬🇧 English below

# 真實生產環境的簡體中文分類：新聞判讀「是否含湖北元素」

## 這組測什麼

一個跑了一年的真實個人專案：每天把《人民日報》的新聞做分類，判斷每篇文章是否包含湖北相關元素。原本用 Gemini Flash Lite（作者自述是成本與速度雙重考量下測試過的最佳選擇），Jev 在 OpenRouter 上線當天，作者用同一組提示詞跑了一個小型對照測試。

## 方法論

累積一年、將近 24,000 筆真實資料，其中約 1,800 筆判定為「包含」；從裡面隨機抽出 1,000 筆當測試集（500 筆判定包含、500 筆判定不包含），16 個併發程序同時打兩邊的 API 做速度與結果對照。**這不是正式跑分**：沒有人工重新標註的絕對正解，比較基準是「跟原本用的 Gemini Flash Lite 判斷一不一致」，分歧原因是作者事後手動審核判斷出來的，不是預先設計好的難例分組。

## 結果

**速度**：Gemini Flash Lite 平均每篇 3 秒，Jev 縮到 0.35 秒／篇，快將近 10 倍。**成本**：約 5,000 筆資料、3,000 萬 token，總花費約 1 美元。**一致性**：跟 Flash Lite 的判斷有約 15% 不一致；作者手動審核後歸因，大部分分歧出在文章提到某個「曾在湖北省任職過的官員」的人名時——Flash Lite 靠比較大的世界知識庫，認得出這個人跟湖北的關聯，判定包含；Jev 在這塊「弱一點」，判定不包含。作者自己的結論：這種分歧在他的實際應用場景裡完全可以接受。

## 這個數字代表什麼、可信到什麼程度

**這是我們目前收錄裡，最直覺易懂的一次核心軸現場示範**——文章本身要不要判定包含湖北元素，大部分情況下答案就寫在文字裡（提到湖北的地名、機構、事件），這種情況兩個模型判斷一致；分歧出在需要**外部世界知識**才能判斷的案例（「這個人名曾經在湖北任職過」這件事，文章正文沒寫，得靠模型自己的預訓練記憶回憶）——這是本 repo 目前「需要外部知識」這種失效模式最直接的證據：不是我們自己設計出來的測試案例，是一個素人在真實應用裡自己撞到、自己正確歸因出原因的。我們自己的合成中文歷史選擇題（[`suites/history-recall-context/`](../../suites/history-recall-context/)）修正錯字、去除算法歧義後反而沒重現這個失效——乾淨的冷門史實題它不給背景也答對了。兩者合起來看：它不是什麼都不知道，但知不知道事前看不出來。

**兩個獨立來源，同一個速度數字**：0.35 秒／篇，剛好跟本 repo 收錄的 ThaiExam 跑分（0.35 秒／題）完全一樣——不同任務、不同語言、完全不相關的兩個來源，量出同一個數字，是一次意外但紮實的交叉驗證。

**該打折扣的地方要老實講**：這不是正式跑分，沒有絕對正解，比較基準是另一個 LLM 而不是人工標註；「15% 不一致」不能直接讀成「15% 錯誤率」——比較準確的講法是「85% 跟 Flash Lite 一致，剩下的分歧裡，作者手動審核後認為大部分可歸因到需要外部知識的案例」。這是單一帳號、單一任務、單一次測試，不是可重複驗證的基準。

**額外價值：這是目前收錄裡第一個簡體中文、真實生產規模的案例**——跟本 repo 其他中文測試（繁體中文歷史選擇題、繁體中文反諷偵測）語域不同，也跟社群另一處提到「TypeSafe 文件自述 CJK 準確率較低」的說法（見 `translations/jev-context-compaction-debate-zh/` 引用的 issue 討論）形成一個有趣的對照——這裡在單純文字分類任務上，整體一致率仍然有 85%，弱點集中在需要外部知識的案例，不是廣泛的語言理解問題；但這只是一個資料點，不足以推翻或證實「CJK 較弱」這個說法，值得記一筆、不下定論。

## 標籤

📚（第三方獨立真實使用案例；原文由 repo 維護者親自轉貼提供，我們沒有自己重跑，也沒有工具能直接對 X 平台內容做自動化查證——見 `SOURCE.md` 的查證提醒）

---

# A real production Simplified-Chinese classification task: "does this news article involve Hubei?" (English)

## What this covers

A real personal project running for a year: classifying each day's People's Daily news articles for whether they contain Hubei-related elements. The author had been using Gemini Flash Lite (self-described as the best cost/speed tradeoff after testing), and ran a small side-by-side comparison with Jev the day it launched on OpenRouter, using the same prompt.

## Methodology

A year's worth of real accumulated data, nearly 24,000 articles, about 1,800 labeled "included"; 1,000 items randomly sampled as a test set (500 "included," 500 "not included"), with 16 concurrent processes hitting both APIs for a speed and result comparison. **This is not a formal benchmark**: there's no independently re-labeled ground truth — the comparison baseline is agreement with the previously-used Gemini Flash Lite, and the reason for disagreements was determined by the author's own manual review after the fact, not a pre-designed hard-case split.

## Results

**Speed**: Gemini Flash Lite averaged 3 seconds per article; Jev cut that to 0.35 seconds, nearly 10x faster. **Cost**: about 5,000 items, 30 million tokens, roughly $1 total. **Agreement**: about 15% disagreement with Flash Lite; after manual review, the author attributes most of it to cases where an article names an official who once served in Hubei — Flash Lite's larger world knowledge recognizes the connection and marks it "included"; Jev is "a bit weaker" here and marks it "not included." The author's own conclusion: this level of disagreement is entirely acceptable for the actual use case.

## What this means, and how much to trust it

**This is the most intuitive live demonstration of the core axis in this collection so far** — whether an article should be marked as involving Hubei is, in most cases, answerable directly from the text itself (a place name, an institution, an event); the two models agree there. The disagreements come from cases requiring **external world knowledge** that isn't in the article's own text (that a named person once served in Hubei is something the article doesn't state — a model has to recall it from pretraining) — currently this repo's most direct evidence for the outside-knowledge failure mode: not a test case we designed, but something an ordinary user hit in a real application and correctly diagnosed themselves. Our own synthetic Chinese history suite ([`suites/history-recall-context/`](../../suites/history-recall-context/)) didn't reproduce this failure once its typos and counting ambiguity were fixed — it answered the clean obscure question correctly with no passage. Read together: it isn't ignorant, but you can't tell in advance what it knows.

**Two independent sources, the same speed number**: 0.35 seconds per item exactly matches this repo's ThaiExam entry (0.35 seconds per question) — two unrelated sources, different tasks, different languages, landing on the identical figure — an unplanned but solid cross-validation.

**Honest discounts to apply**: this isn't a formal benchmark, there's no ground truth, and the comparison baseline is another LLM, not human labels; "15% disagreement" shouldn't be read as "15% error rate" — the more accurate statement is "85% agreement with Flash Lite, and among the remainder, the author's manual review attributes most to cases needing external knowledge." This is a single account, a single task, a single test run — not a reproducible benchmark.

**Extra value: the first Simplified-Chinese, real production-scale case in this collection** — a different register from this repo's other Chinese-language tests (Traditional-Chinese history trivia, Traditional-Chinese sarcasm detection), and an interesting counterpoint to a claim elsewhere in the community that "TypeSafe's own docs say CJK accuracy is lower" (referenced via the issue discussion cited in `translations/jev-context-compaction-debate-zh/`) — here, on a plain text-classification task, overall agreement still holds at 85%, with weakness concentrated in cases needing external knowledge rather than broad language comprehension. But this is one data point, not enough to confirm or refute the "CJK is weaker" claim — worth recording, not worth concluding from.

## Tag

📚 (an independent third-party real-world use case; the original text was pasted in verbatim by this repo's maintainer; we did not re-run it, and have no tool that can automatically verify X/Twitter content directly — see the verification note in `SOURCE.md`)
