🇹🇼 中文｜🇬🇧 English below

# 抓「自證式解釋」：正規表示式抓不到的那一維，Jev 抓不抓得到

> **⚠ 更正（2026-09-23，發布當天）**：這組的主要結論已撤回。判準的作者（babel-antiai 的作者）覆核標籤後，認為 **S2 那 15 段全部是正當的說明**（「該有的說明要有」），S4 也傾向正當（S4-07 有點遲疑）。原本我們寫的「沒有詞彙標記的 15 段，掃描器 0、Jev 15」其實是 **Jev 把 15 段正當說明誤報成自證**。更根本的問題是：**題目是我們自己照判準的字面編的，不像真實的 AI 味**。作者指出真實、常見的情況是另一種——跟 LLM 來回討論、自己內心轉折的**過程**，最後被織進文章裡，讀者其實不需要知道。這種東西憑空編不出來。原始標籤保留在 `data/cases.json`，作者的判定在 `data/labels-author-review.json`，`score.py` 兩份都算。下面「結果」一節是原標籤下的數字，照舊保留以便對照；結論以「更正後的讀法」為準。

## 這組測什麼

「AI 味」裡有一類不是用詞問題，是**功能**問題：一句話的功能在替作者辯白、展示他想過了，而不在幫讀者做決定。[babel-antiai](#關於-babel-antiai)（本 repo 維護者的私有 skill）把它叫做 SELF-JUSTIFY，判準只有一句：

> **刪掉這句，讀者還能做出同樣的決定嗎？能，就刪。**

babel-antiai 的確定性掃描器只能抓「有語法痕跡」的五種形狀——理由宣告、破折號自我旁白、預先辯護、工時清單、自誇比較級。它自己的文件記錄了這個限制：一封信裡被人工刪修的 11 處，掃描器只抓到 4 處，剩下 7 處（自誇包裝、對已經懂的人解釋他懂的事、講道理給不需要的人）沒有詞彙標記。它也記錄了反方向的問題：方法論理由、對不熟脈絡讀者的鋪陳、必要的免責，會被形狀命中，但都是正當的。

所以這組問的是：**在正規表示式抓不到的地方，Jev 能不能照那一句判準讀出來？在正規表示式誤報的地方，Jev 分不分得開？** 照核心那條軸，它是候選——判斷所需的東西（這句話、這段在叫讀者做什麼）都在文字裡。

## 方法論

**資料**：60 段繁體中文，全部由本 repo 維護者為這組撰寫並標註（段落層級：這段裡有沒有至少一句自證式解釋）。分五層：

| 層 | 內容 | 段數 | 標籤 |
|---|---|---|---|
| S1 | 自證式，帶五種形狀之一（各 3 段；刻意用不同說法，例如「原因講明白」「先把理由講清楚」「我說明一下為什麼」）| 15 | 是 |
| S2 | 自證式，沒有詞彙標記（自誇包裝、對已經懂的人解釋、講道理給不需要的人，各 5 段）| 15 | 是 |
| S3 | 正當的解釋，但用了五種形狀之一（各 2 段；例如「原因講明白：舊版升級時會重複扣款」）| 10 | 否 |
| S4 | 正當的解釋，沒有形狀（做法的理由、對新手的鋪陳、必要的免責與提醒）| 10 | 否 |
| S5 | 普通段落，沒有解釋功能 | 10 | 否 |

**三個臂**：

- **掃描器**：babel-antiai 的 `ai-quality-scan.sh` v1.3（`--lang zh`），SELF-JUSTIFY 有命中就算「是」。在本機跑，收據只存逐段結果與腳本的 sha256，不存程式碼。
- **J1 只給判準**：一題 Noul，逐字用上面那句判準（加上「功能在替作者辯白、展示他想過了，而不在讓讀者做決定」的定義）。
- **J2 判準＋例外**：J1 再加一句，點名三種正當的解釋不算——說明做法的理由、對不熟背景的讀者補前提、必要的免責與提醒。這三種取自 babel-antiai 自己記錄的「正當、不該抓」的情況。

每段、每個 Jev 臂各問三次，取平均，門檻 0.5（另報 0.3 與 0.7）。兩個 Jev 臂分開請求。問法寫死在 `run.py`，參數釘在 `protocol.yaml`。

**先凍結、後執行**：60 段與標籤在任何掃描或 API 呼叫之前就以 commit `6a1f110` 推上 GitHub。之後的標籤修改都會記在這份 README，附修改前後的分數。

## 結果

收據：`runs/2026-09-23.json`（360 次呼叫、0 失敗，全部由 `jev-1.13.0` 回答，173,712 input tokens，約 0.007 美元；暖機 352.6 毫秒不計入）、`runs/2026-09-23-scanner.json`；評分：`runs/2026-09-23-scores.json`（`python score.py --check` 可從收據重算）。

**每一層被標成「是」的段數（門檻 0.5）**：

| 臂 | S1 自證＋形狀 | **S2 自證、無標記** | **S3 正當＋形狀** | S4 正當、無形狀 | S5 普通 | 準確率 | 精確率 | 召回率 |
|---|---|---|---|---|---|---|---|---|
| 掃描器 | 6/15 | **0/15** | **7/10** | 0/10 | 0/10 | 0.483 | 0.462 | 0.20 |
| J1 只給判準 | 15/15 | **15/15** | 4/10 | 5/10 | 0/10 | 0.850 | 0.769 | 1.00 |
| J2 判準＋例外 | 15/15 | 12/15 | **0/10** | 1/10 | 0/10 | 0.933 | 0.964 | 0.90 |

（S1–S2 是抓到幾段，越多越好；S3–S5 是誤報幾段，越少越好。）

- **排序能力**（AUC，隨機拿一段是、一段否，前者分數較高的機率）：J1 0.981、J2 0.974。三次重問落在門檻同一側：J1 98.3%、J2 100%。延遲中位數約 227 毫秒。
- **跟掃描器逐段比**（2,000 次配對 bootstrap）：J2 全體 +0.45，95% CI [+0.32, +0.58]，28 勝 1 敗；J1 全體 +0.37 [+0.18, +0.53]，28 勝 6 敗。
- **加那一句例外的效果**（J2 對 J1）：S3 的誤報 4 → 0（+0.4，CI [+0.1, +0.7]），但 S2 的召回 15 → 12（−0.2，CI [−0.4, 0.0]）。

**門檻的影響**：

| 門檻 | J1：S2 抓到／S3+S4 誤報 | J2：S2 抓到／S3+S4 誤報 |
|---|---|---|
| 0.3 | 15/15 ／ 16/20 | 15/15 ／ 14/20 |
| 0.5 | 15/15 ／ 9/20 | 12/15 ／ 1/20 |
| 0.7 | 8/15 ／ 0/20 | 5/15 ／ 0/20 |

**J2 漏掉的 3 段全是「對已經懂的人解釋」**（S2-06、S2-08、S2-10：對資深工程師解釋升級要暫停寫入、對會計解釋借貸要平、對廚師解釋砧板要分開）。平均分數 0.41、0.38、0.32；J1 對同三段是 0.72、0.63、0.64。**J2 唯一的誤報是 S4-08**（電暖器的防火提醒，0.51，剛好過門檻）。

## 更正後的讀法

用判準作者的標籤重算（S2 全部改為正當；只有 S1 那 15 段算自證）：

| | 準確率 | 精確率 | 召回率 | 誤報（45 段正當說明中）| 排序能力 |
|---|---|---|---|---|---|
| 掃描器 | **0.733** | 0.462 | 0.40 | 7 | — |
| Jev・只給判準 | 0.600 | 0.385 | 1.00 | **24** | 0.950 |
| Jev・判準＋例外 | 0.783 | 0.536 | 1.00 | 13 | 0.955 |

💭 **這組能說的只剩三件，而且都比原本的結論小**：

1. **只給那一句判準，Jev 的判斷跟判準作者本人的判斷對不上**，而且偏向「什麼解釋都可疑」：45 段正當說明誤報 24 段，準確率低於零成本的掃描器。「刪掉這句，讀者還能做出同樣的決定嗎」照字面讀，對大多數說明都成立；作者本人用這句話時帶著一整套沒寫出來的判斷，Jev 拿不到。
2. **排序是對的，門檻不對**：真的自證（S1）平均分數 0.86–0.89，被誤報的正當說明（S2）0.64–0.71。排序能力 0.95，但門檻要高很多、而且要在真實資料上校，這組的 60 段不夠。
3. **掃描器那一側的數字不受影響**：S2 沒被命中本來就對；它在 S3 誤報 7/10、在 S1 只抓到 6/15，照舊成立。

**這組沒有回答原本的問題**：「正規表示式抓不到的那種自證，Jev 抓不抓得到」——因為我們編的「抓不到的那種」根本不是自證。要回答，需要真實的文章：作者跟 LLM 討論後組織出來的稿子，以及作者自己標出「這段是過程殘留、讀者不需要」的地方。那是下一輪。

## 原標籤下的讀法（已被上面取代，保留對照）

💭 **判準本身就夠 Jev 讀出沒有詞彙標記的那一類**：S2 那 15 段，掃描器結構上不可能抓到（0/15），J1 全部抓到。這支持維護者對 Jev 應用的那個判斷：**檢查一段文字符不符合一條「被定義好的」寫作要素，是 Jev 的主場**——預測它會不會紅不是，但這個是。

💭 **只給判準時，它把「任何解釋」都當嫌疑**。「刪掉這句，讀者還能做出同樣的決定嗎」這一句，對正當的理由也常常成立——讀者就算不知道「為什麼要先關自動續約」也能照做。J1 在 20 段正當解釋裡誤報 9 段。**這不是 Jev 的問題，是判準只寫了一半**：babel-antiai 的人工判準其實還附帶了「哪些解釋是正當的」這份清單，人讀的時候會自動套用，Jev 不會。

💭 **把例外寫出來，誤報幾乎歸零，但會把一類真的自證也當成例外**。「對不熟背景的讀者補上前提」跟「對已經懂的人解釋他懂的事」在文字上長得一模一樣，差別只在**讀者是誰**。那三段開頭都寫明了讀者（「給後端組的各位資深工程師」），所以資訊其實在 state 裡——但 Jev 沒有把「讀者是誰」跟例外條款連起來。這是跟 jev-mcp、HA-Jev 同一個方向的結論再往前一步：**一句定義能大幅改善結果，但定義裡的例外要寫到它能跟文字裡的線索對上**（例如「如果段落明說了讀者是這個領域的專業人士，對他解釋基本常識不算例外」），光說類別名稱不夠。

**分工**：掃描器零成本、確定，適合當第一道；Jev 補它結構上抓不到的那一類，並把它的誤報分開。兩者不是二選一。

## 限制

1. **題目是我們照判準字面自己編的，而判準作者覆核後推翻了 S2 全部 15 個標籤**（見上方更正）。這是這組最大的限制：編出來的題目不代表真實的 AI 味。
2. **J2 的例外清單跟 S3/S4 的反例來自同一份清單**（babel-antiai 自己記錄的正當情況），所以 J2 在反例上的表現是「定義剛好對上題目」的上限，不代表在別的正當解釋上也能這麼乾淨。
3. **60 段、每層 10 到 15 段**，信賴區間很寬（見上）。這組能說的是方向與量級，不是精確的比率。
4. **掃描器在 S1 的 6/15 取決於我們的措辭**：我們刻意用了不同說法，沒有照它的規則調題目；有些說法它的規則沒涵蓋。這個數字描述的是「這批自然寫法」，不是掃描器的一般召回率。
5. **段落是人工寫的短段**，每段只有一個關鍵句。真實文章裡自證句會跟其他內容混在一起，也可能一段有好幾句。
6. **問法是中文**。官方說 Jev 的中日韓準確率較低 📖，這組沒有測英文問法會不會更好。
7. **一次失敗的第一輪**：第一次執行時，`run.py` 讀答案時用了 Noul 回答物件不存在的屬性，360 次呼叫全部在讀取時失敗、沒有任何資料。修正後重跑的就是上面的結果；`run.py` 現在會讓暖機走同一個函式，失敗就在整批開始前中止。

## 關於 babel-antiai

babel-antiai 是本 repo 維護者的私有 skill，一組反 AI 味的掃描與改寫工具。**它的程式碼沒有公開**；經作者同意，這組公開了它的名字、SELF-JUSTIFY 那一句判準、五種形狀的名稱，以及掃描器在這 60 段上的逐段結果。沒有這支掃描器的人無法重跑掃描器那一臂，但 `runs/2026-09-23-scanner.json` 裡的逐段結果與腳本 sha256（`1da87637…`）足以核對上面的數字。Jev 的兩臂任何人都能重跑。

## 怎麼跑

```bash
python run.py --dry-run     # 印出題目與前幾段，不打 API
python run.py               # 需要 TYPESAFE_API_KEY
BABEL_ANTIAI_SCAN=<path> python baseline_scan.py   # 需要 babel-antiai 的掃描器
python score.py             # 從收據算分；--check 重算並比對
```

## 標籤

🔬（我們自己跑的；收據在 `runs/`）

---

# Catching self-justifying explanations: where regexes can't, can Jev? (English)

> **⚠ Correction (2026-09-23, the day it was published)**: this suite's main conclusion is withdrawn. On reviewing the labels, the criterion's author (babel-antiai's author) judged **all 15 S2 paragraphs to be legitimate explanations** ("the explanation that should be there, should be there"), and leaned toward the S4 labels as well (unsure about S4-07). What we reported as "15 paragraphs with no lexical marker: scanner 0, Jev 15" was in fact **Jev flagging 15 legitimate explanations as self-justifying**. The deeper problem: **we wrote the items ourselves from the literal wording of the criterion, and they don't look like real AI-flavoured writing**. The author points to a different, common case — the **process** of deliberating with an LLM and changing one's mind gets woven into the final article, when the reader doesn't need it. That can't be invented from scratch. The original labels stay in `data/cases.json`, the author's in `data/labels-author-review.json`, and `score.py` scores both. The "Results" section below keeps the original-label figures for comparison; the conclusions are those under "The corrected reading."

## What this tests

One kind of "AI flavour" isn't about wording but about **function**: a sentence that defends the author or shows they thought hard, instead of helping the reader decide. [babel-antiai](#about-babel-antiai) (a private skill belonging to this repo's maintainer) calls it SELF-JUSTIFY, with a one-sentence test:

> **Delete the sentence — can the reader still make the same decision? If so, delete it.** (「刪掉這句，讀者還能做出同樣的決定嗎？能，就刪。」)

babel-antiai's deterministic scanner catches only the five shapes that leave a grammatical trace — reason announcements, dash self-narration, pre-emptive defence, lists of hours worked, and self-flattering comparatives. Its own documentation records the limit: of 11 instances a person marked in one letter, the scanner found 4; the other 7 (self-promotion wrapped in information, explaining to experts what they already know, lecturing people who didn't ask) have no lexical marker. It also records the opposite problem: methodological reasons, background for unfamiliar readers, and necessary disclaimers trip the shapes while being entirely legitimate.

