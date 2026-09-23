🇹🇼 中文｜🇬🇧 English below

# jev-mcp（blakestone-x）：生產資料上的定義、順序、校準與比較

> 同名提醒：這是 **blakestone-x/jev-mcp**，不是 [`browser-automation.md`](../../browser-automation.md) 裡的 jkudish/jev-mcp。

## 這是什麼

[blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp)（MIT）把 Jev 包成一個 MCP 伺服器，讓任何 agent 都能呼叫五種型別化判斷：classify、score、check、match、screen，每個答案都附信心。它的 README 有一節「What we measured」，`RECIPES.md` 把每一項的做法與細節寫開；作者說這些量測**來自一家外勤服務公司的生產資料**。資料沒有公開，但每一項都有具體的數字與樣本數。

## 一、先把標籤定義出來：覆蓋率大跳，再寫更細只多一點

同一批分類，選項的寫法不同：

| 選項怎麼寫 | 同意率 | 信心 ≥ 0.9 那一段的同意率 | 每次請求的 token |
|---|---:|---:|---:|
| 只有標籤名稱 | 64.5% | 91.5% | 735 |
| 每個標籤一句 `what` | **81.0%** | 92.8% | 1,689 |
| `what`＋`not_for`＋`examples` | 84.5% | 94.6% | 4,745 |

作者的讀法寫在小節標題上：**「定義買到的是覆蓋率，不是精確度」**——主要是讓更多答案過得了 0.9 的信心門檻，門檻以上那一段的精確度其實沒怎麼動。從「只有名字」到「一句定義」是 +16.5 分；再加上「不適用於」和範例只多 3.5 分，token 卻是 2.8 倍。建議：**先寫一句 `what`，只在會互相混淆的那幾對上補細節**。

## 二、選項順序會翻掉 16% 的答案——但翻掉的都是低信心的

把 criteria 的順序反過來再問一次，200 題裡有 **32 題換了答案**。換掉的那些平均信心 **0.42**，沒換的平均 **0.81**。

這個伺服器因此提供一個 `ensemble: true` 選項：用不同順序再問一次，兩次不一致就一律落進「交給人看」的區間。作者建議用在**會觸發有後果動作的分類**上。

## 三、校準曲線平坦時，先懷疑標籤

在乾淨的標籤上：信心 0.8–1.0 同意 95%、0.7–0.8 同意 71%、低於 0.6 接近丟銅板。但有一組「供應商產品線」的標籤，校準曲線是平的——**因為標籤錯的頻率跟判斷一樣高**。作者的結論：平坦的校準曲線代表標籤有問題或定義模糊，不自動等於模型失敗。

## 四、把兩個數字都擺進 state 讓它比：可以

- 金額：64 個「兩個顯示金額明顯不同」的案例，問哪個大，**100%**。改成四級的差距評分，完全正確 90%，錯的都是藏在小數點後的平手。
- 日期：「是不是已經過了」**100%**；四級的逾期評分 98%。

作者同時寫明：它擅長決定哪個大、哪個晚，**但需要拿回一個精確數字時，它不能取代解析器**。

## 五、把參考表放進 state：有用，但薄的表會帶來錯的信心

300 題，在 state 裡加一份手寫的前綴對照表：同意率從 30% 升到 39%，過得了 0.9 門檻的從 37 題升到 88 題。另外問一題「有沒有用到參考表」，觸發在 97 列上，其中 70% 是對的。作者的提醒：參考表要真的、要有人維護，**一份薄的表會加上錯的信心**。

## 六、批次幾乎免費，但不是完全獨立

同一個 state 上多加 2 題相關的 Noul，100 個選擇裡改變了 1 個；多加 20 題，改變 3 個、最高機率平均移動 0.016、token 多 6%、時間多 26 毫秒。結論：批次幾乎免費、幾乎獨立，但**一個不能漂移的決定，放在它自己的請求裡**。

## 七、比對與速率限制

