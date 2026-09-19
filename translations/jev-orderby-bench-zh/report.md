🇹🇼 中文｜🇬🇧 English below

# 拿 Jev 的機率做 SQL ORDER BY 排序，這個順序站不站得住腳

## 這組測什麼

三個 DuckDB 擴充套件跟一個 Postgres 擴充套件在 Jev 發布一週內就上線，全部提供 `ORDER BY jev_prob(...)` 這種寫法，但沒有一個附上「這個順序真的可信嗎」的量測。這個專案就是補那個量測：**校準**（信心值講的 0.7 是不是真的 70%）跟**排序**（照這個分數排，順序真的對嗎）是兩件會分開失敗的事——機率全部擠在 [0.48, 0.52] 但完美排序，ECE 很差但一個逆序都沒有；反過來，一個整體校準良好的模型也可能把個別配對排反，讓排序結果肉眼可見地不對。`ORDER BY` 依賴的是後者，但原始規格的判準只寫了前者。

## 方法論

主測試用 **20 Newsgroups**（新聞群組文章，標籤是作者本人選的看板，人工判斷，跟這個專案完全無關，避免球員兼裁判）；360 列，跨三個探針（醫療/二手拍賣/太空），刻意用分層抽樣讓標籤涵蓋整個機率範圍，不是只挑明顯案例。判準門檻**跑之前就定死**：`jev_bool` ECE ≤0.10、逆序率 ≤0.15、resolution >0；`jev_score` 對三級分層目標的序性逆序率 ≤0.15；`jev_choice` 信心 ECE ≤0.10；否定不對稱性 ≤0.15。另外三個**不需要標註答案**的不變性檢驗：否定對稱（`P(問句)` 跟 `1-P(問句的否定)` 該相等）、改述控制（語意相同、換句話說，答案該一致）、量表鏡像（把評分量表反過來，分數該對應鏡像）。

跑完主測試後，另外用 **Amazon ESCI**（真人標註的商品搜尋相關性資料集，四級評分 Exact>Substitute>Complement>Irrelevant）做「困難探針」——30 個特意挑出來的難查詢、306 筆商品，測同一套判準在真實、分級、非二元的相關性任務上還撐不撐得住。

## 結果

**主測試（20 Newsgroups，360 列）：六項判準全過。** `jev_bool` ECE 0.045、逆序率 0.036；`jev_score` 序性逆序率 0.143（比 0.15 門檻低一點，是最勉強過關的一項）；否定不對稱性 0.016，但改述控制也量到 0.016——兩者幾乎一樣，代表這個「否定對稱性好」的結果其實只是「這個模型對措辭本來就不太敏感」，不是真的對否定有特別處理。

**批次大小效應（同一批 360 列，換不同的請求方式量）：把 40 列塞進同一個 state 一次問，直接讓排序判準不過關**（逆序率從 0.038 惡化到 0.171，Spearman 從 0.932 掉到 0.579）。不是文字寫法的問題（用同樣的文字、批次改成 1 列一次，判準又過了），是一個位置效應：批次裡越後面的列，分數被拉得越靠近 0.5——第 0-7 格平均只偏移 0.049，第 24-39 格偏移到約 0.42。分批處理能省一半的 token 費用，但代價是排序品質。

**困難探針（Amazon ESCI，306 列）：六項判準裡四項不過。** `jev_bool` ECE 從 0.045 惡化到 0.242；序性逆序率從 0.143 惡化到 0.254（分層內平均 0.244，30 個查詢裡有 23 個超過門檻）；信心 ECE 從 0.077 惡化到 0.279。四級分類（`jev_choice`）168/306 筆全部被判成同一個等級（Substitute），其中真正該是 Exact 的有 63 筆；信心 1.0 的判斷裡有 47% 是錯的。改述控制在這個困難任務上量到 0.164（新聞群組測試只有 0.016），代表換句話說對答案的影響幾乎跟真正的語意差異一樣大。否定對稱性本身仍然過關（0.023）——但正因為改述控制惡化了，這個「過關」不能再解讀成「模型真的不受措辭影響」。

