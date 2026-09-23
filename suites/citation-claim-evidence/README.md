🇹🇼 中文｜🇬🇧 English below

# 引用查核帳逐條核:主張對證據引句

## 這組測什麼

一篇論文的引用查核帳(ledger)裡,每一筆都是「論文的一句主張＋從被引文獻抄下的證據引句＋判定」。判定(ok 或 misread 誤讀)是查核流程**對照被引文獻全文**做出的。這組問:**只給 Jev 那句主張和記錄下來的引句,它抓不抓得到誤讀?**

來源是維護者自己的論文 `philosophy-of-interaction-reversibility-2026`(前一版已公開於 Zenodo,DOI 10.5281/zenodo.21225988)的查核帳。已判定的 72 筆裡,66 筆 ok、3 筆誤讀,另 3 筆排除(判定帶保留、或資料錯置,理由記在 `data/cases.json`)。3 筆誤讀是同一型——**主張比證據多了一塊**:

- 把 Svanæs 的「傢俱設計」對照講成 Kasap 的(引句寫的是平面設計)
- 替 Leonardi 加引號寫成「human agency loop」(他只說 agency loops)
- 掛在同一個引用下的第三個理由「制度文化」,原文沒有

## 方法論

- **A 臂**:逐字照抄 paper-source-audit 的 `audit-jev.py`——每段引句一次請求、一題 Choice(支持／矛盾／沒提到);該工具自己的規則:不是「支持」或信心低於 0.8 就送人審。
- **B 臂**:一次請求給整句主張、全部引句,以及**引用編號**,三題 Noul,都限定「只判這個引用負責的那部分」(一句主張常掛好幾個引用,不限定會把別人負責的內容也算成沒被蓋到)。**事先定的主判斷**:「那部分有沒有引句沒提到的具體細節——人名、加引號的詞、例子、列舉的理由、對照」,門檻 0.5。另報「引句是否支持每一個部分」與「是否說得更廣或更強」。
- 各問三次取平均。題目與規則在執行前以 commit `2598be4` 凍結推上。

## 結果

收據:`runs/2026-09-23.json`(462 次呼叫、0 失敗,`jev-1.13.0`,259,713 input tokens);評分:`runs/2026-09-23-scores.json`(`score.py --check` 可重算)。

| | 66 筆 ok 被標 | 3 筆誤讀被標 | 誤讀在 69 筆裡的排名(1=最可疑)| 誤讀 vs ok(AUC)|
|---|---|---|---|---|
| A:現有 audit-jev(送人審) | 34 | 3 | 21、28、44 | 0.56 |
| **B 主判斷:有引句沒提到的細節** | **57** | 3 | 3、8、42 | 0.77 |
| B:引句不支持每一部分 | 47 | 3 | 10、11、26 | 0.79 |
| B:說得更廣或更強 | 59 | 3 | 1、9、57 | 0.69 |

**當誤讀偵測器,兩個臂都不及格**:3 筆全抓到,是因為它幾乎什麼都標——主判斷在 66 筆 ok 裡標了 57 筆。現有工具的排序能力 0.56,接近丟銅板。

**但 Jev 不是在亂標。**逐筆看分數最高的 ok:

- Ellul:主張寫「從本體論追問技術的本質、Gestell、先驗而非經驗」,記錄的證據是「the autonomous technique…The Totalitarian State(章名)」——一個指向,沒有內容。
- Diebel:證據只蓋到「公平感下降侵蝕信任」,主張前半「完全交給 AI 的決定被認為程序上較不公平」沒被蓋到。

分數最低的 ok 則是引句幾乎逐字對上主張的(例如 Mitchell 那筆)。**Jev 排的是「記錄下來的證據蓋住主張的程度」,而且排得準。**

## 這代表什麼

💭 **又是核心那條軸,這次在標籤那一側。**ok 的判定是查核者讀了被引文獻全文做的;記進帳本的引句只是指向,不是完整證據。所以對 Jev 來說,「引句沒蓋到的 ok」和「引句沒蓋到的誤讀」長得一模一樣——差別在原文裡,不在 state 裡。誤讀要抓,得把被引段落的全文放進去,不是一段引句。

💭 **但它量到的東西本身有用:帳本的證據留得太薄。**66 筆 ok 裡有 57 筆,記錄下來的引句蓋不住主張的某個細節。如果這本帳的用途包括「日後別人能重新核對」,這是真的缺口——現在只能相信查核者當時讀過。用法很直接:結案前問一次「這筆的引句有沒有蓋住主張的每個細節」,排在前面的補引句。這是**證據覆蓋檢查**,不是誤讀偵測。

**對現有工具的建議**:`audit-jev.py` 照現在的設計,在這本帳上排序能力 0.56,不建議常態接進查核流程。

## 限制

1. 誤讀只有 3 筆,AUC 與排名只能看方向。
2. 標籤是查核流程的判定,本身也可能有錯;這組沒有重新核對 66 筆 ok。
3. 「Jev 在排證據覆蓋程度」這個讀法,是看分數最高與最低各三、四筆得出的,沒有對全部 66 筆逐筆標註覆蓋程度。
4. 單一論文、單一領域(哲學型 HCI)。
5. 主張句摘自維護者自己的稿件,經同意公開;引句是被引文獻的短引,其中 8 段是 OpenAlex 取得的完整摘要。兩者都不適用本 repo 的 MIT 授權。

