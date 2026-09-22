🇹🇼 中文｜🇬🇧 [English below](#virtual-humans-picking-an-expression-per-line-english)

# 虛擬人逐句選表情：現成台本上的實測

## 這組測什麼

有人在做「Jev 即時判讀台詞、決定角色表情」的產品（例如日文圈的 AnimeAct Engine，測試中），也有公開實作在跑同一個想法（[fand/jev-emotional-avatar](https://github.com/fand/jev-emotional-avatar)、[jingx8885/lov-evo](https://github.com/jingx8885/lov-evo)）。**但沒有任何一個發表過數字。** 這組補上那一格。

問題是一題 Choice：「角色說這句話時該擺出哪個表情？」我們不自己編題目，用兩份**現成的對白語料**，因為要的是別人標好的答案，不是我們自己的判斷。

兩份語料回答的是不同的問題，所以兩份都跑：

- **MELD**（英文，《六人行》影集台本）——有對話順序，所以同一批句子可以問兩次：**只給這一句** vs **給這一句＋前面最多四句**，直接量出脈絡值多少。
- **Chinese_Multi-Emotion_Dialogue_Dataset**（繁體中文，日常對話＋電影對白＋AI 生成）——沒有對話順序，只能單句；但它是繁中，正對著官方說「英文最好、CJK 較弱」那條限制 📖。

每類抽 40 句、每題重問 3 次。方法與釘住的參數見 [`protocol.yaml`](protocol.yaml)。

問法的分界線抄自 fand 那個實作（MIT）：**判斷這句話表達出來的語氣，不是它談論的情緒話題、不是句子裡被引述的人、也不是說話者真正的內心狀態；模稜兩可、只是陳述事實、或短到看不出來時選「平淡」**。

## 結果

`jev-1.13.0`，2,640 次呼叫、0 次錯誤、93.7 秒、1,810,113 input tokens（約 0.076 美元）。暖機那次 766.1 毫秒，不計入。

| 臂 | 題數 | 準確率 | 亂猜 | ECE | Brier | 平均信心 | 三次都一樣 | p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| **繁中，只給這一句** | 320 | **0.807** | 0.125 | **0.049** | 0.296 | 0.819 | 0.988 | 268 / 397 ms |
| 英文，這一句＋前四句 | 280 | 0.485 | 0.143 | 0.121 | 0.706 | 0.605 | 0.971 | 270 / 388 ms |
| 英文，只給這一句 | 280 | 0.436 | 0.143 | **0.239** | 0.849 | 0.671 | 0.971 | 275 / 376 ms |

**脈絡的效果**（同一批 280 句配對比較，2,000 次題目層級 bootstrap）：準確率 **+0.049，95% CI [+0.002, +0.095]**，逐題 91 勝 50 敗。

## 這代表什麼

**⚠ 這不是「它中文比英文好」。** 兩份語料的標註方式不一樣，差別在那裡，不在語言：

- **MELD 的標籤是標註者看著影片、聽著聲音標的**，所以有一部分答案**根本不在文字裡**。收據裡的實例：`Where is Leslie?` 標 fear、`Sorry.` 標 sadness、`Well, people!` 標 sadness、`Why are there only two of you?` 標 fear——這些只看文字讀不出來。
- **中文那份是純文字標註的**，答案照定義就在文字裡。

所以這組真正量到的，是**核心那條軸在「選表情」這個任務上的落差**：同一個問法、同一顆模型，**答案在文字裡時 0.807／ECE 0.049，答案在演出裡時 0.436／ECE 0.239。**

**而且失準的方向是老樣子。** 答案不在文字裡的時候，它不是變猶豫，是**維持高信心地答錯**：`Where is Leslie?` 以信心 1.00 選 neutral、`Where are you Leslie?` 0.99、`Leslie, now would be a` 0.99。平均信心 0.671 對上 0.436 的準確率——這就是 README 裡 DAIR Emotion 那個「顯得比實際上更有把握」的模式，在這個任務上重現。

**脈絡買到的主要不是準確率，是校準。** 加上前四句，準確率只多 4.9 分（信賴區間下緣 +0.002，剛好不含 0），**但 ECE 從 0.239 掉到 0.121，幾乎砍半**，平均信心也從 0.671 降到 0.605。也就是說：看不到前文時它不只選得差，還不知道自己選得差。

**難的是哪幾類**：英文那邊 sadness 只有 0.15–0.175、fear 0.32、disgust 0.35，錯的時候幾乎都倒向 neutral——因為那些情緒在台詞文字裡通常沒有線索。中文那邊最差的是厭惡語調 0.558，倒向憤怒語調；那是真正相鄰的兩類，不是訊號不見了。

**如果要拿來當閘**：繁中那組門檻 0.7 時，覆蓋率 0.75、被覆蓋的準確率 0.882（低於門檻退回平淡語氣的話，整體會掉到 0.689——退回不是免費的）。英文那組門檻掃到 0.7 也只有 0.522，救不回來。

**給要做這件事的人一句話**：先確定你的標準答案是哪一種。**目標是「人看文字會選哪個」就是 0.8 這一區；目標是「配音員實際怎麼演」就是 0.45 這一區**，而虛擬人讀劇本的時候沒有演出可以讀。

## 限制

- **抽樣是每類 40 句的平衡抽樣**，所以這裡的準確率**不能**跟公開的 MELD 基準數字比——那些是在 42% 都是 neutral 的自然分布上算的。這裡亂猜是 1/7 與 1/8。
- **兩邊的標籤集不同**（7 類 vs 8 類），亂猜線也不同，跨語料的數字不是同一把尺。
- **兩份語料都沒有公布標註者一致性**。
- **中文那份的資料集卡片跟實際檔案對不上**：卡片列了「恐懼」與 Confuse，實際 `data.csv` 沒有恐懼、卻有「關切語調」。我們以檔案為準。
- **中文那份混了 AI 生成的對白，而且沒有來源欄位**，分不開人寫的跟模型寫的。模型寫的句子情緒通常比較不含糊，這會讓 0.807 偏高。
- **中文那份有些標準答案本身可爭議**：`你覺得人工智能會影響我們的工作嗎?` 標平淡語氣，Jev 以 0.82 選疑問語調——那是個問句。這份語料把「是不是問句」跟「聽起來不確定」放進同一個標籤。這類爭議我們沒有重標，照它的 gold 計分。
- **那份語料標示為繁體中文，但 4,159 句裡有 5 句含簡體字**（灿烂、这样、霉），是我們自己的簡體閘掃出來的；我們沒有修改語料。
- 單一 run date、單一模型版本（`jev-latest` 當天回的是 `jev-1.13.0`）。延遲是從台灣打過去量的，含網路往返。

## 資料與授權

**兩份語料的原文都不在這個 repo 裡。** MELD 上游是 GPL-3.0，而且內容衍生自受版權保護的影集台詞；中文那份是 MIT，但混有 AI 生成內容。`data/cases.json` 與 `data/_cache/` 都進了 `.gitignore`，**收據存的是每個 state 的 SHA-256，不是台詞本身**。

要稽核就重建：

```bash
python data/build_cases.py --verify runs/2026-09-23.json   # 2640 receipts, 0 hash mismatches
python score.py --check                                    # 從收據重算，數字對不上就 exit 1
```

`build_cases.py` 釘住兩份語料的 commit 與抽樣種子，所以重建是決定性的。

## 怎麼重跑

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # 印出三臂實際會送出的 state
python run.py               # 2,640 次呼叫
python score.py             # 重算並寫出 runs/<日期>-scores.json
```

## 標籤

🔬（我們自己打 API 測的；原始回應在 [`runs/`](runs/)。語料的標準答案是第三方的，不是我們標的。）

---

# Virtual humans picking an expression per line (English)

## What this measures

People are shipping "Jev reads the line, the character makes a face" products (AnimeAct Engine in the Japanese scene, in testing), and there are public implementations of the same idea ([fand/jev-emotional-avatar](https://github.com/fand/jev-emotional-avatar), [jingx8885/lov-evo](https://github.com/jingx8885/lov-evo)). **None of them has published a number.** This fills that gap.

The task is one Choice per line: *which facial expression should the avatar wear while speaking this?* We did not write the items ourselves — we used two **existing dialogue corpora**, because what we needed was somebody else's labels, not our own judgement.

The two corpora answer different questions, so both are run:

- **MELD** (English, Friends TV scripts) — carries turn order, so the same lines can be asked twice: **line only** vs **line plus up to four preceding turns**, measuring directly what context is worth.
- **Chinese_Multi-Emotion_Dialogue_Dataset** (Traditional Chinese; daily conversation, movie dialogue and AI-generated lines) — no turn order, so single-line only, but it aims squarely at the documented "English is best, CJK weaker" limit 📖.

40 lines per class, each asked 3 times. Method and pinned parameters: [`protocol.yaml`](protocol.yaml).

The question's boundary is borrowed from fand's implementation (MIT): **judge the tone expressed in the line itself, not the emotional topic, not a quoted speaker, not the speaker's actual inner state; when ambiguous, factual, or too short to tell, choose neutral.**

## Results

`jev-1.13.0`; 2,640 calls, 0 errors, 93.7 s, 1,810,113 input tokens (about $0.076). The warm-up call took 766.1 ms and is excluded.

| Arm | Items | Accuracy | Chance | ECE | Brier | Mean conf. | Same answer ×3 | p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| **Chinese, line only** | 320 | **0.807** | 0.125 | **0.049** | 0.296 | 0.819 | 0.988 | 268 / 397 ms |
| English, line + 4 turns | 280 | 0.485 | 0.143 | 0.121 | 0.706 | 0.605 | 0.971 | 270 / 388 ms |
| English, line only | 280 | 0.436 | 0.143 | **0.239** | 0.849 | 0.671 | 0.971 | 275 / 376 ms |

**What context buys** (paired over the same 280 items, 2,000 item-level bootstrap resamples): accuracy **+0.049, 95% CI [+0.002, +0.095]**, winning 91 items and losing 50.

## What this means

**⚠ This is not "it is better at Chinese than English."** The two corpora were labelled differently, and that is where the gap lives:

- **MELD's labels were assigned by annotators watching the video and hearing the delivery**, so part of the answer **is not in the text at all**. From the receipts: `Where is Leslie?` is labelled fear, `Sorry.` sadness, `Well, people!` sadness, `Why are there only two of you?` fear. None of those is recoverable from text.
- **The Chinese set was labelled from text alone**, so by construction its answer is in the text.

So what this really measures is **the core axis, applied to expression selection**: same question, same model — **0.807 with ECE 0.049 when the answer is in the text, 0.436 with ECE 0.239 when the answer is in the performance.**

**And it fails in the usual direction.** When the answer isn't in the text it doesn't get hesitant, it **stays confident and wrong**: `Where is Leslie?` chose neutral at confidence 1.00, `Where are you Leslie?` at 0.99, `Leslie, now would be a` at 0.99. Mean confidence 0.671 against 0.436 accuracy — the same "looks surer than it is" pattern the README records for DAIR Emotion, reproduced on this task.

**Context buys calibration more than accuracy.** Four preceding turns add 4.9 points of accuracy (lower CI bound +0.002, only just excluding zero) — **but ECE falls from 0.239 to 0.121, close to half**, and mean confidence from 0.671 to 0.605. Without the preceding turns it isn't only choosing worse; it doesn't know it is.

**Which classes are hard**: in English, sadness scores 0.15–0.175, fear 0.32 and disgust 0.35, nearly always falling back to neutral — those emotions usually leave no trace in the words. In Chinese the worst is 厭惡語調 (disgust) at 0.558, falling into 憤怒語調 (anger): genuinely adjacent classes, not a missing signal.

**As a gate**: on Chinese, a 0.7 threshold covers 75% of lines at 0.882 accuracy on what it covers (falling back to neutral below the threshold drops the overall figure to 0.689 — the fallback is not free). On English, even a 0.7 threshold only reaches 0.522; there is nothing to rescue.

**One sentence for anyone building this**: decide first which oracle you mean. **If the target is "what a human picks from the text," you are in the 0.8 regime; if it is "what the voice actor actually did," you are in the 0.45 regime** — and an avatar reading a script has no performance to read.

## Limitations

- **The sample is balanced at 40 lines per class**, so these accuracies are **not** comparable to published MELD numbers, which are computed on its natural distribution (42% neutral). Chance here is 1/7 and 1/8.
- **The two label sets differ** (7 vs 8 classes) with different chance lines, so the cross-corpus figures are not one ruler.
- **Neither corpus publishes inter-annotator agreement.**
- **The Chinese set's dataset card disagrees with its own file**: the card lists Fear and Confuse; `data.csv` has no fear and does have 關切語調 (concern). We followed the file.
- **The Chinese set mixes in AI-generated dialogue and has no source column**, so human-written and model-written lines can't be separated. Model-written lines tend to be less ambiguous, which inflates the 0.807.
- **Some of its gold labels are arguable**: `你覺得人工智能會影響我們的工作嗎?` is labelled 平淡語氣 (neutral) while Jev chose 疑問語調 (questioning) at 0.82 — it is a question. That corpus folds "is this a question" and "sounds uncertain" into one label. We did not relabel; those count against Jev.
- **It is labelled Traditional Chinese but 5 of its 4,159 lines contain Simplified characters** (灿烂, 这样, 霉), found by this repo's own Simplified gate. We did not modify the corpus.
- One run date, one model build (`jev-latest` answered as `jev-1.13.0`). Latency was measured from Taiwan and includes the network round trip.

## Data and licensing

**Neither corpus's text is in this repository.** MELD is GPL-3.0 upstream and derived from copyrighted TV dialogue; the Chinese set is MIT but mixes in AI-generated content. `data/cases.json` and `data/_cache/` are gitignored, and **the receipts store the SHA-256 of each state rather than the line**.

To audit, rebuild:

```bash
python data/build_cases.py --verify runs/2026-09-23.json   # 2640 receipts, 0 hash mismatches
python score.py --check                                    # recomputes from receipts; exit 1 on drift
```

`build_cases.py` pins both corpora's commits and the sampling seed, so the rebuild is deterministic.

## Reproducing

```bash
export TYPESAFE_API_KEY=<your key>
python run.py --dry-run     # print the exact states the three arms would send
python run.py               # 2,640 calls
python score.py             # recompute and write runs/<date>-scores.json
```

## Tag

🔬 (our own API calls; raw responses in [`runs/`](runs/). The gold labels are third-party, not ours.)
