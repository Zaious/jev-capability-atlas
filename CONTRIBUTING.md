🇹🇼 中文｜🇬🇧 English below

# 貢獻規則

## 收據優先——這是唯一不能商量的規則

每一個數字都要能回頭查到出處：我們自己跑的（🔬）附 `runs/` 裡真實 API 回應的原始 log（JSON，含 `usage`）；別人發表的（📚）附一手來源連結；TypeSafe 官方文件（📖）附頁面連結。手打的數字、憑印象寫的信心值、沒跑過就先寫結論——一律不收。這條規則的理由：這整個專案存在的意義就是「用收據取代印象」，破例一次，後面所有數字都失去意義。

## 收錄準則

### 四種來源標記

每一條實質主張都標上其中一種。一段話裡混了不同來源，就分開標，不要用一個標記蓋過全部。

| 標記 | 意思 | 收據是什麼 |
|---|---|---|
| 🔬 我們自己測的 | 用真的 API key 打出去的呼叫，報的是真的回傳值，不是估的 | `runs/` 裡的原始回應 |
| 📚 第三方來源 | 別人發表的跑分、文章、貼文、repo 自述或實驗（不是 TypeSafe，也不是我們）。我們讀過並轉述，沒有自己重跑 | 可查證的一手來源連結 |
| 📖 TypeSafe 官方文件 | 廠商自己講的設計、訓練法、規格與使用指引。我們確認過頁面存在、引文一致，但沒有獨立驗證底層的技術主張（例如模型架構或參數量，超出官方揭露的部分我們無法確認）| [docs.typesafe.ai](https://docs.typesafe.ai) 的頁面連結 |
| 💭 我們自己的判斷 | 把上面幾種組合起來推出的框架或推論，本身沒有獨立驗證 | 寫明是根據哪些條目推出來的 |

### 收什麼、不收什麼

- **收**：附收據或一手來源、結果可以回頭查證的東西；誠實回報的失敗；推翻我們自己結論的證據。**對 Jev 不利的結果跟有利的一樣收**，收不收只看證據，不看結論。
- **不收**：只有宣稱、沒有證據或結果的東西（純構想、上架公告、安裝教學——那類交給 [awesome-jev](https://github.com/yibie/awesome-jev) 這種清單）；找不到一手來源的轉述。查不到就寫「無法查證」，或乾脆不收。

### 新東西進來，放哪裡

| 你手上的東西 | 放哪裡 | 通常的標記 |
|---|---|---|
| 我們自己對 Jev 跑的實驗 | `suites/<slug>/`（①）| 🔬 |
| 別人發表、有可驗證結果的 Jev 應用、跑分、文章、貼文 | `translations/<slug>/`（②）；`capability-map` 的彙整由維護者加 | 📚 |
| Jev 的替代品、復刻、相容伺服器，或在 Jev 之上擴充新操作的函式庫 | [`jev-variants.md`](jev-variants.md) 加一列（④）| 📚（我們同輸入實測過的才是 🔬）|
| 某個領域的實作做法（架構、踩過的坑、檢查清單）| 對應的實作指南（目前只有 [`browser-automation.md`](browser-automation.md)）；同一個領域累積三個以上真實實作，才開新的指南（④）| 📚＋💭 |
| 對既有條目或判準軸的評論、綜合分析 | 併進該條目；沒有單一對應條目才開 `analysis/<slug>.md`（③）| 💭 |
| 沒有結果、沒有證據，只是宣傳或構想 | 不收 | — |

### 查證外部宣稱時要問的事

這些都是整理過程中真的遇到過的問題：

1. **找得到一手來源嗎？** 數字要對得上原文，轉述要能回頭查。只有二手轉貼時，先追到原始出處。
2. **歸屬對嗎？** 轉貼常把 A 說的話掛到 B 身上，或把回覆當成主文。
3. **誰量的、怎麼量的？** 樣本數多少、標準答案是人工還是另一個模型、有沒有對照組。
4. **比較是不是同一批輸入？** 引用別人發表的數字，跟在同一批輸入上實測，要分開講。
5. **被比較的是通用還是專用模型？** 在評測資料的同一個分布上訓練過就是專用，主場贏不稀奇。
6. **校準數字是出廠的，還是事後調過溫度？** 調溫度用的資料如果跟測試資料重疊，數字會好看得不真實。
7. **宣稱者跟被宣稱的東西有沒有利害關係？** 例如創辦人推銷自己的服務。

### 授權

- 程式碼與原創文字：MIT，見 [`LICENSE`](LICENSE)。
- 摘要第三方來源的內容（`translations/`、`capability-map`、實作指南、變體清單、README 的比較段落）：用自己的話寫、附原始連結，直接引述只限標明出處的短句；完整說明見 [`NOTICE`](NOTICE)。
- 要轉載超過短句的原文（例如測試題目全文），先確認原始授權允許散布，並記進 `SOURCE.md`。
- 測試組用的資料：自己寫的可以直接放；公開資料集寫明來源、授權、有沒有把原文放進 repo；私人或受限的資料必須先去識別化，並在 README 說明怎麼處理的。

## 四種貢獻方式

### ① 新測試組（`suites/<slug>/`）

複製 [`suites/TEMPLATE/`](suites/TEMPLATE/)，照結構填：
- `README.md`——這組測什麼、為什麼、方法論、資料來源與授權、結果、限制（樣本數小、單一標註者這類要老實寫）；新測試組通常標 🔬
- `protocol.yaml`——釘住模型版本（`jev-latest` 還是特定版號）、信心閾值、樣本數、資料來源
- `data/`——題目本身（自己編的資料可以直接放；引用了受版權保護的內容，只放連結跟出處，不放全文）
- `run.py`——支援 `--dry-run` 只印出將送出的 state，收據裡逐題存下實際送出的 state
- `runs/`——真實 API 回應 log
- README 裡有彙總數字（準確率、敏感度這類）的話，附一支從收據重算的腳本，加 `--check` 在數字對不上時 exit 1（照 [`suites/icu-alarm-classification/metrics.py`](suites/icu-alarm-classification/metrics.py)）

### ② 整理並查證外部來源（`translations/<slug>/`）

目錄名稱沿用早期規劃，實際收的是別人發表的跑分、文章、貼文與 repo——**用自己的話整理並查證，不是翻譯稿，也不逐字翻譯題目**。如果你想把題目翻成中文、真的重新對 Jev 跑一次拿新資料——那是①新測試組（在 README 標明靈感來源），不是這條；這條沒有 `data/`、沒有 `runs/`，因為沒有新的 API 呼叫。

複製 [`translations/TEMPLATE/`](translations/TEMPLATE/)，填兩個檔案：
- `SOURCE.md`——原始來源在哪、誰做的、方法論摘要一句話、連結、「轉載範圍」（必填）；要搬題目全文的話，先填範本裡的授權欄位
- `report.md`——把原始來源的方法論、數字，還有「這個數字代表什麼、可信到什麼程度」講清楚，標 📚，不是 🔬——你沒有自己重跑，是把別人的收據整理成完整的論述，不是只複製一行表格數字

這裡的「收據」不是 `runs/` 的 API log，是**可驗證的出處連結**——`SOURCE.md` 的連結要能讓任何人回頭查證你整理得準不準確。

**`capability-map.md` 的彙整表由我們維護**——你負責把新找到的來源講清楚，不用自己學怎麼合併主表。

### ③ 純分析/心得

不一定要有新資料，也歡迎讀完現有內容後寫的綜合分析、批判、或指出我們判準軸的漏洞。**優先併入你分析的對象本身**：批評/延伸某個測試組，寫進 `suites/<slug>/README.md`；批評/延伸某個外部來源條目，寫進 `translations/<slug>/report.md`——都標 💭，說明是分析既有資料還是有新跑分佐證。

如果你的分析沒有單一對應的既有條目可以掛（例如直接評論核心判準軸本身、或跨多個條目的整體觀察），才新開 `analysis/<slug>.md`（單一雙語檔案：中文區塊＋`---`＋英文區塊，比照 `CONTRIBUTING.md` 自己的排版；樣板見 [`analysis/TEMPLATE.md`](analysis/TEMPLATE.md)），一樣標 💭。

### ④ 修正或補充既有頁面（變體清單、實作指南、能力地圖）

開 issue 或 PR，附一手來源連結與標記。[`jev-variants.md`](jev-variants.md) 的新項目要填齊「做法」「能不能直接換掉 Jev SDK」「跟 Jev 的比較（寫明是誰量的、是不是同一批輸入）」「標記」四欄；實作指南的新內容要指出是哪個真實實作、在哪個檔案或段落。

## PR checklist

- [ ] 每個數字都查得到出處：🔬 對應 `runs/` 裡的一筆 log；📚 對應可查證的一手來源連結；📖 對應官方頁面
- [ ] 每個 finding 標了 🔬/📚/📖/💭 之一（定義見上面的「收錄準則」）
- [ ] ①新測試組：README 寫了資料來源與授權；私人資料已去識別化；收據存了實際送出的 state
- [ ] ②外部來源：`SOURCE.md` 寫了「轉載範圍」（見 [`NOTICE`](NOTICE)）
- [ ] 如果搬了題目全文（不只是結果），確認過原始授權，寫進 `SOURCE.md`
- [ ] 強宣稱（「完全失效」「完美」）附了對照組，不是單一模型單次結果
- [ ] README（測試組）或 `report.md`（外部來源）老實列出樣本數、標註者數量等限制，不誇大
- [ ] `python scripts/zh-check/check_zh.py` 通過（PR 會自動跑；刻意保留的簡體字加進 `scripts/zh-check/allowlist.txt`）

## 共用工具

`scripts/common/jev_client.py` 提供 key 讀取跟一個自檢（零成本，故意用錯 key 打 401 確認服務活著）。各 suite 的跑分腳本 import 它，不要各自重寫存取邏輯。

`scripts/zh-check/check_zh.py` 檢查繁體中文文字裡有沒有混進簡體字（字表由 OpenCC 推導，排除台灣與香港的合法寫法），有就 exit 1，每個 PR 都會自動跑。它抓不到「寫成另一個真的字」這種錯（例如把「皇帝」寫成「皮帝」）；那一類可以跑 `scripts/zh-check/proofread_jev.py`（需要 TYPESAFE_API_KEY），它用 Jev 列出可疑的句子讓人確認，不擋 commit，門檻依據見 [`suites/zh-proofreading/`](suites/zh-proofreading/)。

---

# Contributing (English)

## Receipts first — the one non-negotiable rule

Every number must trace back to where it came from: for what we ran ourselves (🔬), the raw API response log in `runs/` (JSON, including `usage`); for what others published (📚), a primary-source link; for TypeSafe's own docs (📖), the page link. Hand-typed numbers, remembered confidence values, or conclusions written before anything was actually run — none of these are accepted. Why: this project's entire reason for existing is replacing impressions with receipts; one exception and every other number loses its meaning.

## Inclusion rules

### The four source tags

Tag every substantive claim with one of these. When a passage mixes sources, tag each part separately rather than covering it all with one tag.

| Tag | Meaning | What the receipt is |
|---|---|---|
| 🔬 Our own test | Calls we made with a real API key; the numbers are real returned values, not estimates | Raw responses in `runs/` |
| 📚 Third-party source | Benchmarks, articles, posts, repo self-reports or experiments published by others (not TypeSafe, not us). We read and relay them; we didn't re-run them | A verifiable primary-source link |
| 📖 TypeSafe's own docs | The vendor's own statements about design, training, specs and usage. We confirmed the pages exist and our quotes match, but haven't independently verified the underlying technical claims (e.g. architecture or parameter count beyond what TypeSafe discloses) | A page link on [docs.typesafe.ai](https://docs.typesafe.ai) |
| 💭 Our own judgment | A framework or inference assembled from the above, not independently verified | Which entries it's derived from |

### What we accept, and what we don't

- **Accept**: things with receipts or primary sources whose results can be checked; honestly reported failures; evidence that overturns our own conclusions. **Results unfavorable to Jev are accepted exactly like favorable ones** — inclusion depends on the evidence, not the conclusion.
- **Don't accept**: claims with no evidence or results behind them (pure ideas, launch announcements, install tutorials — those belong in lists like [awesome-jev](https://github.com/yibie/awesome-jev)); retellings whose primary source can't be found. If it can't be verified, say "unverifiable," or leave it out.

### Where new material goes

| What you have | Where it goes | Usual tag |
|---|---|---|
| An experiment we ran against Jev ourselves | `suites/<slug>/` (①) | 🔬 |
| A Jev application, benchmark, article or post published by others, with verifiable results | `translations/<slug>/` (②); maintainers add the `capability-map` rollup | 📚 |
| A Jev replacement, replica, compatible server, or a library that builds new operations on Jev | A row in [`jev-variants.en.md`](jev-variants.en.md) (④) | 📚 (🔬 only if we tested it on identical inputs) |
| How-to for a domain (architecture, pitfalls, checklists) | The matching implementation guide (currently only [`browser-automation.en.md`](browser-automation.en.md)); open a new guide only once a domain has three or more real implementations (④) | 📚 + 💭 |
| Commentary or synthesis on an existing entry or the core axis | Attach it to that entry; open `analysis/<slug>.md` only if there's no single entry to attach to (③) | 💭 |
| No results, no evidence — promotion or an idea | Not accepted | — |

### Questions to ask when verifying an external claim

Each of these came up for real while compiling this repo:

1. **Can the primary source be found?** Numbers must match the original, and paraphrases must be checkable. If all you have is a repost, trace it to the origin first.
2. **Is the attribution right?** Reposts often pin A's words on B, or treat a reply as the main post.
3. **Who measured it, and how?** Sample size, whether ground truth is human or another model, whether there's a control.
4. **Is the comparison on the same inputs?** Quoting someone's published number and measuring on the same inputs are different things; say which.
5. **Is the compared model a generalist or a specialist?** If it was trained on the same distribution as the evaluation data, it's a specialist, and winning at home is unremarkable.
6. **Are the calibration numbers as shipped, or temperature-fitted afterwards?** If the fitting data overlaps the test data, the numbers look better than they are.
7. **Does the claimant have a stake in the claim?** E.g. a founder promoting their own service.

### Licensing

- Code and original writing: MIT, see [`LICENSE`](LICENSE).
- Content summarizing third-party sources (`translations/`, `capability-map`, implementation guides, the variants page, the README's comparison sections): written in our own words with links to the originals; direct quotation limited to short, attributed phrases; full details in [`NOTICE`](NOTICE).
- To reproduce more than short phrases of an original (e.g. full test items), first confirm its license permits redistribution and record it in `SOURCE.md`.
- Data used by suites: original material can go in directly; for public datasets, state the source, the license, and whether the original text is included in the repo; private or restricted data must be de-identified first, with the README explaining how.

## Four ways to contribute

### ① A new test suite (`suites/<slug>/`)

Copy [`suites/TEMPLATE/`](suites/TEMPLATE/) and fill in:
- `README.md` — what it tests, why, methodology, data source and license, results, limitations (small N, single annotator — say so plainly); a new suite is usually 🔬
- `protocol.yaml` — pinned model version (`jev-latest` or a specific build), confidence threshold, sample size, data source
- `data/` — the test items themselves (original material is fine; for copyrighted content, link and cite instead of pasting the full text)
- `run.py` — support `--dry-run` to print the states it would send, and store each sent state in the receipt
- `runs/` — raw API response logs
- If the README reports aggregate numbers (accuracy, sensitivity and the like), add a script that recomputes them from the receipts, with `--check` exiting 1 on a mismatch (as in [`suites/icu-alarm-classification/metrics.py`](suites/icu-alarm-classification/metrics.py))

### ② Organizing and verifying an external source (`translations/<slug>/`)

The directory name is a holdover from early planning; it actually holds benchmarks, articles, posts and repos published by others — **written up and verified in our own words, not translations, and never word-for-word translations of test items**. If you want to translate the actual questions and re-run them against Jev for new data, that's ① a new test suite (note the inspiration in its README), not this one; this category has no `data/`, no `runs/`, because there's no new API call.

Copy [`translations/TEMPLATE/`](translations/TEMPLATE/) and fill two files:
- `SOURCE.md` — where the original is, who made it, a one-line methodology summary, a link, and the reproduction scope (required); if you want to bring in full test items, fill the template's license fields first
- `report.md` — a full write-up of the original's methodology, numbers, and what those numbers actually mean and how much to trust them, tagged 📚, not 🔬 — you didn't re-run it yourself, you're organizing someone else's receipts into a complete narrative, not just copying one row of a table

The "receipt" here isn't a `runs/` API log — it's a **verifiable source link**. `SOURCE.md`'s link needs to let anyone check how accurate your write-up is.

**The `capability-map.md` rollup table is maintained by us** — you're responsible for writing up the new source clearly; you don't need to learn how to merge the master table yourself.

### ③ Pure analysis or write-ups

Doesn't require new data — critiques of existing content or of our axis framework are welcome too. **Attach it to whatever it's analyzing first**: a critique/extension of a specific suite goes in `suites/<slug>/README.md`; a critique/extension of a specific external-source entry goes in `translations/<slug>/report.md` — both tagged 💭, noting whether it's analysis of existing data or backed by a new run.

Only open a new `analysis/<slug>.md` (a single bilingual file — Chinese block, `---`, English block, following `CONTRIBUTING.md`'s own layout; template at [`analysis/TEMPLATE.md`](analysis/TEMPLATE.md)) when your analysis has no single existing entry to attach to — e.g. a direct critique of the core axis itself, or an observation spanning multiple entries. Also tagged 💭.

### ④ Correcting or extending existing pages (variants page, implementation guides, capability map)

Open an issue or PR with a primary-source link and a tag. New rows in [`jev-variants.en.md`](jev-variants.en.md) need all four columns filled: "approach," "drop-in for the Jev SDK?," "compared with Jev (who measured it, and whether on the same inputs)," and "tag." New material for an implementation guide should name the real implementation it comes from and the file or section.

## PR checklist

- [ ] Every number traces to its source: 🔬 to a log in `runs/`; 📚 to a verifiable primary-source link; 📖 to an official page
- [ ] Every finding is tagged 🔬/📚/📖/💭 (definitions under "Inclusion rules" above)
- [ ] ① new suites: the README states the data source and license; private data is de-identified; receipts store each sent state
- [ ] ② external sources: `SOURCE.md` states its reproduction scope (see [`NOTICE`](NOTICE))
- [ ] If you brought in full test items (not just results), the original license was checked and is cited in `SOURCE.md`
- [ ] Strong claims ("completely fails," "perfect") have a control comparison, not a single unreplicated run
- [ ] The README (suites) or `report.md` (external sources) states sample size and annotator-count limitations honestly
- [ ] `python scripts/zh-check/check_zh.py` passes (it runs on every PR; add intentional Simplified text to `scripts/zh-check/allowlist.txt`)

## Shared tooling

`scripts/common/jev_client.py` handles key loading and a zero-cost self-check (deliberately triggers a 401 with a bad key to confirm the service is live). Suite scripts should import it rather than reimplementing access logic.

`scripts/zh-check/check_zh.py` checks that no Simplified character slipped into Traditional Chinese text (the list is derived from OpenCC, excluding forms valid in Taiwan and Hong Kong) and exits 1 if one did; it runs on every PR. It can't catch a wrong-but-real character (writing 皮帝 for 皇帝); for that kind, run `scripts/zh-check/proofread_jev.py` (needs TYPESAFE_API_KEY), which uses Jev to list suspicious sentences for a person to check without blocking the commit — threshold basis in [`suites/zh-proofreading/`](suites/zh-proofreading/).