- **有候選時的比對**：11 次裡有 8 次選中；選錯的那幾次，「有沒有真正相符的候選」那題都很低。所以這個伺服器的 `match` 是 Choice 加一題 `exists` Noul：`exists ≥ 0.70` 且 Choice 信心 ≥ 0.50 才算相符，中間值交給人，低值回「沒有」。
- **速率限制**：官方沒有公布。作者在一把早期使用的金鑰上觀察到：小請求每秒 160 次、延遲持平、沒有被擋；但每秒約 40 次、每次 1,700 token 持續跑，三分鐘後開始出現 429。建議**把速率限制當成「每分鐘多少 token」，不是「每秒多少請求」**，批次工作要能續跑，被擋時退避幾秒而不是幾毫秒。

## 這代表什麼、可信到什麼程度

**我們的但書**：

1. **我們沒有重跑，資料也沒有公開**——題目、標籤、原始回應都沒有，數字只能照作者的說法引用。
2. **標籤品質本身沒說明**，而作者自己就撞過一組錯得跟判斷一樣多的標籤；同意率的分母有不確定性。
3. **單一公司、單一領域**（外勤服務），樣本 64 到 300 不等。

**跟本 repo 既有結論的關係**：

- **「從沒有定義到一句定義 +16.5 分」是目前最直接的證據：要 Jev 判斷一件事，先把那件事定義出來。** 這也是「檢查一篇文字符不符合某些寫作要素」能不能交給 Jev 的關鍵：要素沒被定義時，它只能猜你要什麼；定義成一句話之後，答案才真的在文字裡。
- **跟 [HA-Jev](../ha-jev-home-assistant-zh/) 的兩個發現一致**：HA-Jev 量到結構化定義（`what`／`not_for`／`examples`）在 15 個模糊案例上完全沒差，這裡量到它只多 3.5 分——大收益都在第一句定義。
- **跟 HA-Jev「Jev 不會比數字」看起來衝突，其實不衝突**：這裡是兩個值都攤在 state 裡、問哪個大；HA-Jev 是只給一個讀數、把門檻埋在說明裡、要它自己記住再套用。**能比眼前的兩個值，不能指望它自己套一條沒寫進題目的門檻**——兩邊加起來的做法是：比較需要的兩邊都攤進 state，或乾脆由程式先比好、只給結論。
- **選項順序偏誤是地圖上第一個量化證據。** 我們 README 引過的黑箱實驗說「同一題的選項會一起讀、多一個無關選項會改變其他選項之間的比例」；這裡量到的是更直接的後果：光是換順序就翻掉 16%，而且翻掉的集中在低信心——所以信心門檻本來就擋掉了大部分。

## 標籤

📚（第三方發表的量測；我們沒有重跑，資料沒有公開，數字逐格抄自作者的 README 與 `RECIPES.md`，連結在 [`SOURCE.md`](SOURCE.md)）

---

# jev-mcp (blakestone-x): definitions, ordering, calibration and comparison on production data (English)

> Name check: this is **blakestone-x/jev-mcp**, not the jkudish/jev-mcp cited in [`browser-automation.en.md`](../../browser-automation.en.md).

## What this is

[blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp) (MIT) wraps Jev as an MCP server so any agent can call five typed judgments — classify, score, check, match, screen — each with a confidence. Its README has a "What we measured" section and `RECIPES.md` spells each item out; the author says the measurements **come from a field-service company's production data**. The data isn't public, but every item comes with concrete figures and sample sizes.

## 1. Define the labels first: coverage jumps; defining them further adds a little

The same classification, with the options written differently:

| How the options are written | agreement | agreement at confidence ≥ 0.9 | tokens per request |
|---|---:|---:|---:|
| bare label names | 64.5% | 91.5% | 735 |
| one-line `what` per label | **81.0%** | 92.8% | 1,689 |
| `what` + `not_for` + `examples` | 84.5% | 94.6% | 4,745 |

The author's reading is in the section title: **"descriptions buy coverage, not precision"** — mostly they let more answers clear the 0.9 confidence gate, while precision inside that band barely moves. Bare names to one sentence is +16.5 points; adding "not for" and examples adds 3.5 more at 2.8× the tokens. Advice: **start with a one-line `what` and add detail only to the pairs that get confused**.

## 2. Option order flips 16% of answers — but the flips are the low-confidence ones

Asking again with the criteria in reverse order changed **32 of 200** answers. The flipped items averaged **0.42** confidence; the stable ones **0.81**.