So the question: **where a regex can't see, can Jev read it from that one-sentence test? Where a regex false-alarms, can Jev tell the difference?** On the core axis it's a candidate — everything the judgment needs is in the text.

## Method

**Data**: 60 Traditional-Chinese paragraphs, all written and labelled by this repo's maintainer for this suite (paragraph-level: does it contain at least one self-justifying sentence). Five strata:

| Stratum | Content | n | Label |
|---|---|---|---|
| S1 | self-justifying, with one of the five shapes (3 each, deliberately phrased in varied ways) | 15 | yes |
| S2 | self-justifying, no lexical marker (self-promotion, explaining to experts, lecturing; 5 each) | 15 | yes |
| S3 | legitimate explanation using one of the five shapes (2 each) | 10 | no |
| S4 | legitimate explanation with no shape (reasons for a procedure, background for newcomers, necessary warnings) | 10 | no |
| S5 | plain paragraph with no explanatory function | 10 | no |

**Three arms**:

- **Scanner**: babel-antiai's `ai-quality-scan.sh` v1.3 (`--lang zh`); any SELF-JUSTIFY hit counts as "yes." Run locally; the receipt stores only per-case verdicts and the script's sha256, not the code.
- **J1, criterion only**: one Noul using the test verbatim (plus the definition "the sentence defends the author and shows they thought it through, rather than helping the reader decide").
- **J2, criterion plus exceptions**: J1 plus one sentence naming three legitimate kinds of explanation — reasons the reader needs to handle exceptions, background for readers new to the context, and necessary safety, legal or health warnings. These come from babel-antiai's own list of legitimate cases.