## 這個數字代表什麼、可信到什麼程度

**簡單任務的好結果是能力的上限，不是下限**——這句話是原作者自己講的，我們完全同意：新聞群組主題分類，本質上答案幾乎就寫在文字裡；商品搜尋相關性要比對「這個商品符合查詢的哪個面向、符合到什麼程度」，需要比對的東西不只在給定文字內，這正好落在本 repo 核心那條軸的「不自足」那一側，跟這裡量出來的失敗完全吻合。

**批次大小這個發現，直接跟我們已經記錄的另一條證據對上**：`translations/jev-context-compaction-debate-zh/` 裡也發現過批次/state 內容看不看得到會直接影響 Jev 的判斷品質；這裡量出的是同一種現象的另一個面向——不是「看不到內容」，是「同一個 state 裡塞太多列，越後面的列判斷品質越差」。兩條證據合起來說明：**Jev 的品質不只取決於問題設計，也取決於一次請求裡放了什麼、放了多少**，這是一個工程細節，卻能讓校準數字整個垮掉，而且垮的方式很安靜——排序不會報錯，只是排得不對。

**信心值系統性偏低（underconfident）這件事，方向是好的，但門檻要照這張表校準，不能憑直覺**：新聞群組測試裡，模型講 0.855 時，真實比率其實是 0.914——用直覺設一個「信心 >0.9 就自動執行」的門檻，會比你以為的更嚴格。到了 ESCI 困難探針，這個系統性偏低的方向沒變，但因為模型本身已經分不太出類別（resolution 只剩 0.043，AUC 0.745），偏低就不再是無傷大雅的方向，變成一個嚴重訊號。

**兩位小數的機率輸出，本身就是排序系統的一個結構性限制，跟任務難度無關**：360 列只產生 45 個不同的機率值，53 列並列在 0.99——`ORDER BY prob DESC LIMIT 20` 在這種情況下回傳的 20 筆，只是資料庫引擎剛好把 53 筆並列資料排出來的其中一組，換一次查詢引擎版本結果可能就不一樣。這件事任何拿 Jev 機率做排序的人都會踩到，不是只有困難任務才有。

## 標籤

📚（第三方獨立跑分，方法論、原始碼、逐項數字全公開；我們沒有自己重跑，但通篇核對過每個數字對應的判準跟原始碼邏輯）

---

# Does sorting by a Jev probability via SQL ORDER BY hold up? (English)

## What this covers

Three DuckDB extensions and one Postgres extension shipped within a week of Jev's launch, all offering `ORDER BY jev_prob(...)`, none shipping a measurement of whether that order is actually defensible. This project is that measurement: **calibration** (does a stated 0.7 really mean 70%) and **ranking** (does sorting by this score put rows in the right order) fail independently — probabilities squashed into [0.48, 0.52] but perfectly ordered give terrible ECE with zero inversions; conversely, a model calibrated in aggregate can still invert many individual pairs and produce a visibly wrong page of results. `ORDER BY` depends on the latter, but the original spec's gate only named the former.

## Methodology

The main test uses **20 Newsgroups** (newsgroup posts, labeled by which board the author themselves chose to post to — a human judgment, entirely independent of this project, avoiding self-grading); 360 rows across three probes (medical/for-sale/space), deliberately stratified to span the whole probability range rather than sampling only obvious cases. Gate thresholds were **fixed before any results were seen**: `jev_bool` ECE ≤0.10, inversion rate ≤0.15, resolution >0; `jev_score` ordinal inversion against a 3-level stratified target ≤0.15; `jev_choice` confidence ECE ≤0.10; negation asymmetry ≤0.15. Three additional invariant checks need **no ground-truth labels at all**: negation symmetry (`P(question)` should equal `1 - P(negated question)`), a paraphrase control (a semantically equivalent reworded question should get the same answer), and rubric mirroring (reversing the scoring rubric should mirror the score).

