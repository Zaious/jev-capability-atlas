🇹🇼 中文｜🇬🇧 English below

# Hermes Jev Skills：把 agent 的小決策外包給 Jev，以及三份負面結果

## 這是什麼

[hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)（MIT，2026-09-18 建立）把一個 agent 一天之中的小決策交給 Jev：這一輪該用哪個模型、要載入哪個技能、檢索回來的哪幾段值得讀、逐字稿被砍時哪幾個回合該留、下一步該點哪個按鈕。它為 [Hermes](https://github.com/NousResearch/hermes-agent) 寫的，但技能是十個 `SKILL.md` 目錄（README 自述九個功能技能，另有一個安裝用的 `jev-setup`），Claude Code 與 Codex 也讀得到；`jevkit` 只用標準函式庫，測試全離線、Jev 的回應全部假造。

值得看的不是功能清單，是 `evals/`。**五份 scorecard 裡有三份是負面結果**——量完之後決定不用，或決定不改。我們自己的 repo 一直在找這一類證據，很少有人肯寫。

## 一、對話壓縮與交接摘要：量完把 Jev 拿掉了

[`evals/compaction/results/SCORECARD-2026-09-20.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/compaction/results/SCORECARD-2026-09-20.md)

**方法**：七個真實工作 session（243–614 列、12–194 個使用者/助理回合、25,000–118,000 字元對話，全部重度使用工具），每個 session 一份 15 題回憶考。105 題裡有 104 題能被「看得到完整逐字稿」的 oracle 答出來，recall 只算那 104 題。摘要寫手與作答者是 `z-ai/glm-5.3-flash`，出題與評分是 `google/gemini-3.8-flash`，Jev 用 `jev-latest`。所有 arm 都寫同樣的 400 字摘要、用同一個寫手。

**結果**（closed-book＝只有摘要；「一次搜尋」＝摘要加一次檢索）：

| 寫摘要的人讀到什麼 | closed-book | 加一次搜尋 | 寫手讀入的字元 |
|---|---|---|---|
| 單純取最後 24,000 字（fallback 用的） | **48.1%** | 68.3% | 24,940 |
| 整段對話 | 46.2% | 67.3% | 88,609 |
| 最後 24,000 字，換一種 prompt 措辭 | 40.4% | **73.1%** | 24,770 |
| **Jev 挑回合（0.13.2 出貨的版本）** | **37.5%** | 68.3% | 17,434 |
| Jev 掛掉時的 fail-open | 33.7% | 61.5% | 12,511 |
| 用正規表示式留「像識別碼」的回合 | 31.7% | 62.5% | 24,940 |
| 照 Jev 留下的數量、改用「取最近的」 | 30.8% | 60.6% | 12,757 |
| 完全沒有摘要 | — | 56.7% | 0 |

後來出貨的 0.14.0 是「整段對話（上限 30 萬字元）＋1,200 字預算＋不用 Jev」，拿到 **58.7% / 75.0%**。

**作者的三點讀法，第三點最重要**：

1. **Jev 的判斷本身是有效的，輸的是做法。** 同樣數量的標記，Jev 挑的勝過「取最近的」——逐題比 11 勝 4 敗（加搜尋 12 勝 4 敗）。但用 Jev 的摘要輸給同樣大小的「取最後一段」，逐題 4 勝 15 敗。作者推測的原因很具體：一個 `summarize` 回合只留下前 400 字元，而七個 session 裡有五個平均每回合 1,400–7,400 字元——**裁掉的東西不是換一組回合能救回來的**。
2. **寫手讀了多少不是 400 字摘要的瓶頸。** 整段對話並沒有贏過它的最後四分之一，是摘要本身裝不下。要把數字拉高，得同時放寬兩邊：讀完整段 **且** 寫 1,200 字。
3. **一次搜尋比上面全部都值錢。** 每個 arm 都因此上升 20 到 33 分；沒有摘要但能搜尋一次的 session，贏過每一個 closed-book 的摘要。

**兩個「看起來明顯該有用」的改良也量了，也都沒用**：把留下的行放在背景之前、把識別碼從被裁掉的文字裡掃出來（`digest_v2`），30.8% 對 37.5%，5 勝 12 敗；把免費的正規表示式識別碼清單附在摘要後面，49.0% 對 48.1%（4 勝 3 敗），但**附給一個完全沒有摘要的 session 反而掉 13 分**（43.3% 對 56.7%，4 勝 18 敗）。

**最後，事實到底藏在哪**：104 題裡，最能支撐答案的那個回合是工具輸出的有 48 題、助理文字 32 題、使用者自己說的話 24 題。**沒有任何一個 arm 讀得到工具輸出**，因為交接外掛不匯出它。出貨的設定仍然答對了 48 題裡的 22 題——agent 會把工具回傳的東西重述一遍，摘要是從重述裡讀到的。

## 二、技能挑選的第二階段：留下來，因為第一階段會高信心答錯

[`evals/skill-pick/SCORECARD-2026-09-22.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/skill-pick/SCORECARD-2026-09-22.md)

第一階段把技能目錄切成 120 個一批，每批問一題 Choice；第二階段是第二次請求：一題 `needs_skill` 加上每個入圍者一題 Noul。問題是那 500 毫秒值不值得。14 個案例（10 個該命中某個指定技能、4 個刻意平凡、不該用任何技能），兩種目錄大小：

| 做法 | 目錄 | n | 對 | **錯** | 多事 | 漏 |
|---|---|---|---|---|---|---|
| 只做第一階段 | 10 個技能 | 14 | 10 | 0 | **4** | 0 |
| 兩階段（出貨的） | 10 個技能 | 14 | 14 | 0 | **0** | 0 |
| 只做第一階段 | 379 個技能 | 28 | 18 | **2** | 8 | 0 |
| 兩階段（出貨的） | 379 個技能 | 28 | 22 | **0** | 6 | 0 |

中位延遲 428 毫秒（10 個技能）/ 489 毫秒（379 個）。

**決定這件事的是那兩次錯**：

```
click through the checkout flow in the browser and confirm each step
  只做第一階段： dogfood  (0.96，重跑 0.94)   ← 錯，而且很確定
  出貨版：       jev-browser-use (needs_skill 0.85)  ← 對
```

用他們自己的話：這是門檻救不了的失敗模式——**門檻只看答案有多確定，而這一次它就是很確定**。這是我們收集到的第三方「高信心答錯」實例裡最乾淨的一個，而且是在正式產品的決策路徑上抓到的。

作者自己標的但書：期望答案是同一批人寫的（量的是「跟書面意圖一致」不是 ground truth）；`None` 標籤只對它寫的那個目錄成立，所以 fleet 那兩列的「多事」是上限，該讀的是那兩次高信心錯；小目錄每案只跑一次。

## 三、動作選擇的第二題：有訊號，但不採用

[`evals/choose-match/SCORECARD-2026-09-21.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-21.md)

Stagehand 的 Act 在接受一個 Jev 的選擇之前會問兩題——哪個候選最好、以及**有沒有任何候選真的符合目標**——這個 repo 只用一個信心門檻。他們拿 31 個標註案例（16 個有解、8 個陷阱、7 個無解）跑五次，兩題放在同一次請求裡，所有閘門離線重放。

**第二題確實帶著真訊號**：無解案例的 match 機率上限在每一次跑都停在 0.43–0.45，其他全部從 0.61 起跳——「這個畫面上沒有東西能達成目標」是分得開的。信心值本身分得比較不乾淨（兩個無解案例落在 0.58–0.70）。

**但它對這個閘門要做的決定沒有幫助**：現行的 0.65 單題門檻在五次跑裡**零次錯誤動作**。那個唯一已知的錯誤答案（「關掉這個對話框但不要丟掉我的工作」→ 選了「儲存」）每次都落在 0.45–0.60，被門檻擋掉；而同一題的 match 是 0.79–0.83，所以**只用第二題當閘門的話，每一次跑都會點錯那一下**。

作者的結論寫得很克制：「零次錯誤動作讓第二題沒有改善的空間。沒有改善是比有害更弱的主張」，而且「0.65 就是在這 31 題上校出來的，這個比較是在門檻的主場打的，只能說第二題在這裡沒用，不能說門檻沒有過擬合」。同一天的[另一份 scorecard](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-22-stakes-and-margin.md) 把 18 種閘門組合（依「不可逆」提高門檻、要求第一名與第二名的差距）在 93 個案例決策上全部重放，**沒有一列跟現行門檻不同**，所以一樣什麼都沒出貨。

## 四、一個可量的寫問題方法：必要條件與偏好要分開寫

[`docs/writing-a-jev-question.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/docs/writing-a-jev-question.md)

一個在生產環境用 Jev 的廠商（Virlo，短影音研究工具）回報他們最大的一次準確率跳升不是來自更大的模型或更長的提示詞，是來自一句話。他們的任務是判斷一支影片屬不屬於某個主題。第一版把整份 brief 寫進去——主題、語氣、格式、受眾——**Jev 把每一項都當成硬性條件**，44 支人工標註影片的準確率 **16/44**。改寫成「主題是條件，其餘明說是用來打破平手的偏好」之後：**33/44**。同模型、同測試集、同程式路徑。

機制解釋跟核心那條軸是同一件事：Jev 拿你給的選項去對你給的 state 評分，**它沒有辦法知道你 state 裡哪一行才是有約束力的那一行**，所以一個軟性屬性會被當成篩選條件。作者給的三種題型寫法：Choice 先點名決定性的那個屬性、再點名只用來打破平手的；Score 說明哪幾個等級被條件把關、哪幾個吸收偏好；Noul 咬得最兇，因為一個藏著「而且還要……」的是非題其實是兩題。

**這條要打折**：一手來源是 X 貼文（[@dsqjaffa](https://x.com/dsqjaffa)，2026-09-21），賣產品的廠商自述，n=44，沒有逐案拆解，而我們抓不到 X——我們只能查證到「hermes 的文件這樣轉述」。作者自己也寫「當成一個值得試並量測的強預設，不是定律」。當成假設用，別當成結論。

## 五、Jev 是雲端 API，state 就是送出去的東西

這個 repo 的 README 有一節叫「What leaves your machine」，逐個功能寫明送出去什麼。我們的地圖到目前為止沒有處理過這個維度，但它是「這個任務適不適合 Jev」的真實判準之一：

- **路由**：使用者那一輪的字，遮蔽過（信箱、電話、token、長十六進位），上限 2,500 字元。不送歷史、工具結果、檔案或記憶。看起來像帶著機密的回合、以及任何列進 `private_profiles` 的設定檔，只送粗特徵：長度、有沒有程式碼、有沒有風險字眼。
- **記憶**：query 加每段最多 900 字元。你自己的 id、路徑與來源換成 `P0`、`P1`……不送出去。看起來像憑證的段落整段不送。
- **挑回合**：每個回合的頭尾各 350 字元。預設的交接完全不呼叫 Jev。
- **信箱分類**：主旨與最多 2,500 字元的內文；寄件者的 **domain**（不送信箱本身）；`Received:` 只留下它帶的日期，因為其餘部分是收件人地址與每一跳的內部 IP。**信件先解碼再篩**——quoted-printable、percent-encoding、HTML entity、base64——理由很具體：電子報頁尾會把你自己的地址 percent-encode 在退訂連結裡、base64 在追蹤連結裡，純文字遮蔽器兩個都看不到。
- **電腦與瀏覽器操作**：只送目標、元素的短標籤與你自己寫的動作描述。不送截圖、頁面文字或欄位值。

作者也誠實寫了一件不好聽的事：在預設的 `redacted-text` 模式下，路由送的就是使用者那一輪的原文（遮蔽過），而且**路由發生在 agent 行動之前，所以 agent 對這件事沒有發言權**。

## 這代表什麼、可信到什麼程度

**方法論值得照抄的地方**：

- **先量自己的雜訊地板。** 壓縮那份裡有兩組看同一段文字、只差 prompt 措辭的 arm，在兩種模式下往相反方向各移動約 8 分。有這條，其他行才讀得出來。
- **把「這個做法沒用」跟「這個模型不行」分開。** Jev 的標記勝過「取最近的」，但建在它上面的摘要還是輸——這兩句話同時成立，而且第二句的原因（裁到 400 字元）跟 Jev 無關。
- **決定之前先把標準寫下來。** 風險門檻那份的腳本 docstring 裡先寫好「新閘門必須每一次跑都零錯誤動作，而且停頓次數嚴格更少」，才去看數字。
- **負面結果留在 repo 裡，連同「什麼情況會重啟這個討論」。** 技能挑選那份的最後一段寫明兩個會讓它重新考慮的條件。

**我們的但書**：

1. **我們沒有重跑任何一份。** 數字全部出自作者發布的 scorecard。壓縮那份的逐字稿、考卷與摘要都不在 repo 裡（作者明講），所以那份可以重算、不能被外部複現。
2. **樣本都很小**：七個 session / 104 題、14 個案例、31 個案例。作者每一份都自己標了但書，這點比多數 repo 自述誠實。
3. **壓縮那份最大的那個差距，只比它自己的雜訊地板大一點。** 48.1% 對 37.5% 是 10.6 分，而他們自己量到的「只改措辭」效應約 7.7 分。真正撐住這個結論的不是那兩個百分比，是逐題的 **4 勝 15 敗**——引用這份的時候該引那一組數字，不是兩個平均值。另外整套評測的寫手、出題與評分全是模型，沒有人工標註。
4. **Virlo 那條是二手，一手查不到**（見上）。

**跟本 repo 既有結論的關係**：

- 第一條「路由、技能挑選、動作選擇」落在核心軸自足的那一側——候選都在畫面上、都在目錄裡、都在那一輪的文字裡，這跟 [`browser-automation.md`](../../browser-automation.md) 收斂出的那套架構是同一件事。
- 第二條**壓縮與交接站在軸的另一側，而且提供了一個我們原本沒有的失敗原因**。我們原本記的失敗是「state 只給長度佔位字串，內容根本沒露出來」（見 [`translations/jev-context-compaction-debate-zh/`](../jev-context-compaction-debate-zh/)）。這一份的 state 是給齊的，判斷也確實比「取最近的」好，**輸在「挑回合」這個問題形狀本身**——選得再準，被留下的回合仍然只保留前 400 字元。換句話說：**把任務改寫成 Jev 能答的形狀之後，還要再問一次「這個形狀本身能不能完成原本的工作」**。

## 標籤

📚（第三方發表的實驗與實作；我們沒有重跑它的任何評測，數字逐格抄自作者發布的 scorecard 檔案，連結都在 [`SOURCE.md`](SOURCE.md)）

---

# Hermes Jev Skills: outsourcing an agent's small decisions to Jev, and three negative results (English)

## What this is

[hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills) (MIT, created 2026-09-18) hands an agent's small daily decisions to Jev: which model answers this turn, which skill to load, which retrieved passages matter, which turns survive a cut, which button comes next. It was built for [Hermes](https://github.com/NousResearch/hermes-agent), but the skills are ten `SKILL.md` directories (nine feature skills plus a `jev-setup` installer) that Claude Code and Codex also read; `jevkit` is stdlib-only and the tests are offline with every Jev reply faked.

The interesting part isn't the feature list, it's `evals/`. **Three of its five scorecards are negative results** — measured, then not shipped, or not changed. That's the kind of evidence this repo keeps looking for and rarely finds written down.

## 1. Compaction and handoffs: measured, and Jev was taken out

[`evals/compaction/results/SCORECARD-2026-09-20.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/compaction/results/SCORECARD-2026-09-20.md)

**Method**: seven real working sessions (243–614 rows, 12–194 user/assistant turns, 25,000–118,000 characters of dialogue, all with heavy tool use), a 15-question recall exam each. 104 of the 105 questions were answerable by an oracle holding the whole transcript, and recall is scored on those. The capsule writer and the answerer are `z-ai/glm-5.3-flash`, the exam and judge `google/gemini-3.8-flash`, Jev `jev-latest`. Every arm writes the same 400-word capsule with the same writer.

**Results** (closed-book = capsule only; "one search" = capsule plus one retrieval):

| What the writer read | closed-book | with one search | chars read |
|---|---|---|---|
| Plain last 24,000 chars (the fallback) | **48.1%** | 68.3% | 24,940 |
| The whole dialogue | 46.2% | 67.3% | 88,609 |
| Last 24,000 chars, different prompt wording | 40.4% | **73.1%** | 24,770 |
| **Jev picking turns (what 0.13.2 shipped)** | **37.5%** | 68.3% | 17,434 |
| Fail-open, i.e. what a Jev outage gave | 33.7% | 61.5% | 12,511 |
| Regex-kept identifier-shaped turns | 31.7% | 62.5% | 24,940 |
| Jev's own counts, chosen by recency | 30.8% | 60.6% | 12,757 |
| No capsule at all | — | 56.7% | 0 |

What 0.14.0 shipped instead — the whole dialogue (up to 300,000 characters), a 1,200-word budget, no Jev — scores **58.7% / 75.0%**.

**Three readings from the author, the third being the one that matters**:

1. **Jev's judgement is real; the approach built on it is what lost.** Given the same number of marks, Jev's beat recency — 11 questions won to 4 lost (12 to 4 with a search). But the capsule written from the Jev digest lost to one written from a plain tail of the same size, 4 won to 15 lost. The author's suspected cause is specific: a `summarize` turn survives as its first 400 characters, and five of the seven sessions average 1,400–7,400 characters a turn — **no choice of turns recovers what clipping them throws away**.
2. **How much the writer read was not the limit at 400 words.** The whole dialogue did no better than its last quarter; the capsule was simply full. Moving the number takes both: read everything *and* write 1,200 words.
3. **One search is worth more than any of it.** Every arm gained 20 to 33 points, and a session with no capsule but one search beat every closed-book capsule.

**Two "obviously right" improvements were also measured, and neither worked**: placing kept lines before any background and sweeping identifiers out of clipped text (`digest_v2`) scored 30.8% against 37.5%, 5 won to 12 lost; appending a free regex-harvested identifier list scored 49.0% against 48.1% (4 won, 3 lost) but **cost 13 points when given to a session with no capsule** (43.3% against 56.7%, 4 won and 18 lost).

**Where the facts actually were**: of the 104 questions, the best supporting turn was tool output for 48, assistant text for 32 and the person's own words for 24. **No arm can read tool output**, because the handoff plugin doesn't export it — and the shipped configuration still answered 22 of those 48, because agents restate much of what their tools return.

## 2. Skill selection's stage 2: kept, because stage 1 is confidently wrong

[`evals/skill-pick/SCORECARD-2026-09-22.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/skill-pick/SCORECARD-2026-09-22.md)

Stage 1 cuts the catalog into batches of 120 and asks one Choice per batch; stage 2 is a second request — one `needs_skill` plus one Noul per finalist. The question is whether those ~500 ms earn their place. 14 cases (10 that should reach one named skill, 4 deliberately unremarkable ones that want none), on two catalog sizes:

| Arm | Catalog | n | right | **wrong** | spurious | missed |
|---|---|---|---|---|---|---|
| Stage 1 only | 10 skills | 14 | 10 | 0 | **4** | 0 |
| Both stages (shipped) | 10 skills | 14 | 14 | 0 | **0** | 0 |
| Stage 1 only | 379 skills | 28 | 18 | **2** | 8 | 0 |
| Both stages (shipped) | 379 skills | 28 | 22 | **0** | 6 | 0 |

Median latency 428 ms (10 skills) and 489 ms (379).

**Two wrong answers decide it**:

```
click through the checkout flow in the browser and confirm each step
  stage 1 alone:  dogfood  (0.96, then 0.94 on the repeat)   <- wrong, and certain
  shipped:        jev-browser-use (needs_skill 0.85)         <- right
```

In their words, this is the failure a floor cannot catch: **the floor only sees how sure the answer is, and this one was sure.** It's the cleanest third-party instance of confident-wrong we've collected, and it was caught on a shipping product's decision path.

The author's own caveats: the expectations were written by the same hands that run the eval, so it measures agreement with a written intent rather than ground truth; the `None` labels only hold for the catalog they were written against, so the fleet arm's spurious counts are an upper bound and the signal to read is the two confident-wrong picks; the small-catalog arm ran once per case.

## 3. The second question on action choice: real signal, not adopted

[`evals/choose-match/SCORECARD-2026-09-21.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-21.md)

Stagehand's Act accepts a Jev pick only after asking two questions — which candidate is best, and **whether any candidate matches the goal at all** — while this repo gates on a single confidence floor. They ran 31 labelled cases (16 answerable, 8 traps, 7 with no answer) five times, both questions in the same request, replaying every gate offline.

**The second question does carry real signal**: the no-answer band tops out at 0.43–0.45 in every run while everything else starts at 0.61, so "nothing here serves the goal" is separable. Confidence alone separates it less cleanly (two no-answer cases landed at 0.58–0.70).

**It buys nothing for the decision the gate makes**: the current single-question floor at 0.65 produced **zero wrong actions in all five runs**. The one known wrong answer ("cancel this dialog without losing my work" → picks *Save*) came back at 0.45–0.60 every time, under the floor — while its `match` is 0.79–0.83, so **a match-only gate clicks that wrong button in every run**.

The conclusion is carefully stated: "zero wrong actions leaves the second question no room to help," and absence of an improvement is a weaker claim than a demonstrated harm; also, 0.65 was calibrated on these very 31 cases, so the comparison is played on the floor's home turf and cannot show the floor isn't overfitted to them. A [companion scorecard](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-22-stakes-and-margin.md) replayed 18 gate families (a higher bar for irreversible candidates, a required margin between first and second place) over 93 case-decisions and **not one row differed** from today's floor, so nothing shipped there either.

## 4. A measurable way to write a question: separate the requirement from the preferences

[`docs/writing-a-jev-question.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/docs/writing-a-jev-question.md)

A vendor running Jev in production (Virlo, a short-form video research tool) reported that their largest single accuracy jump came not from a bigger model or a longer prompt but from one sentence. Their task: decide whether a video belongs to a stated topic. Their first version described the whole brief — topic, tone, format, audience — and **Jev read every one of those as a hard requirement**: **16 of 44** on a human-labelled set. Rewriting so that the *topic* was the requirement and everything else was explicitly a tie-breaking preference: **33 of 44**. Same model, same test set, same code path.

The mechanism is the core axis again: Jev scores your options against your state and **has no way to know which line of your state is the binding one**, so a soft attribute becomes a filter. The author's per-shape advice: for Choice, name the deciding attribute and then name the tie-breakers; for Score, say which rubric levels are gated by the requirement and which absorb preferences; Noul bites hardest, because a yes/no with an unstated "and also" is really two questions.

**Discount this one**: the primary source is an X post ([@dsqjaffa](https://x.com/dsqjaffa), 2026-09-21), self-reported by a vendor selling the product, n=44 with no per-case breakdown, and we cannot fetch X — we can verify only that hermes' documentation reports it this way. The author says the same: "treat it as a strong default to try and measure, not a law." Use it as a hypothesis, not a conclusion.

## 5. Jev is a cloud API, and the state is what leaves your machine

The repo's README has a section called "What leaves your machine" that spells out, per feature, what is sent. Our map hasn't covered this dimension, and it is a real criterion for whether a task suits Jev:

- **Routing**: the user's turn, redacted (emails, phones, tokens, long hex), capped at 2,500 characters. Never history, tool results, files or memory. Turns that look like they hold a secret, and any profile listed in `private_profiles`, send only coarse features: length, whether code is present, whether risk words appear.
- **Memory**: the query and up to 900 characters per passage. Your store's ids, paths and sources are replaced with `P0`, `P1`… and never sent. A passage that looks like a credential is not sent at all.
- **Choosing turns**: the first and last 350 characters of each turn. A default handoff sends Jev nothing.
- **Mailbox sorting**: the subject and up to 2,500 characters of body; the sender's **domain**, never the mailbox; a `Received:` header reduced to the date it carries, because the rest is the recipient's address and the internal IP of every hop. Mail is **decoded before it is screened** — quoted-printable, percent-encoding, HTML entities, base64 — for a concrete reason: a newsletter footer carries your own address percent-encoded in the unsubscribe link and base64'd in the tracking link, and a plain-text redactor sees neither.
- **Computer and browser use**: the goal, short element labels and your own action descriptions. Never screenshots, page text or field values.

The author is also plain about the uncomfortable part: in the default `redacted-text` mode routing sends the turn itself, redacted, and **routing happens before the agent acts, so the agent has no say in it**.

## What it means, and how much to trust it

**Method worth copying**:

- **Measure your own noise floor first.** Two arms in the compaction eval see the same text and differ only in prompt wording, and they moved about 8 points in opposite directions across the two modes. Nothing else in that table is readable without it.
- **Separate "this approach doesn't work" from "this model can't do it."** Jev's marks beat recency and the capsule built on them still lost; both are true, and the reason for the second (clipping to 400 characters) has nothing to do with Jev.
- **Write the bar down before looking at the numbers.** The stakes scorecard's script states in its docstring that a new gate must produce zero wrong actions in every run and strictly fewer stalls, before any number is seen.
- **Keep negative results in the repo, along with what would reopen them.** The skill-selection scorecard ends by naming the two conditions that would put the question back on the table.

**Our caveats**:

1. **We re-ran none of it.** Every number comes from the author's published scorecards, and the compaction eval's transcripts, exams and capsules are deliberately not in the repo — so it can be recomputed but not independently reproduced.
2. **The samples are small**: seven sessions / 104 questions, 14 cases, 31 cases. The author labels each one, which is more honest than most repo self-reports.
3. **The headline gap in the compaction eval is only a little larger than its own noise floor.** 48.1% against 37.5% is 10.6 points, against a measured wording-only effect of about 7.7. What actually carries the conclusion is the per-question **4 won, 15 lost** — that's the figure to quote, not the two averages. The whole matrix is also written, examined and judged by models, with no human labelling.
4. **The Virlo finding is second-hand and its primary source is unreachable** (above).

**How it relates to this repo's existing findings**:

- Routing, skill selection and action choice sit on the self-contained side of the core axis — the candidates are on the screen, in the catalog, in this turn's text — which is the same shape [`browser-automation.en.md`](../../browser-automation.en.md) converged on.
- **Compaction and handoffs sit on the other side, and supply a failure mode we didn't have.** What we had recorded was "the state only carried length placeholders, so the content was never exposed" (see [`translations/jev-context-compaction-debate-zh/`](../jev-context-compaction-debate-zh/)). Here the state was complete and the judgement really was better than recency; what lost was **the shape of the question itself** — however well the turns are chosen, the kept ones still survive only as their first 400 characters. Which is to say: **after you rewrite a task into a shape Jev can answer, ask once more whether that shape can still do the original job**.

## Tag

📚 (a third-party experiment and implementation; we re-ran none of its evaluations and transcribed the figures cell by cell from the author's published scorecards — links in [`SOURCE.md`](SOURCE.md))