Three repeats per case per Jev arm, averaged, threshold 0.5 (0.3 and 0.7 also reported). The two Jev arms are separate requests. Wording is fixed in `run.py`; parameters are pinned in `protocol.yaml`.

**Frozen before running**: the 60 paragraphs and labels were pushed to GitHub in commit `6a1f110` before any scanner pass or API call. Any later label change will be recorded in this README with before/after scores.

## Results

Receipts: `runs/2026-09-23.json` (360 calls, 0 failures, all answered by `jev-1.13.0`, 173,712 input tokens, about $0.007; a 352.6 ms warm-up excluded) and `runs/2026-09-23-scanner.json`; scores: `runs/2026-09-23-scores.json` (`python score.py --check` recomputes them from the receipts).

**Paragraphs flagged "yes" per stratum (threshold 0.5)**:

| Arm | S1 self-justifying + shape | **S2 self-justifying, no marker** | **S3 legitimate + shape** | S4 legitimate, no shape | S5 plain | Accuracy | Precision | Recall |
|---|---|---|---|---|---|---|---|---|
| Scanner | 6/15 | **0/15** | **7/10** | 0/10 | 0/10 | 0.483 | 0.462 | 0.20 |
| J1 criterion only | 15/15 | **15/15** | 4/10 | 5/10 | 0/10 | 0.850 | 0.769 | 1.00 |
| J2 criterion + exceptions | 15/15 | 12/15 | **0/10** | 1/10 | 0/10 | 0.933 | 0.964 | 0.90 |