After the main test, a **hard probe** using **Amazon ESCI** (human-labeled product-search relevance, a four-level grade: Exact>Substitute>Complement>Irrelevant) tests whether the same gate holds up on a real, graded, non-binary relevance task — 30 deliberately hard queries, 306 products.

## Results

**Main test (20 Newsgroups, 360 rows): all six gate conditions pass.** `jev_bool` ECE 0.045, inversion rate 0.036; `jev_score` ordinal inversion 0.143 (just under the 0.15 threshold — the weakest link); negation asymmetry 0.016, but the paraphrase control also measured 0.016 — nearly identical, meaning the "good negation symmetry" result is really just "this model isn't very sensitive to wording in general," not genuine negation handling.

**Batch-size effect (same 360 rows, measured across different request shapes): packing 40 rows into one state in a single call breaks the ranking gate outright** (inversion rate worsens from 0.038 to 0.171, Spearman drops from 0.932 to 0.579). It isn't about wording (the same text, sent one row at a time, passes again) — it's a position effect: rows later in the batch get pulled closer to 0.5, the more so the later they sit — slots 0-7 shift by 0.049 on average, slots 24-39 by about 0.42. Batching halves the token bill and pays for it in ranking quality.

**Hard probe (Amazon ESCI, 306 rows): four of six gate conditions fail.** `jev_bool` ECE worsens from 0.045 to 0.242; ordinal inversion worsens from 0.143 to 0.254 (0.244 averaged within each query, 23 of 30 queries over threshold); confidence ECE worsens from 0.077 to 0.279. The four-way choice collapses: 168 of 306 rows are predicted the same grade (Substitute), 63 of which are actually Exact; among picks made at 1.0 confidence, 47% are wrong. The paraphrase control measures 0.164 on this hard task (versus 0.016 on newsgroups) — rewording moves the answer almost as much as real semantic difference does. Negation symmetry itself still passes (0.023) — but because the paraphrase control worsened, that "pass" can no longer be read as "the model is genuinely insensitive to wording."

## What this means, and how much to trust it

**A good result on an easy task is an upper bound, not a floor** — the original author says this directly, and we fully agree: newsgroup topic classification is a task where the answer is nearly written into the text itself; product-search relevance requires comparing "how well does this product match which facet of the query, and how well" — something that isn't fully contained in the given text, landing squarely on the "not self-contained" side of this repo's core axis, exactly matching the failure measured here.

**The batch-size finding lines up directly with evidence we've already recorded**: `translations/jev-context-compaction-debate-zh/` also found that batching/state visibility directly affects Jev's judgment quality; this measures a different facet of the same phenomenon — not "can't see the content," but "too many rows packed into one state, with judgment quality degrading the further into the batch a row sits." Together, the two pieces of evidence say: **Jev's quality depends not just on question design but on what — and how much — goes into a single request**, an engineering detail that can quietly wreck calibration numbers without ever throwing an error; sorting doesn't fail loudly, it just comes out wrong.

**Systematic underconfidence is the right direction, but calibrate against this table, not intuition**: on the newsgroups test, a stated 0.855 corresponds to a true rate of 0.914 — setting an "auto-execute above 0.9 confidence" threshold by feel would be stricter than intended. On the ESCI hard probe, the same underconfident direction persists, but because the model is barely separating classes at all by that point (resolution only 0.043, AUC 0.745), underconfidence stops being a benign direction and becomes a serious signal.

**Two-decimal-place probability output is a structural limitation of any ranking built on it, independent of task difficulty**: 360 rows produced only 45 distinct probability values, with 53 rows tied at 0.99 — `ORDER BY prob DESC LIMIT 20` in that situation returns whichever 20 of those 53 tied rows the database engine happens to have left in that order, which can change with a query engine version bump. Anyone sorting by a Jev probability will hit this, not just on hard tasks.

## Tag

📚 (an independent third-party benchmark; methodology, source code, and every number are public; we did not re-run it ourselves, but read the full README and cross-checked every number against its gate and the underlying logic)