## 標籤

🔬(我們自己跑的;收據在 `runs/`)

---

# Checking a citation-audit ledger claim by claim (English)

## What this tests

Each row of a paper's citation-audit ledger is a claim sentence from the paper, an evidence quote copied from the cited work, and a verdict (ok, or misread) made by the audit process **against the cited work's full text**. The question: **given only the claim and the recorded quote, can Jev catch the misreads?**

The ledger belongs to the maintainer's paper `philosophy-of-interaction-reversibility-2026` (an earlier version is public on Zenodo, DOI 10.5281/zenodo.21225988). Of 72 judged rows, 66 are ok and 3 misread, with 3 excluded (qualified verdicts or a data misplacement; reasons in `data/cases.json`). All three misreads have the same shape — **the claim carries more than its evidence**: Svanæs's furniture-design contrast attributed to Kasap (the quote says graphic design); "human agency loop" put in quotation marks for Leonardi (he says agency loops); and a third reason, "institutional culture," hung on a citation whose source lacks it.

## Method

- **Arm A**: paper-source-audit's `audit-jev.py` verbatim — one request per quote, one Choice (supports / contradicts / says nothing); the tool's own rule sends anything not "supports" or below 0.8 confidence to human review.
- **Arm B**: one request with the whole claim, all quotes, and **the citation number**, three Nouls each scoped to "only the part attributed to this citation" (a claim sentence often cites several sources; unscoped, parts that belong to other citations would count as uncovered). **Pre-registered primary**: "does that part contain a specific detail — a name, a term in quotation marks, an example, a listed reason, or a comparison — that none of the quotes mention?", threshold 0.5. Also reported: "do the quotes support every element" and "is the source's point stated more broadly or strongly".
- Three repeats, averaged. Cases and rules were frozen and pushed in commit `2598be4` before running.

## Results

Receipts: `runs/2026-09-23.json` (462 calls, 0 failures, `jev-1.13.0`, 259,713 input tokens); scores: `runs/2026-09-23-scores.json` (`score.py --check` recomputes).

| | ok flagged (of 66) | misreads flagged (of 3) | misread ranks among 69 (1 = most suspicious) | misread vs ok (AUC) |
|---|---|---|---|---|
| A: current audit-jev (sent to review) | 34 | 3 | 21, 28, 44 | 0.56 |
| **B primary: detail not in the quotes** | **57** | 3 | 3, 8, 42 | 0.77 |
| B: quotes don't support every element | 47 | 3 | 10, 11, 26 | 0.79 |
| B: stated more broadly or strongly | 59 | 3 | 1, 9, 57 | 0.69 |

**As a misread detector, both arms fail**: all three are caught because nearly everything is flagged — the primary flags 57 of 66 ok rows. The current tool's AUC of 0.56 is close to a coin flip.

**But Jev isn't flagging at random.** The top-scoring ok rows: Ellul — the claim says "asks after the essence of technology from an ontological vantage, Gestell, transcendental rather than empirical", the recorded evidence is "the autonomous technique…The Totalitarian State (chapter title)", a pointer with no content; Diebel — the quote covers "reduced fairness undermines trust" but not the first half, "a decision fully delegated to AI is perceived as procedurally less fair". The lowest-scoring ok rows are ones whose quote matches the claim almost word for word (Mitchell, for instance). **Jev is ranking how well the recorded evidence covers the claim, and ranking it accurately.**

## What it means

💭 **The core axis again, this time on the label side.** The ok verdicts were made by an auditor who read the cited full text; the quote in the ledger is a pointer, not the whole evidence. To Jev, "an ok row whose quote doesn't cover it" and "a misread whose quote doesn't cover it" look identical — the difference is in the source, not in the state. Catching misreads needs the cited passage's full text in the state, not one quote.

💭 **What it does measure is useful: the ledger's evidence is thin.** For 57 of 66 ok rows the recorded quote doesn't cover some detail of the claim. If the ledger is meant to let someone re-verify later, that's a real gap — today you have to trust that the auditor read it. The use is direct: before closing a row, ask whether its quote covers every detail of the claim, and top up the rows that rank highest. That's **an evidence-coverage check**, not a misread detector.

**On the current tool**: as designed, `audit-jev.py` has an AUC of 0.56 on this ledger; we don't recommend wiring it into the audit routine.

## Limitations

1. Three misreads: AUC and ranks give direction only.
2. The labels are the audit process's verdicts and may themselves be wrong; this suite didn't re-check the 66 ok rows.
3. "Jev is ranking evidence coverage" rests on reading the top and bottom three or four rows, not on labelling coverage for all 66.
4. One paper, one field (philosophical HCI).
5. Claim sentences are excerpts of the maintainer's manuscript, published with permission; quotes are short excerpts of cited works, eight of them full abstracts retrieved from OpenAlex. Neither is under this repo's MIT license.

## Tag

🔬 (run by us; receipts in `runs/`)