(S1–S2: how many were caught, higher is better. S3–S5: false alarms, lower is better.)

- **Ranking** (AUC, the chance a random "yes" paragraph scores above a random "no"): J1 0.981, J2 0.974. Same side of the threshold on all three repeats: J1 98.3%, J2 100%. Median latency about 227 ms.
- **Against the scanner, case by case** (2,000 paired bootstrap resamples): J2 overall +0.45, 95% CI [+0.32, +0.58], 28 won and 1 lost; J1 overall +0.37 [+0.18, +0.53], 28 won and 6 lost.
- **What the exception sentence does** (J2 vs J1): false alarms on S3 fall from 4 to 0 (+0.4, CI [+0.1, +0.7]), but S2 recall falls from 15 to 12 (−0.2, CI [−0.4, 0.0]).

**Effect of the threshold**:

| Threshold | J1: S2 caught / S3+S4 false alarms | J2: S2 caught / S3+S4 false alarms |
|---|---|---|
| 0.3 | 15/15 / 16/20 | 15/15 / 14/20 |
| 0.5 | 15/15 / 9/20 | 12/15 / 1/20 |
| 0.7 | 8/15 / 0/20 | 5/15 / 0/20 |

**All three paragraphs J2 missed are "explaining to experts what they know"** (S2-06, S2-08, S2-10: explaining to senior engineers why writes pause during an upgrade, to accountants why debits must equal credits, to chefs why raw and cooked food need separate boards). Mean scores 0.41, 0.38 and 0.32; J1 gave the same three 0.72, 0.63 and 0.64. **J2's only false alarm was S4-08** (a fire-safety warning for a heater, 0.51, just over the line).

