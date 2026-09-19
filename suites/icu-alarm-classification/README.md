🇹🇼 中文｜🇬🇧 English below

# ICU 心律警報分類：拿公開資料集驗證一則爆紅推文

> ⚠️ **這是拿公開學術資料集做的分類練習，測試 Jev 這種窄判斷模型在「生理特徵摘要」上的表現。不是臨床驗證、不是醫療器材評估、不建議用於任何實際病患照護決策。**

## 這組測什麼

日本一則爆紅推文（[`@roiyaruRIZ`](https://x.com/roiyaruRIZ)）宣稱做了一個「用 Jev 判斷生命徵象急變機率」的示範，說監測器警報常誤判身體動作、對徐脈患者持續失靈，但 Jev「精準持續預測患者狀態」。這則貼文沒有附程式碼、資料、或方法論——這組測試是拿一個真實、開放的公開資料集，重建一個對應的簡化版本，看這個宣稱能不能立得住。

## 為什麼測這個

這是我們查證那則推文時找到的一個真空的、有公認權威資料集可用的方向：**PhysioNet/CinC Challenge 2015**，750 筆 ICU 床邊監測器警報錄音，涵蓋五種心律不整類型（含極端徐脈），每筆都由至少兩位專家標註為真警報／假警報。這個任務本身在能力地圖那條軸上是**混合、偏不自足**——心律判斷理論上答案就在生理訊號裡，但「訊號」不是文字，要先轉成 Jev 能讀的文字特徵，這個轉換本身能不能保留判斷所需的資訊，是這組測試真正在測的東西。

## 方法論

**資料**：PhysioNet/CinC Challenge 2015 訓練集（750 筆，ODC-By 開放授權，免 credential），分層抽樣 30 筆，涵蓋五種心律不整類型（VTA/ETC/ASY/EBR/VFB），每種各 3 筆真警報＋3 筆假警報。抽樣清單見 `data/sample.csv`。

**特徵抽取**：`data/extract_features.py`，獨立撰寫，只用 MIT-license 的 `wfdb`／`neurokit2`，**沒有引用**任何其他專案的程式碼。刻意做成「naive」規模（不做訊號品質閘控、不做跨通道比對）：對每個 ECG 導聯用 R 波峰偵測抓心率，用**警報實際觸發時刻往前 30 秒**（不是檔案結尾——「…l」結尾的檔案在警報後還多錄了 30 秒，抓檔案結尾會抓過頭）算心率中位數／四分位距，再附一段全程 10 秒窗口的心率趨勢，跟一個簡單的雜訊/削波粗判。過程中修過一次真的問題：一開始用瞬時心率的 min/max，被單一個誤偵測的波峰拉出離譜的極值（例如同一個 30 秒窗口冒出 25bpm 又冒出 116bpm），改成中位數/IQR 後才穩定。

**問題設計**：比照我們自己在 README 補進去的建議——先試單題，真的弱才拆解。單一 Noul 問題：「這個警報是真的具臨床意義的事件，不是雜訊/導聯脫落/動作假影嗎？」，門檻 0.5。

**沒有做的事**：沒有複製 `NeillWhite/icu-false-alarm-reduction`（這個開源專案示範過同一個資料集可以做到官方評分 0.73-0.81，但沒有掛授權，不能直接搬程式碼）——只把它已發表的分數當對照組引用，連結見結果。

## 結果

真實 log 見 `runs/2026-09-19.json`（30 次真實 API 呼叫，共 28,030 input token，花費約 $0.0012）。

| 指標 | 數值 |
|---|---|
| 準確率 | 63.3%（19/30） |
| 敏感度（真警報抓到的比例） | **33.3%**（5/15） |
| 特異度（假警報正確放行的比例） | 93.3%（14/15） |
| Challenge 官方評分（`(TP+TN)/(TP+TN+FP+5·FN)`，漏放真警報罰 5 倍） | **0.271** |

跟 `NeillWhite/icu-false-alarm-reduction` 已發表的分數對照（**引用他已發表的數字，我們沒有驗證過他的結果**）：

| 方法 | 官方評分 |
|---|---|
| 保留全部警報（基準線） | 0.39 |
| **這組（Jev + naive 特徵，單題）** | **0.271** |
| NeillWhite Model 1（naive ML baseline，調過門檻） | 0.65 |
| NeillWhite Model 2（訊號品質閘控＋跨通道＋LightGBM） | 0.73（保留集 0.81） |

**這組甚至輸給「保留全部警報」這個什麼都不做的基準線**——因為官方評分對漏放真警報罰很重，而這組的錯誤幾乎全部是漏放（10 個 FN，只有 1 個 FP）。

依心律不整類型拆開看，敏感度差很多：

| 類型 | 敏感度 |
|---|---|
| Asystole（心搏停止） | **0%**（3/3 全漏） |
| Ventricular Tachycardia | **0%**（3/3 全漏，另誤判 1 個假警報） |
| Bradycardia | 33%（1/3） |
| Tachycardia | 67%（2/3） |
| Ventricular Fibrillation | 67%（2/3） |

## 這代表什麼

**Asystole 跟 VTA 完全掛掉，而且有清楚的訊號處理理由，不是隨機失手**：Asystole 的判準是「連續 ≥4 秒沒有心跳」，我們抽的特徵是 30 秒窗口的心率中位數——一段 4 秒的停頓，被 30 秒窗口平均掉了；VTA 的判準本質是 **QRS 波形變寬變形**，不是心率快慢，這組特徵完全沒有形態學資訊。Bradycardia／Tachycardia／Ventricular Fibrillation 表現相對好（33-67%），剛好是「心率本身的數值/變異程度就是診斷特徵」的三種類型——**這再次印證本 repo 核心那條軸：state 裡沒有判斷所需的特定資訊，Jev 沒辦法變出來，而且失效的方式精準對應到「這個特徵集缺了什麼」**，不是隨機性能下滑。

**信心值沒有表現出危險的過度自信**：答錯的 11 筆裡，`p_real` 全部落在 0.14-0.51，沒有一筆是「很有把握但錯得離譜」——比較像是「證據不夠、猶豫」，跟前面的機制解釋吻合：不是校準機制失靈，是它老實反映了拿到的證據真的不足以判斷。這點呼應 `suites/history-recall-context/` 的教訓，但方向相反：那組是「沒給該給的資訊，還很有信心」，這組是「沒給該給的資訊，信心也老實跟著下修」——同一個「state 不完整」的原因，這次沒有出現「自信答錯」那種更危險的失效模式，值得記一筆但不代表通則。

**回到 `@roiyaruRIZ` 那則推文**：在這個簡化重建裡，宣稱站不住——用一個刻意做得陽春的特徵集，Jev 連「什麼都不做、全部當真警報」這個基準線都打不過，尤其在心搏停止跟心室頻脈這兩種真正攸關生死的類型上完全抓不到訊號。**這不能反過來讀成「Jev 不能用在生理訊號分類」**——真正的問題出在我們刻意選擇的陽春特徵抽取，而不是 Jev 本身；`NeillWhite` 的完整版證明這個任務用對的特徵（訊號品質閘控＋跨通道確認＋形態學）可以做到 0.73-0.81，只是那套工程本身就是一個真正的訊號處理專案，不是把生理波形轉成幾行文字餵給窄判斷模型就能繞過的捷徑。

## 限制

N=30（跨五種類型分層，每種僅 6 筆），單一次執行、無重跑驗證變異程度；特徵抽取刻意做成 naive 規模，不是這個任務能達到的能力上限；`p_real≥0.5` 這個門檻沒有針對這個任務調過，Challenge 官方評分對 FN 罰 5 倍，實務上應該調低門檻換取更高敏感度（代價是特異度下降），這組沒有做門檻搜索；跟 `NeillWhite` 的比較是引用他已發表的數字，不是我們獨立驗證過的重跑。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# ICU arrhythmia alarm classification: testing a viral tweet against a public dataset (English)

> ⚠️ **This is a classification exercise on a public academic dataset, testing how a narrow-judgment model like Jev performs on physiological feature summaries. It is not clinical validation, not a medical-device evaluation, and not recommended for any real patient-care decision.**

## What this tests

A viral Japanese tweet ([`@roiyaruRIZ`](https://x.com/roiyaruRIZ)) claimed to have built a demo using Jev to predict acute vital-sign deterioration, arguing that hospital monitor alarms often misfire on body movement and fail persistently for bradycardia patients, while Jev "precisely and continuously predicted patient state." The post included no code, no data, and no methodology. This suite reconstructs a simplified, honest version of that claim on a real, open public dataset to see whether it holds up.

## Why this task

This is the gap we found while verifying that tweet, one with a recognized, authoritative open dataset available: **PhysioNet/CinC Challenge 2015**, 750 ICU bedside-monitor alarm recordings across five arrhythmia types (including extreme bradycardia), each labeled true/false alarm by at least two expert annotators. On this repo's core axis, the task is **mixed, leaning not-self-contained**: the answer is in principle present in the physiological signal, but "signal" isn't text — it has to be converted into a textual feature Jev can read, and whether that conversion preserves what the judgment actually needs is what this suite is really testing.

## Methodology

**Data**: PhysioNet/CinC Challenge 2015 training set (750 records, ODC-By license, no credentialing required), stratified sample of 30 across five arrhythmia types (VTA/ETC/ASY/EBR/VFB), 3 true + 3 false alarms per type. Sample list in `data/sample.csv`.

**Feature extraction**: `data/extract_features.py`, independently written, using only MIT-licensed `wfdb`/`neurokit2` — **no code copied** from any other project. Deliberately kept naive in scope (no signal-quality gating, no cross-channel confirmation): R-peak detection per ECG lead for heart rate, with median/IQR computed over **the 30 seconds before the alarm's actual trigger time** (not the end of the file — "…l"-suffixed files record 30 more seconds after the alarm, so using file-end would overshoot), plus a full-recording 10-second-window HR trend and a crude noise/clipping flag. One real bug was caught and fixed along the way: instantaneous-beat-to-beat min/max HR was getting distorted by single misdetected peaks (e.g. 25bpm and 116bpm both appearing in the same 30s window); switching to median/IQR fixed it.

**Question design**: following our own README's guidance — try a single question first, decompose only if it's genuinely weak. One Noul question: "is this alarm a real, clinically significant event, not an artifact/lead-off/motion artifact?", threshold 0.5.

**What wasn't done**: no code was copied from `NeillWhite/icu-false-alarm-reduction` (an open-source project that demonstrates 0.73-0.81 on the official metric for the same dataset, but carries no license, so its code can't be reused directly) — its published numbers are cited as a comparison only, linked in Results.

## Results

Real log in `runs/2026-09-19.json` (30 real API calls, 28,030 input tokens total, about $0.0012).

| Metric | Value |
|---|---|
| Accuracy | 63.3% (19/30) |
| Sensitivity (true alarms caught) | **33.3%** (5/15) |
| Specificity (false alarms correctly let through) | 93.3% (14/15) |
| Challenge's official score (`(TP+TN)/(TP+TN+FP+5·FN)`, a suppressed true alarm costs 5x) | **0.271** |

Compared against `NeillWhite/icu-false-alarm-reduction`'s published numbers (**citing their published figures, we did not verify their results ourselves**):

| Method | Official score |
|---|---|
| Keep every alarm (do-nothing baseline) | 0.39 |
| **This suite (Jev + naive features, single question)** | **0.271** |
| NeillWhite Model 1 (naive ML baseline, threshold-tuned) | 0.65 |
| NeillWhite Model 2 (signal-quality gating + cross-channel + LightGBM) | 0.73 (holdout 0.81) |

**This result loses even to "keep every alarm," the do-nothing baseline** — because the official metric penalizes suppressed true alarms heavily, and this suite's errors are almost entirely suppressions (10 FN, only 1 FP).

Broken down by arrhythmia type, sensitivity varies sharply:

| Type | Sensitivity |
|---|---|
| Asystole | **0%** (0/3) |
| Ventricular Tachycardia | **0%** (0/3, plus 1 false positive) |
| Bradycardia | 33% (1/3) |
| Tachycardia | 67% (2/3) |
| Ventricular Fibrillation | 67% (2/3) |

## What this means

**Asystole and VTA fail completely, and there's a clear signal-processing reason, not random bad luck**: Asystole's criterion is "no heartbeat for ≥4 continuous seconds" — the feature extracted is a median heart rate over a 30-second window, which averages a 4-second gap into invisibility. VTA's criterion is fundamentally about **wide, deformed QRS morphology**, not rate — this feature set carries no morphological information at all. Bradycardia/Tachycardia/Ventricular Fibrillation did comparatively better (33-67%) — exactly the three types where the numeric value or variability of heart rate itself *is* the diagnostic signal. **This is, again, this repo's core axis at work: when `state` lacks the specific information a judgment needs, Jev can't conjure it, and the failure maps precisely onto what the feature set is missing** — it isn't random degradation.

**Confidence didn't show the dangerous overconfident pattern**: across the 11 wrong predictions, `p_real` stayed in the 0.14-0.51 range — none were "confident and badly wrong." That's consistent with the mechanistic explanation above: not a calibration failure, but an honest reflection of genuinely insufficient evidence. This is the mirror image of `suites/history-recall-context/`'s lesson: that suite showed "missing information, high confidence anyway"; this one shows "missing information, and confidence honestly tracked it down too" — same root cause (incomplete state), a less dangerous failure mode this time, worth noting without generalizing into a rule.

**Back to `@roiyaruRIZ`'s tweet**: in this simplified reconstruction, the claim doesn't hold up. With a deliberately naive feature set, Jev couldn't even beat "treat every alarm as real," the do-nothing baseline — and it caught nothing at all on the two most life-critical categories, asystole and ventricular tachycardia. **This should not be read the other way, as "Jev can't be used for physiological signal classification"** — the real problem is the deliberately naive feature extraction we chose, not Jev itself; NeillWhite's full pipeline proves this task can reach 0.73-0.81 with the right features (signal-quality gating, cross-channel confirmation, morphology) — but that engineering is a real signal-processing project in its own right, not something a few lines of text-feature conversion can shortcut around.

## Limitations

N=30 (stratified across 5 types, only 6 per type), a single run with no repeat-variance check; feature extraction was deliberately kept naive, not this task's achievable ceiling; the `p_real≥0.5` threshold wasn't tuned for this task — the official metric penalizes FN 5x, so a lower threshold trading specificity for sensitivity would likely be the right practical choice, and this suite didn't search for it; the comparison to `NeillWhite` cites their published numbers, not an independent reproduction we verified ourselves.

## Tag

🔬 Our own test, real API calls, see `runs/`.