So the server offers `ensemble: true`: ask again in a different order and, if the two disagree, always put the result in the "review" band. The author recommends it for **classifications that gate a consequential action**.

## 3. A flat calibration curve is a label warning first

On clean labels: 95% agreement at confidence 0.8–1.0, 71% at 0.7–0.8, and near a coin flip below 0.6. But one "vendor product line" label set gave a flat curve — **because the labels were wrong as often as the judgment**. The author's conclusion: a flat calibration curve means the labels are bad or ambiguous; it is not automatically a model failure.

## 4. Put both numbers in the state and ask which is larger: that works

- Amounts: 64 cases where the two displayed amounts visibly differed, asked which is larger — **100%**. As a four-level distance Score, exact 90%, with every miss a hidden sub-dollar tie.
- Dates: "is it past" **100%**; a four-level overdue Score 98%.

The author adds: it's good at deciding what is larger or later, **but it is not a replacement for a parser when you need an exact number back**.

## 5. A reference table in the state helps, but a thin one adds the wrong confidence

On 300 items, adding a hand-written prefix catalog to the state raised agreement from 30% to 39% and the count clearing a 0.9 gate from 37 to 88. A separate "did it use the reference" Noul fired on 97 rows, 70% of them rightly. The author's warning: the reference has to be real and maintained — **a thin catalog can add the wrong confidence**.

## 6. Batching is nearly free, but not fully independent

Adding two related Nouls on the same state changed 1 of 100 choices; adding 20 changed 3, moved the top probability by 0.016 on average, added 6% tokens and 26 ms. Conclusion: batching is nearly free and nearly independent, but **a decision that must not drift goes in its own request**.

## 7. Matching and rate limits

- **Matching when a candidate exists**: 8 of 11 picks matched; the misses all had a low "does any candidate genuinely match" answer. So the server's `match` pairs a Choice with an `exists` Noul: a match only when `exists ≥ 0.70` and the Choice confidence is at least 0.50; middle values go to review, low values return "none."
- **Rate limits**: none are published. On one early-access key the author saw small requests run at 160 per second with flat latency and no rejections, while a sustained ~40 per second at 1,700 tokens each drew 429s after three minutes. Advice: **treat the limit as tokens per minute, not requests per second**, keep bulk jobs resumable, and back off for seconds, not milliseconds.

## What it means, and how much to trust it

**Our caveats**:

1. **We re-ran none of it and the data isn't public** — no questions, labels or raw responses, so the figures stand on the author's word.
2. **Label quality isn't described**, and the author hit one label set that was wrong as often as the judgment; the agreement denominators carry uncertainty.
3. **One company, one domain** (field service), samples from 64 to 300.

**How it relates to this repo's existing findings**:

- **"No definition to one sentence: +16.5 points" is the most direct evidence we have that you have to define the thing before Jev can judge it.** It's also the crux of whether "check a piece of writing against some writing criteria" can be handed to Jev: undefined, it can only guess what you mean; defined in a sentence, the answer really is in the text.
- **It agrees with [HA-Jev](../ha-jev-home-assistant-zh/) on two points**: HA-Jev found structured definitions (`what`/`not_for`/`examples`) made no difference on 15 ambiguous cases, and here they add only 3.5 points — the big gain is all in the first sentence of definition.
- **It looks like it contradicts HA-Jev's "Jev doesn't compare numbers," but doesn't**: here both values sit in the state and the question asks which is larger; there, one reading is given and the threshold is buried in prose for the model to recall and apply. **It can compare two values in front of it; don't expect it to apply a threshold the question never states** — taken together: put both sides of any comparison in the state, or let code compare and hand over only the conclusion.
- **It's the map's first quantitative evidence of option-order bias.** The black-box study our README cites found that a question's options are read together and that adding an irrelevant option shifts the ratios between the others; this measures the more direct consequence — reordering alone flips 16%, concentrated in low confidence, so a confidence gate already catches most of it.

## Tag

📚 (third-party measurements; we didn't re-run them and the data isn't public; figures transcribed cell by cell from the author's README and `RECIPES.md`, links in [`SOURCE.md`](SOURCE.md))