## The corrected reading

Rescored with the criterion author's labels (all of S2 legitimate; only the 15 S1 paragraphs count as self-justifying):

| | Accuracy | Precision | Recall | False alarms (of 45 legitimate) | AUC |
|---|---|---|---|---|---|
| Scanner | **0.733** | 0.462 | 0.40 | 7 | — |
| Jev, criterion only | 0.600 | 0.385 | 1.00 | **24** | 0.950 |
| Jev, criterion + exceptions | 0.783 | 0.536 | 1.00 | 13 | 0.955 |

💭 **Only three things survive, all smaller than the original claim**:

1. **Given the one-sentence test alone, Jev's judgment does not match the test's own author**, and it leans toward "every explanation is suspect": 24 of 45 legitimate explanations flagged, lower accuracy than the zero-cost scanner. Read literally, "delete it — can the reader still decide the same way?" holds for most explanations; the author applies it with a body of unwritten judgment Jev never receives.
2. **The ranking is right; the threshold is not**: real self-justification (S1) averages 0.86–0.89, the wrongly flagged legitimate explanations (S2) 0.64–0.71. AUC 0.95, but the threshold would have to be much higher and calibrated on real writing, which these 60 paragraphs are not.
3. **The scanner's side stands**: not firing on S2 was correct all along; 7/10 false alarms on S3 and 6/15 on S1 still hold.

