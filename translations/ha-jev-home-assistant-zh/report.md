🇹🇼 中文｜🇬🇧 English below

# HA-Jev：一個 Home Assistant 整合對著真 API 量到的七件事

## 這是什麼

[AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev)（MIT）把 Jev 接進 Home Assistant：一個問題的答案變成一個感測器，另有四個可用在自動化的動作，以及一個給 Assist 語音助理用的對話代理。值得看的是它的[量測頁](https://github.com/AboveColin/HA-Jev/blob/main/site-docs/measurements.md)：每一項都是作者對著真的 API 量的（主要從荷蘭的家用網路），而且**開頭先寫了雜訊地板**——同一格重跑大約會飄 0.15，所以「看差距，不看小數點」。

## 一、Jev 會判斷，不會自己套門檻

問「洗衣機是不是洗好了、衣服還在裡面」，功率讀數分別是 1.2 W（待機）與 1450 W（運轉），每格跑五次：

| state 裡放了什麼 | 待機時 | 運轉時 | 分離度 |
|---|---|---|---|
| 只有讀數 | 0.47 | 0.26 | +0.21 |
| 規則寫進 `background`（「低於 5 W 代表待機」）| 0.70 | 0.10 | +0.60 |
| 由模板先比好，只給結論（「幾乎沒在耗電，代表待機」）| 0.74 | 0.06 | +0.69 |
| 兩個都做 | 0.72 | 0.04 | +0.68 |

**任一個做法都讓分離度大約變三倍，而且兩個不會疊加——做一個就好。**

兩個相關的量測：

- **規則放在哪很重要**：同一句話放進 state、而不是放進題目，只量到 +0.33，大約是放在題目裡的一半。
- **一句上下文的威力**：問洗衣是否完成，只給功率與門的感測器是 0.31；多加一句「程式在 14 分鐘前結束」之後是 0.80。

作者自己的結論一句話：「Jev 做判斷，不做計算」。所以「把燈調到 40%」裡的數字是用正規表示式抽出來的，不是問 Jev——正規表示式精確、免費，而且不可能搞錯 40 是什麼意思。

## 二、多問幾題幾乎不花時間

一次請求問 3 題花 712 毫秒，問 100 題花 714 毫秒——多 97 題只多 24 毫秒；400 題是 1.3 秒。**多一題花的是 token，不是時間**（一個短題目大約 38 個 input token）。

## 三、延遲：跟我們自己量的獨立對上

官方公布 70 到 500 毫秒。作者從荷蘭量 16 次：暖機後 250 到 580 毫秒，閒置一段時間後的第一次 700 到 900 毫秒；後來在真的 Home Assistant 上跑 16 句指令，暖機 257 到 455 毫秒、重啟後第一次 512 到 753 毫秒。這跟我們自己的 [`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/)（中位數 247 毫秒、暖機那一次 699 毫秒）是兩個獨立來源對上同一個形狀：**官方數字量的是靠近他們機房的情況，冷啟動要另外算**。

## 四、結構化的選項定義沒有幫助（負面結果）

官方文件說 `instructions` 與每個選項的定義可以寫成物件（例如 `what`／`not_for`／`examples`），兩個選項模糊時能把邊界劃清楚。作者拿五個刻意模糊的門鈴訪客、每個跑三次：

| 選項定義寫法 | 符合預期答案 | 平均信心 | 不穩定 |
|---|---|---|---|
| 純字串 | 12/15 | 0.90 | 0/5 |
| 結構化 `what`／`not_for`／`examples` | 12/15 | 0.87 | 0/5 |

較簡單的一組兩邊都是 12/12。作者的建議：這個功能有支援，但**只有在兩個選項真的糊在一起、而且一句白話定義已經失敗時才值得用**。

## 五、低信心不一定代表模型搞不懂

同一句「打開檯燈」、同一個裝置，每種起始狀態跑三次：

| 檯燈原本 | 動作題的信心 |
|---|---|
| 關著 | 1.00、1.00、1.00 |
| 開著 | 0.25、0.28、0.31 |

檯燈已經開著時，機率分布的排名沒有變（開燈 0.39–0.48、查詢狀態 0.30–0.35、都不是 0.22–0.30），只是攤開了——因為這時那句話真的可能是指令、也可能是在問。**只讀最高分那個答案，會讓一句「多餘的指令」看起來像聽不懂**；讀最高分選項再對照目前狀態，就能回「檯燈已經開著了」。

## 六、多題一起問時，讓信心決定信哪一題

語音指令路由的真實事故：「打開廚房的燈」，範圍題回 `one_room`、信心 0.41，裝置題回 `light.kitchen_lights`、信心 1.00。程式先看範圍題再分支，**丟掉了確定的答案、採用了不確定的那個，結果全家的燈都開了**。

作者同一節也寫明：信心值沒有公開的校準證據，官方文件稱它為「方便的預設」；在你自己的題目上量過之前，把 0.9 當成「比 0.6 高」，不要當成「十次對九次」。

## 七、選項清單本身是題目的一部分

兩個「單元測試不會發現」的失敗：

1. 房間選項是從登錄的所有房間產生的，包括裡面沒有任何可控裝置的房間。「關掉廚房的燈」以 0.98 選中那個房間——**對它被問的題目來說是對的答案，卻指向一個 agent 無法動作的地方**。修法是只列出有可控裝置的房間。
2. 「全部關掉」沒有送任何目標，Home Assistant 要求名稱、區域或樓層三擇一，結果回「抱歉，沒有成功」——**而模型本身以 0.99 答對了**。

## 成本

每一個裝置記錄大約 65.8 個 input token。在真實實例上（5 個裝置、7 題），每道指令 1,329 到 1,371 個 input token，30 道指令總共 0.0017 美元、每道 0.000057 美元。裝置少的時候，大約 1,300 token 的固定題目文字才是大頭；裝置多時換成裝置記錄是大頭。作者也分清楚了哪些是量出來的、哪些是推算的——例如 bytes-per-token 比例，他明寫那是「兩次量測之間的推導，不是同一份 payload 兩邊都數過」。

## 這代表什麼、可信到什麼程度

**值得照抄的方法**：先量雜訊地板再報差距；對著真的 API、真的實例量；把推算值跟端到端量測分開標示；把「模型答對了但系統失敗」的案例單獨記下來。

**我們的但書**：

1. **我們沒有重跑，而且原始回應沒有公開**——repo 裡沒有量測腳本或 API 回應，數字能引用、不能重算。
2. **樣本都很小**：每格 5 次、門鈴 5 個案例 × 3 次、真實實例 16 句。作者自己用「看差距不看小數點」處理這件事，但差距本身也只有這個樣本。
3. **單一作者、單一網路位置**（荷蘭的家用網路）。
4. 量測頁散文裡「原始門檻 0.06」那句跟表格對不上，我們以表格為準。

**跟本 repo 既有結論的關係**：

- **這是核心軸第二個獨立領域的量化證據。** 西洋棋那條「事實先由程式算好放進 state，比模型本身重要」（見 [`analysis/jev-games-tcg.md`](../../analysis/jev-games-tcg.md)）原本只有一個來源；這裡在感測器讀數上量到同一件事，而且給出了幅度：大約三倍的分離度。
- **跟 [jev-mcp（blakestone-x）](../blakestone-jev-mcp-zh/) 的「把兩個數字擺進 state 讓它比，64 題全對」並不衝突**：那邊是兩個值都攤在眼前、問哪個大；這邊是只給一個讀數、把門檻埋在說明裡，要它自己記住再套用。能比眼前的兩個值，不能指望它自己套一條沒寫進題目的門檻。
- **「結構化定義沒幫助」跟 jev-mcp 的「定義寫得更細只多 3.5 分」方向一致**：大收益在「從沒有定義到有一句定義」，之後的結構化是邊際的。

## 標籤

📚（第三方發表的量測；我們沒有重跑，原始回應也沒有公開，數字逐格抄自作者的量測頁，連結在 [`SOURCE.md`](SOURCE.md)）

---

# HA-Jev: seven things a Home Assistant integration measured against the live API (English)

## What this is

[AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) (MIT) wires Jev into Home Assistant: a question's answer becomes a sensor, there are four actions for automations, and a conversation agent for the Assist voice assistant. What's worth reading is its [measurements page](https://github.com/AboveColin/HA-Jev/blob/main/site-docs/measurements.md): everything on it was measured against the live API (mostly from a consumer connection in the Netherlands), and **it opens with its noise floor** — repeated runs of the same cell wander by around 0.15, so "treat the gaps as the finding rather than the digits."

## 1. Jev judges; it does not apply a threshold on its own

Asking whether the laundry is finished but still in the machine, at 1.2 W (idle) and 1450 W (running), five runs per cell:

| What the state carried | idle | running | separation |
|---|---|---|---|
| the readings alone | 0.47 | 0.26 | +0.21 |
| the rule in `background` ("under 5 W means idle") | 0.70 | 0.10 | +0.60 |
| the comparison done in the template, conclusion only ("drawing almost no power, so idle") | 0.74 | 0.06 | +0.69 |
| both | 0.72 | 0.04 | +0.68 |

**Either fix roughly triples the separation, and they don't stack — do one.**

Two related measurements:

- **Placement matters**: the same sentence put in the state rather than the question measured +0.33, about half of what it's worth on the question.
- **One sentence of context**: asking whether the laundry was finished, a power sensor and a door sensor gave 0.31; one added sentence saying the programme had finished 14 minutes ago gave 0.80.

The author's own summary: "Jev judges and does not calculate." So the number in "set the lamp to 40 percent" is pulled out by a regex, not by a question — a regex is exact, free, and cannot be wrong about what 40 means.

## 2. More questions cost almost no time

Three questions in one request took 712 ms; a hundred took 714 — 24 ms for 97 more questions; four hundred took 1.3 s. **An extra question costs tokens, not time** (roughly 38 input tokens for a short one).

## 3. Latency: independently matches our own

TypeSafe publishes 70 to 500 ms. Sixteen calls from the Netherlands: 250 to 580 ms warm, 700 to 900 ms for the first call after an idle spell; later, sixteen commands on a real Home Assistant: 257 to 455 ms warm and 512 to 753 ms for the first call after a restart. That lines up with our own [`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/) (median 247 ms, warm-up call 699 ms) — two independent sources showing the same shape: **the published figures are measured close to their own service, and cold start has to be counted separately**.

## 4. Structured option definitions didn't help (a negative result)

The docs say `instructions` and each criterion can be written as an object (such as `what`/`not_for`/`examples`) to sharpen the boundary when two options blur. On five deliberately ambiguous doorbell callers, three runs each:

| How the options were defined | agreed with the intended answer | mean confidence | unstable |
|---|---|---|---|
| flat strings | 12/15 | 0.90 | 0/5 |
| structured `what`/`not_for`/`examples` | 12/15 | 0.87 | 0/5 |

An easier set gave 12 of 12 for both. The author's advice: it's supported, but **worth reaching for only when two options genuinely blur and a plain sentence has already failed**.

## 5. Low confidence doesn't always mean the model is lost

The same sentence, "turn on the desk lamp," one device, three runs per starting state:

| lamp starts | action confidence |
|---|---|
| off | 1.00, 1.00, 1.00 |
| on | 0.25, 0.28, 0.31 |

With the lamp already on, the ranking didn't change (turn on 0.39–0.48, get state 0.30–0.35, none of these 0.22–0.30); the distribution just spread — because the sentence really could be either a command or a question. **Reading only the top answer made a redundant command look unintelligible**; reading the top option against the current state lets it answer "the desk lamp is already on."

## 6. When several questions come back together, let confidence decide which to trust

A real failure in the voice-command router: "turn on the kitchen lights" came back `one_room` at 0.41 on the scope question and `light.kitchen_lights` at 1.00 on the device question. The code branched on scope first, **throwing away the certain answer in favour of the uncertain one, and turned on every light in the house**.

The same section says plainly that confidence has no published calibration evidence and that the docs call it a convenient default; until you've measured it on your own questions, treat 0.9 as "higher than 0.6," not as "right nine times in ten."

## 7. The option list is part of the question

Two failures "a unit test would not have found":

1. Room options were built from every registered area, including rooms with nothing controllable in them. "Kill the lights in the kitchen" picked such a room at 0.98 — **the right answer to the question asked, naming somewhere the agent couldn't act**. The fix: offer only rooms that hold an exposed device.
2. "Turn everything off" sent no target, Home Assistant requires a name, area or floor, and the reply was "Sorry, that did not work" — **with the model itself right at 0.99**.

## Cost

Each device record costs about 65.8 input tokens. On a real instance (5 devices, 7 questions), each command was 1,329 to 1,371 input tokens; 30 commands cost $0.0017 in total, $0.000057 each. With few devices, the roughly 1,300 tokens of fixed question text dominate; with many, the device records do. The author also keeps measured and derived figures apart — the bytes-per-token ratio, for instance, is labelled "a derivation across two runs rather than one payload counted both ways."

## What it means, and how much to trust it

**Method worth copying**: measure the noise floor before reporting gaps; measure against the live API on a real instance; label derived estimates separately from end-to-end measurements; record "the model was right but the system failed" cases on their own.

**Our caveats**:

1. **We re-ran none of it, and no raw responses are published** — there are no measurement scripts or API responses in the repo, so the figures can be cited but not recomputed.
2. **Samples are small**: 5 runs per cell, 5 doorbell cases × 3 runs, 16 commands on the live instance. The author handles this with "gaps, not digits," but the gaps themselves rest on these samples.
3. **One author, one network location** (a Dutch consumer connection).
4. The prose line about "0.06 separation on a raw threshold" doesn't match the table; we follow the table.

**How it relates to this repo's existing findings**:

- **It's quantitative evidence for the core axis in a second, independent domain.** The chess finding that facts computed by code and put in the state matter more than the model (see [`analysis/jev-games-tcg.md`](../../analysis/jev-games-tcg.md)) had one source; this measures the same thing on sensor readings and puts a size on it: roughly triple the separation.
- **It doesn't contradict [jev-mcp (blakestone-x)](../blakestone-jev-mcp-zh/)'s "put both amounts in the state and ask which is larger: 64 of 64"**: there, both values sit side by side; here, one reading is given and the threshold is buried in prose for the model to recall and apply. It can compare two values in front of it; don't expect it to apply a threshold the question never states.
- **"Structured definitions didn't help" points the same way as jev-mcp's "richer definitions added only 3.5 points"**: the big gain is going from no definition to one sentence; structure beyond that is marginal.

## Tag

📚 (third-party measurements; we didn't re-run them and no raw responses are published; figures transcribed cell by cell from the author's measurements page, links in [`SOURCE.md`](SOURCE.md))
