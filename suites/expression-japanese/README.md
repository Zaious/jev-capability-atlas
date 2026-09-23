🇹🇼 中文｜🇬🇧 [English below](#japanese-what-a-reader-sees-vs-what-the-writer-felt-english)

# 日文表情選擇：同一句話，兩個標準答案，還有一條人類天花板

## 這組測什麼

前兩組 suite 用兩份不同的語料，對照「答案在文字裡」與「答案在演出裡」。那個比較有一個弱點：**兩份語料不只標註方式不同，語料本身也不同**，所以永遠可以說差異來自語言或題材。

[WRIME](https://github.com/ids-cv/wrime) 把這個混淆拿掉了——**同一句日文貼文，筆者本人標一次（主観），另外三個群眾標註者只看文字各標一次（客観）**。於是這組能做到前兩組做不到的三件事：

1. **測日文**。官方說英文最好、CJK 較弱 📖，我們之前只測過繁體中文。
2. **同一批句子上直接比兩個標準答案**，沒有語料差異的混淆。
3. **算得出人類天花板**。這是最重要的一件——沒有它，任何準確率都讀不出是模型不行，還是**這題人也答不出來**。

作法：一次呼叫問**兩題**（同一個 `state`，官方說多問幾題幾乎不增加等待時間 📖）——

- `expressed`：讀這篇貼文的人會接收到什麼情緒？→ 對上**三位標註者的共識**
- `felt`：筆者寫這句時自己真正感覺到什麼？→ 對上**筆者本人的自述**

選項是 Plutchik 八情緒加「平静」，題目與選項描述全用日文。400 題、每題重問 3 次、1,200 次呼叫。

## 先看人類天花板（零成本算出來的，沒有打 API）

| | 值 |
|---|---|
| 三位標註者中至少兩人一致的比例 | 0.859 |
| **一位標註者 vs 另外兩人的共識**（n=3,311） | **0.722** |
| **三人共識 vs 筆者本人的自述** | **0.524** |
| 客観共識的最大類別（期待） | 0.291 |
| 主観自述的最大類別（喜び） | 0.343 |

第三列是這整組最重要的數字：**三個人只看文字去猜筆者當時的心情，只有 52.4% 猜對。** 任何只讀文字的模型都不可能超過這條線太多——這不是模型的限制，是題目的。

## 結果

`jev-1.13.0`，1,200 次呼叫、0 次錯誤、40.1 秒、1,805,181 input tokens（約 0.076 美元）。暖機 746.4 毫秒不計入。延遲 p50 256.0、p95 333.2 毫秒。

| 問的是 | 對上哪個標準答案 | 準確率 | 最大類別 | 人類天花板 | ECE | 三次都一樣 |
|---|---|---|---|---|---|---|
| `felt` | 客観共識 | **0.594** | 0.298 | 0.722 | **0.122** | 0.950 |
| `expressed` | 客観共識 | 0.483 | 0.298 | 0.722 | 0.183 | 0.973 |
| `felt` | 主観自述 | 0.448 | 0.330 | **0.524** | 0.260 | 0.950 |
| `expressed` | 主観自述 | 0.381 | 0.330 | 0.524 | 0.283 | 0.973 |

同一次呼叫裡，兩題給同一個答案的比例是 **0.763**。

## 這代表什麼

### 一、日文的答案：能跑，但明顯低於人類水準

把它當成**第四位標註者**來看最直接：**它跟任意一位人類標註者的一致率是 0.459，而人與人之間是 0.722。** 這是我們目前對「CJK 較弱」這句官方說法最具體的一次量測。繁中那組 0.807 不能拿來推日文——那是不同語料、不同標籤集、而且**那份語料沒有人類天花板可以對照**。

延遲沒有語言差異：p50 256 毫秒、p95 333 毫秒，跟英文、繁中三組完全同一區間。

### 二、但「離人類多遠」比「準確率多少」更值得看

- 客観：0.594 / 天花板 0.722 = **82%**
- 主観：0.448 / 天花板 0.524 = **86%**

💭 兩個標準答案上它都落在人類天花板的**八成多**。也就是說，**主観那一題之所以分數低，主要不是因為模型在那裡特別差，是因為那題人也答不出來**——三個人只看文字猜筆者心情也只有 52.4%。這補上了前兩組留下的一個缺口：我們在 MELD 上說過「0.436 是因為答案在演出裡」，但當時沒有人類天花板可以證明那句話。這裡有了。

（但這個比值只是觀察，不是嚴謹的比較——兩個任務的基準線與類別分布都不同，不能因為「都是八成多」就說兩題一樣難。）

### 三、最大的單一改進來自一句話：把「不確定就選平靜」拿掉

這是這組最實用、也最意外的發現。**同一次呼叫、同一個 `state`、同一組選項**，兩題對上同一個標準答案（客観共識）：

| 題目 | 對客観共識 |
|---|---|
| `expressed`（含「はっきりしない…場合は「平静」を選んでください」） | 0.483 |
| `felt`（沒有這句退場條款） | **0.594** |

差距 **11 分**。原因看 per-class 就很清楚：`expressed` 幾乎每一類的最常見錯誤都是**平静**，而它的平静 recall 是 1.000——**我們自己寫的那句退場條款，把它推去選了一個標準答案幾乎不會給的答案**（客観共識裡平静只佔 2%：1,717 題裡 36 題）。

💭 教訓不是「不要寫退場條款」，而是：**退場選項必須跟你的標準答案／表情選單真的會用它的程度對得上**。如果你的角色幾乎不會擺一張完全沒有表情的臉，就不要在題目裡給它一條「不確定就擺沒表情」的捷徑。這跟 [`AGENTS.md`](../../AGENTS.md) 那條「必要條件跟偏好要分開寫」是同一類問題：**一句話的措辭，效果比換模型大。**

### 四、信心門檻在這裡真的有用

`felt` 對客観共識，門檻 0.7 時覆蓋率 0.562、被覆蓋的準確率 **0.742**——**高於人類彼此的 0.722**。也就是說：讓它在有把握的那 56% 上回答，剩下的交給預設或給人，它在那一段的表現跟一位人類標註者同級。ECE 0.122 也是四列裡最好的。

### 五、那到底為什麼日文比較弱？把缺口拆開

以下全部從既有收據重算，沒有再打 API（`analysis/why-japanese.py` 與 `analysis/tokens-per-char.py`）。

**先講一件我們證不出來的事：我們沒有證據說「日文比繁體中文弱」。** 繁中那組拿到 0.807，但**那份語料沒有人類天花板**——我們不知道人在那批句子上能拿幾分。這裡日文是 0.594／天花板 0.722＝**81%**，排除兩個非表情類別後是 **86%**。如果繁中那份語料的人類天花板在 0.95 附近（很可能，它混有 AI 生成、標籤不含糊），那 Jev 在繁中也就是八成多——**跟日文一樣**。兩個原始準確率是在難度不同的題目上量的，不能對接。

站得住的說法只有一句：**在這批日文句子上，它明顯低於人類**（跟任一位標註者一致 0.459，人與人 0.722）。

把這個缺口拆開，至少三塊：

| 來源 | 證據 | 佔多少 |
|---|---|---|
| **標籤集不是表情選單** | 排除「期待」「信頼」後，felt／天花板從 0.81 升到 **0.86**；只看那兩類是 0.72 | 約三分之一 |
| **我們自己的題目措辭** | 退場條款值 11 分（見上一節）。而且它**最常見的錯誤就是「期待 → 平静」（82 次）**，人類幾乎不會這樣（平静／期待 的分歧只有 9 次） | 可觀 |
| **剩下的才像語言本身** | 貼文帶顏文字／`！！`／`。。。`／`www` 這類表面標記時，felt／天花板 **0.91**；沒有時 **0.79** | 剩下的 |

💭 第三塊的解讀：**它很吃表面的情緒標記**。而日文有大量情緒是靠**終助詞、語氣形式（〜たい／〜といいな）、敬體與常體的落差、長音**承載的，不是靠情緒詞——「期待」正是這種，語感在語法裡不在詞彙裡。它在「期待」上把答案丟進「平静」，跟這條解釋一致。另外短貼文反而做得好（16 字以內 0.88），長的差（0.76–0.77），所以不像是讀不懂長句，比較像是缺少可抓的標記時就退場。

**順手證偽一個最流行的解釋：不是 tokenizer。** 用收據裡的 `input_tokens` 對字元數做最小平方擬合（`tokens = 固定開銷 + b × 字數`）：

| | 每字 tokens | 相對英文 |
|---|---|---|
| 英文（MELD 單句） | 0.254 | 1.00x |
| 繁體中文（單句） | 1.064 | 4.19x |
| **日文（WRIME 貼文）** | **0.983** | **3.87x** |

**日文每個字比繁中還便宜一點（0.92x）**，所以 token 效率解釋不了「日文 vs 中文」。它只支持「CJK vs 英文」那一層，而那一層也要打折：一個漢字承載的內容比一個英文字母多，同樣意思的句子 CJK 大約貴 1.5 到 2 倍，不是 4 倍。

**真正的機制，外面的人證不了。** TypeSafe 沒有公開架構、參數量或訓練語料比例 📖，所以「因為日文資料少」這類說法——包括我們自己可能想講的——都是猜測，不是證據。我們能量的只有行為。

**要真的回答「哪個語言比較弱」，需要的是同一批句子翻成多種語言、同一組選項、同一個標準答案的同輸入對照**（就像 [`suites/laya-head-to-head/`](../laya-head-to-head/) 對模型做的那樣）。那需要人工翻譯與重新標註，我們還沒做。

## 限制

- **WRIME 是 SNS 貼文，不是台詞**。虛擬人讀的是劇本或對話，句子的形狀不一樣，這裡的數字不能直接搬過去。
- **Plutchik 八類不是表情選單**：「期待」和「信頼」根本沒有對應的臉，而「期待」還是客観共識裡的最大類別（0.298）。這讓整組的準確率天生偏低，對做表情系統的人來說，該看的是「它跟人差多遠」而不是絕對值。「信頼」在 400 題裡幾乎不出現，recall 0.0 沒有意義。
- **單一標籤是我們從強度推導的**（八個強度取最大、全 0 為平静、平手照固定順序）。WRIME 原本是多標籤強度，不同的推導方式會給出不同的數字。
- **只收三人中至少兩人一致的句子**（85.9%），所以排除掉的是最難的那 14%。這讓所有數字（包含人類天花板）都偏樂觀。
- 單一 run date、單一模型版本。延遲從台灣量，含網路往返。

## 資料與授權

**語料原文不在這個 repo 裡。** WRIME 是 **CC BY-NC-ND 4.0**——我們既不轉載、也不散布修改版；`data/cases.json` 與 `data/_cache/` 都 gitignored，**收據存的是每個 state 的 SHA-256**。注意 NonCommercial 這一條約束的是**跑這支 suite 去下載語料的人**，不是本 repo 自己的 MIT 程式碼。

引用：Kajiwara et al., *WRIME: A New Dataset for Emotional Intensity Estimation with Subjective and Objective Annotations*, NAACL 2021。

```bash
python data/build_cases.py --stats                         # 人類天花板與基準線，不打 API
python data/build_cases.py --verify runs/2026-09-23.json   # 1200 receipts, 0 hash mismatches
python score.py --check                                    # 從收據重算，數字對不上就 exit 1
```

## 怎麼重跑

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # 印出兩題的題目與實際會送出的 state
python run.py               # 1,200 次呼叫
python score.py             # 重算並寫出 runs/<日期>-scores.json
```

## 標籤

🔬（我們自己打 API 測的；原始回應在 [`runs/`](runs/)。標準答案與人類天花板都出自 WRIME 的原始標註。）

---

# Japanese: what a reader sees vs what the writer felt (English)

## What this measures

The previous two suites contrasted "the answer is in the text" with "the answer is in the performance" using two different corpora. That comparison has a weakness: **the corpora differ in more than their annotation**, so the gap can always be blamed on language or genre.

[WRIME](https://github.com/ids-cv/wrime) removes that confound: **the same Japanese post is labelled once by its own author (subjective) and once each by three crowdworkers who only see the text (objective)**. That lets this suite do three things the earlier ones could not:

1. **Test Japanese.** The docs say English is best and CJK weaker 📖; we had only measured Traditional Chinese.
2. **Compare two oracles on identical items**, with no corpus difference in between.
3. **Compute a human ceiling.** This is the important one — without it, no accuracy number tells you whether the model is weak or **the question is one people can't answer either**.

Method: **two questions in one request** (same state; the docs say extra questions add almost no latency 📖) —

- `expressed`: what emotion does a reader take from this post? → scored against the **three-reader consensus**
- `felt`: what was the writer actually feeling? → scored against the **writer's own self-report**

Options are Plutchik's 8 plus 平静 (neutral), with the question and all option descriptions written in Japanese. 400 items, 3 repeats, 1,200 calls.

## The human ceiling first (computed offline, no API calls)

| | Value |
|---|---|
| Posts where at least 2 of 3 readers agree | 0.859 |
| **One reader against the other two's agreement** (n=3,311) | **0.722** |
| **Reader consensus against the writer's self-report** | **0.524** |
| Largest class in the reader consensus (期待, anticipation) | 0.291 |
| Largest class in the writer self-report (喜び, joy) | 0.343 |

The third row is the most important number here: **three people reading only the text guess the writer's actual feeling correctly 52.4% of the time.** No text-only model should be expected to go much past that — it is a property of the question, not of the model.

## Results

`jev-1.13.0`; 1,200 calls, 0 errors, 40.1 s, 1,805,181 input tokens (about $0.076). Warm-up 746.4 ms, excluded. Latency p50 256.0 ms, p95 333.2 ms.

| Question | Oracle | Accuracy | Majority class | Human ceiling | ECE | Same answer ×3 |
|---|---|---|---|---|---|---|
| `felt` | reader consensus | **0.594** | 0.298 | 0.722 | **0.122** | 0.950 |
| `expressed` | reader consensus | 0.483 | 0.298 | 0.722 | 0.183 | 0.973 |
| `felt` | writer self-report | 0.448 | 0.330 | **0.524** | 0.260 | 0.950 |
| `expressed` | writer self-report | 0.381 | 0.330 | 0.524 | 0.283 | 0.973 |

Within a single call, the two questions give the same answer **76.3%** of the time.

## What this means

### 1. The Japanese answer: it works, but clearly below human level

The most direct reading is to treat it as **a fourth annotator**: **it agrees with any single human reader 0.459 of the time, where humans agree with each other 0.722.** That is the most concrete measurement we have of the official "CJK is weaker" note. The Chinese suite's 0.807 cannot be carried over — different corpus, different label set, and **that corpus had no human ceiling to compare against**.

Latency shows no language effect: p50 256 ms, p95 333 ms, the same band as the English and Chinese suites.

### 2. But "how far from a human" matters more than the raw accuracy

- Reader oracle: 0.594 / ceiling 0.722 = **82%**
- Writer oracle: 0.448 / ceiling 0.524 = **86%**

💭 On both oracles it lands at roughly four-fifths of the human ceiling. Which means **the writer-oracle score is low mostly because the question is hard for people too** — three humans reading the text only manage 52.4%. That fills a gap the earlier suites left: we said on MELD that 0.436 was because the answer lived in the performance, but we had no ceiling to prove it. Here we do.

(This ratio is an observation, not a rigorous comparison — the two tasks have different baselines and class distributions, so "both about four-fifths" does not mean they are equally hard.)

### 3. The single biggest improvement came from one sentence: dropping "choose neutral when unsure"

This is the most practical and most surprising result here. **Same call, same state, same options**, both questions scored against the same oracle (the reader consensus):

| Question | Against the reader consensus |
|---|---|
| `expressed` (contains "when unclear… choose 平静") | 0.483 |
| `felt` (has no such escape clause) | **0.594** |

An **11-point** gap. The per-class breakdown explains it: nearly every class's most common error under `expressed` is **平静**, and its 平静 recall is 1.000 — **our own escape clause pushed it toward an answer the oracle almost never gives** (neutral is 2% of the reader consensus: 36 of 1,717).

💭 The lesson isn't "never write an abstention clause", it's that **the abstention option has to match how often your oracle or expression menu actually uses it**. If your character almost never wears a blank face, don't hand the model a shortcut to "blank face when unsure". This is the same class of problem as the "separate the requirement from the preferences" rule in [`AGENTS.en.md`](../../AGENTS.en.md): **one sentence of wording outweighs changing the model.**

### 4. A confidence threshold genuinely helps here

For `felt` against the reader consensus, a 0.7 threshold covers 56.2% of items at **0.742** accuracy on what it covers — **above the 0.722 humans manage with each other**. Let it answer only where it is confident and hand the rest to a default or a person, and on that portion it performs at the level of one human annotator. Its ECE of 0.122 is also the best of the four rows.

### 5. So why is Japanese weaker? Decomposing the gap

Everything below is recomputed from the existing receipts, with no further API calls (`analysis/why-japanese.py` and `analysis/tokens-per-char.py`).

**First, something we cannot show: we have no evidence that Japanese is weaker than Traditional Chinese.** The Chinese suite scored 0.807, but **that corpus has no human ceiling** — we don't know what people would score on those sentences. Here Japanese is 0.594 against a 0.722 ceiling = **81%**, or **86%** once the two non-facial classes are excluded. If the Chinese corpus's human ceiling sits near 0.95 (quite likely: it mixes in AI-generated lines and its labels are unambiguous), then Jev is at roughly four-fifths of ceiling there too — **the same as Japanese**. The two raw accuracies were measured on tasks of different difficulty and don't connect.

The defensible statement is narrower: **on these Japanese sentences it is clearly below human level** (0.459 agreement with any single annotator, against 0.722 between annotators).

That gap decomposes into at least three parts:

| Source | Evidence | Share |
|---|---|---|
| **The label set is not an expression menu** | Excluding 期待 (anticipation) and 信頼 (trust), felt-over-ceiling rises from 0.81 to **0.86**; on those two classes alone it is 0.72 | About a third |
| **Our own question wording** | The abstention clause is worth 11 points (previous section), and its single most common error is **期待 → 平静, 82 times**, which humans almost never do (they disagree over 平静/期待 only 9 times) | Substantial |
| **What's left looks like the language** | On posts carrying surface markers (kaomoji, `！！`, `。。。`, `www`), felt-over-ceiling is **0.91**; without them, **0.79** | The remainder |

💭 Reading the third row: **it leans heavily on surface affect markers.** A lot of Japanese emotion is carried by sentence-final particles, modality (〜たい, 〜といいな), the gap between polite and plain register, and elongation — not by emotion words. Anticipation is exactly that kind: the feeling lives in the grammar, not the vocabulary. Its habit of dumping 期待 into 平静 fits that explanation. Short posts also do *better* (0.88 within 16 characters) and long ones worse (0.76–0.77), so this doesn't look like failing to parse long sentences; it looks like taking the exit when there's no marker to grab.

**And one popular explanation falsified in passing: it isn't the tokenizer.** Least-squares fit of `input_tokens` against character count (`tokens = overhead + b × chars`):

| | Tokens per character | Relative to English |
|---|---|---|
| English (MELD, line only) | 0.254 | 1.00x |
| Traditional Chinese (line only) | 1.064 | 4.19x |
| **Japanese (WRIME posts)** | **0.983** | **3.87x** |

**Japanese costs slightly *less* per character than Traditional Chinese (0.92x)**, so token efficiency cannot explain a Japanese-versus-Chinese difference. It supports only the CJK-versus-English layer, and even that needs discounting: a Han character carries more content than a Latin letter, so for sentences of comparable content CJK costs roughly 1.5–2× more tokens, not 4×.

**The actual mechanism is not knowable from outside.** TypeSafe publishes neither the architecture, the parameter count, nor the training-data mix 📖, so "there was less Japanese data" — including any version of it we might be tempted to write — is a guess, not evidence. Behaviour is all we can measure.

**Answering "which language is weaker" properly needs an identical-input comparison**: the same sentences translated into several languages, with the same options and the same gold labels, the way [`suites/laya-head-to-head/`](../laya-head-to-head/) does it across models. That needs human translation and re-annotation, and we haven't done it.

## Limitations

- **WRIME is SNS posts, not dialogue.** A virtual character reads scripts or conversation; the shape of the sentences differs, so these numbers don't transfer directly.
- **Plutchik's 8 is not an expression menu**: 期待 (anticipation) and 信頼 (trust) have no corresponding face, and 期待 is the largest class in the reader consensus (0.298). That depresses the absolute accuracy, so for anyone building an expression system the number to read is the distance from the human ceiling, not the raw value. 信頼 barely appears in 400 items, so its 0.0 recall means nothing.
- **The single label is our derivation** (argmax of the 8 intensities, 平静 when all are 0, ties broken in a fixed order). WRIME is natively multi-label intensity; a different derivation gives different numbers.
- **Only posts where at least 2 of 3 readers agree are kept** (85.9%), so the hardest 14% are excluded. That makes every number here, including the human ceilings, optimistic.
- One run date, one model build. Latency measured from Taiwan, including the network round trip.

## Data and licensing

**The corpus text is not in this repository.** WRIME is **CC BY-NC-ND 4.0** — we neither redistribute it nor distribute a modified version; `data/cases.json` and `data/_cache/` are gitignored and **the receipts store the SHA-256 of each state**. Note that the NonCommercial term binds **whoever downloads the corpus by running this suite**, not this repository's own MIT-licensed code.

Citation: Kajiwara et al., *WRIME: A New Dataset for Emotional Intensity Estimation with Subjective and Objective Annotations*, NAACL 2021.

```bash
python data/build_cases.py --stats                         # human ceilings and baselines, no API calls
python data/build_cases.py --verify runs/2026-09-23.json   # 1200 receipts, 0 hash mismatches
python score.py --check                                    # recomputes from receipts; exit 1 on drift
```

## Reproducing

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # print both questions and the exact state
python run.py               # 1,200 calls
python score.py             # recompute and write runs/<date>-scores.json
```

## Tag

🔬 (our own API calls; raw responses in [`runs/`](runs/). The gold labels and the human ceilings come from WRIME's original annotation.)