**This suite does not answer its original question** — whether Jev can catch the self-justification a regex can't — because what we wrote as "the kind a regex can't catch" wasn't self-justification. Answering it needs real writing: drafts an author organised after discussing them with an LLM, with the author marking the passages that are leftover process the reader doesn't need. That's the next round.

## The reading under the original labels (superseded above, kept for comparison)

💭 **The criterion alone is enough for Jev to read the kind that has no lexical marker**: the scanner structurally cannot catch the 15 S2 paragraphs (0/15); J1 caught all of them. This supports the maintainer's view on applying Jev: **checking whether a piece of writing meets a *defined* writing criterion is Jev's territory** — predicting whether it will go viral is not, but this is.

💭 **Given only the criterion, it treats every explanation as suspect.** "Delete it — can the reader still decide the same way?" is often true of legitimate reasons too: a reader can follow "turn off auto-renew first" without knowing why. J1 flagged 9 of 20 legitimate explanations. **That isn't Jev's fault; the criterion was only half written down**: babel-antiai's human test comes with a list of which explanations are legitimate, which a person applies automatically and Jev does not.

💭 **Writing the exceptions out almost removes the false alarms, but it also excuses one kind of real self-justification.** "Background for a reader new to the context" and "explaining to experts what they know" look identical on the page; the difference is **who the reader is**. All three missed paragraphs name their reader in the first line ("to the senior engineers on the backend team"), so the information was in the state — but Jev didn't connect "who the reader is" to the exception. This takes the jev-mcp and HA-Jev finding one step further: **a sentence of definition helps a great deal, but the exceptions in it have to be written so they meet the cues in the text** (for instance, "if the paragraph says the readers are professionals in this field, explaining basics to them is not an exception") — naming the category is not enough.

**Division of labour**: the scanner is free and deterministic, a good first pass; Jev covers the kind it structurally can't see and separates out its false alarms. It isn't either/or.

## Limitations

1. **We wrote the items ourselves from the literal wording of the criterion, and its author overturned all 15 S2 labels on review** (see the correction above). This is the suite's largest limitation: invented items don't represent real AI-flavoured writing.
2. **J2's exception list and the S3/S4 negatives come from the same list** (babel-antiai's own legitimate cases), so J2's performance on the negatives is a ceiling where the definition happens to match the test, not evidence it will be as clean on other legitimate explanations.
3. **60 paragraphs, 10 to 15 per stratum**; the confidence intervals are wide. This establishes direction and magnitude, not precise rates.
4. **The scanner's 6/15 on S1 depends on our wording**: we deliberately varied the phrasing and did not tune items to its rules; some phrasings aren't covered. The figure describes this set of natural phrasings, not the scanner's general recall.
5. **Short hand-written paragraphs** with one key sentence each. In real writing a self-justifying sentence sits among other content, and a paragraph may have several.
6. **The question is in Chinese.** TypeSafe says Jev is weaker in CJK 📖; we didn't test whether an English question would do better.
7. **A failed first run**: on the first attempt `run.py` read an attribute the Noul answer object doesn't have, so all 360 calls failed while reading the answer and produced no data. The results above are from the corrected re-run; `run.py` now sends its warm-up through the same function and aborts before the batch if it fails.

## About babel-antiai

babel-antiai is a private skill belonging to this repo's maintainer: a set of tools for scanning and rewriting AI-sounding text. **Its code is not public**; with its author's consent this suite publishes its name, the SELF-JUSTIFY test sentence, the names of the five shapes, and the scanner's per-case verdicts on these 60 paragraphs. Without the scanner, its arm can't be re-run, but the per-case verdicts and the script's sha256 (`1da87637…`) in `runs/2026-09-23-scanner.json` are enough to check the numbers above. Anyone can re-run the two Jev arms.

## How to run

```bash
python run.py --dry-run     # print the questions and sample paragraphs, no API calls
python run.py               # needs TYPESAFE_API_KEY
BABEL_ANTIAI_SCAN=<path> python baseline_scan.py   # needs babel-antiai's scanner
python score.py             # score from the receipts; --check recomputes and compares
```

## Tag

🔬 (run by us; receipts in `runs/`)
