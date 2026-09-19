🇹🇼 中文｜🇬🇧 English below

# 貢獻規則

## 收據優先——這是唯一不能商量的規則

每一筆數字都要附**真實 API 回應的原始 log**（存在 `runs/`，JSON 格式，含 `usage`）。手打的數字、憑印象寫的信心值、沒跑過就先寫結論——一律不收。這條規則的理由：這整個專案存在的意義就是「用收據取代印象」，破例一次，後面所有數字都失去意義。

## 三種貢獻方式

### ① 新測試組（`suites/<slug>/`）

複製 [`suites/TEMPLATE/`](suites/TEMPLATE/)，照結構填：
- `README.md`——這組測什麼、為什麼、用哪種標籤（🔬 自己測的最合適，新測試組本來就該是 🔬）
- `protocol.yaml`——釘住用的模型版本（`jev-latest` 還是特定版號）、信心閾值、樣本數
- `data/`——題目本身（自己編的資料可以直接放；如果引用了受版權保護的內容，只放連結跟出處，不放全文）
- `runs/`——真實 API 回應 log
- `report.md`——結果、發現、老實講清楚樣本數多小、單一標註者這類限制

### ② 翻譯與整理國外的跑分結果（`translations/<原始跑分>-<語言>/`）

**這條處理的是結果與論述的翻譯整理，不是題目逐字翻譯。** 如果你想把題目翻成中文、真的重新對 Jev 跑一次拿新資料——那是①新測試組（在 `report.md` 標明靈感來源是哪個外部跑分），不是這條；這條没有 `data/`、没有 `runs/`，因為沒有新的 API 呼叫。

複製 [`translations/TEMPLATE/`](translations/TEMPLATE/)，填兩個檔案：
- `SOURCE.md`——原始跑分在哪、誰做的、方法論摘要一句話、連結（引用別人已發表的結論、附上出處，通常不算衍生作品，不需要處理授權；但如果你想把**題目全文**搬進來就要先查授權，見 SOURCE.md 裡的欄位）
- `report.md`——用中文把原始跑分的方法論、數字，還有「這個數字代表什麼、可信到什麼程度」講清楚，標 📚，不是 🔬——你沒有自己重跑，是把別人的收據翻譯／整理成完整的中文論述，不是只複製一行表格數字

這裡的「收據」不是 `runs/` 的 API log，是**可驗證的出處連結**——`SOURCE.md` 的連結要能讓任何人回頭查證你翻譯/整理得準不準確。

目的是讓這個 repo 持續發現我們自己還沒找到的國外跑分，用完整敘述帶進來，不是只留一行表格數字。**`capability-map.md` 的彙整表由我們維護**——你負責把新找到的來源講清楚，不用自己學怎麼合併主表。

### ③ 純分析/心得

不一定要有新資料，也歡迎讀完現有內容後寫的綜合分析、批判、或指出我們判準軸的漏洞。**優先併入你分析的對象本身**：批評/延伸某個測試組，寫進 `suites/<slug>/report.md`；批評/延伸某個翻譯整理條目，寫進 `translations/<slug>/report.md`——都標 💭，說明是分析既有資料還是有新跑分佐證。

如果你的分析沒有單一對應的既有條目可以掛（例如直接評論核心判準軸本身、或跨多個條目的整體觀察），才新開 `analysis/<slug>.md`（單一雙語檔案：中文區塊＋`---`＋英文區塊，比照 `CONTRIBUTING.md` 自己的排版；樣板見 [`analysis/TEMPLATE.md`](analysis/TEMPLATE.md)），一樣標 💭。

## PR checklist

- [ ] ①新測試組:每個數字都對應 `runs/` 裡的一筆真實 log；②翻譯整理:每個數字都對應 `SOURCE.md` 裡可查證的出處連結
- [ ] 每個 finding 標了 🔬/📚/📖/💭 之一
- [ ] 如果搬了題目全文（不只是結果），確認過原始授權，寫進 `SOURCE.md`
- [ ] 強宣稱（「完全失效」「完美」）附了對照組，不是單一模型單次結果
- [ ] `report.md` 老實列出樣本數、標註者數量等限制，不誇大

## 共用工具

`scripts/common/jev_client.py` 提供 key 讀取跟一個自檢（零成本，故意用錯 key 打 401 確認服務活著）。各 suite 的跑分腳本 import 它，不要各自重寫存取邏輯。

---

# Contributing (English)

## Receipts first — the one non-negotiable rule

Every number needs a **raw API response log** attached (in `runs/`, JSON, including `usage`). Hand-typed numbers, remembered confidence values, or conclusions written before anything was actually run — none of these are accepted. Why: this project's entire reason for existing is replacing impressions with receipts; one exception and every other number loses its meaning.

## Three ways to contribute

### ① A new test suite (`suites/<slug>/`)

Copy [`suites/TEMPLATE/`](suites/TEMPLATE/) and fill in:
- `README.md` — what it tests, why, which tag (🔬 is the natural fit for a new suite you ran yourself)
- `protocol.yaml` — pinned model version (`jev-latest` or a specific build), confidence threshold, sample size
- `data/` — the test items themselves (original material is fine; for copyrighted content, link and cite instead of pasting the full text)
- `runs/` — raw API response logs
- `report.md` — findings, stated plainly with sample-size and single-annotator caveats

### ② Translating and organizing a foreign benchmark's results (`translations/<original>-<lang>/`)

**This is about translating and organizing results and their narrative — not translating the test items word-for-word.** If you want to translate the actual questions and re-run them against Jev for new data, that's ① a new test suite (note the external benchmark as inspiration in `report.md`), not this one; this category has no `data/`, no `runs/`, because there's no new API call.

Copy [`translations/TEMPLATE/`](translations/TEMPLATE/) and fill two files:
- `SOURCE.md` — where the original benchmark is, who made it, a one-line methodology summary, and a link (citing someone else's published conclusion with a source link usually isn't a derivative work and doesn't need a license check; if you want to bring in the **full test items** verbatim, check the license first — see the field for that in SOURCE.md)
- `report.md` — a full Chinese write-up of the original benchmark's methodology, numbers, and what those numbers actually mean and how much to trust them, tagged 📚, not 🔬 — you didn't re-run it yourself, you're translating/organizing someone else's receipts into a complete narrative, not just copying one row of a table

The "receipt" here isn't a `runs/` API log — it's a **verifiable source link**. `SOURCE.md`'s link needs to let anyone check how accurate your translation/organization is.

The goal is to keep surfacing foreign benchmarks we haven't found yet, brought in with a full narrative, not just one more table row. **The `capability-map.md` rollup table is maintained by us** — you're responsible for writing up the new source clearly; you don't need to learn how to merge the master table yourself.

### ③ Pure analysis or write-ups

Doesn't require new data — critiques of existing content or of our axis framework are welcome too. **Attach it to whatever it's analyzing first**: a critique/extension of a specific suite goes in `suites/<slug>/report.md`; a critique/extension of a specific translated entry goes in `translations/<slug>/report.md` — both tagged 💭, noting whether it's analysis of existing data or backed by a new run.

Only open a new `analysis/<slug>.md` (a single bilingual file — Chinese block, `---`, English block, following `CONTRIBUTING.md`'s own layout; template at [`analysis/TEMPLATE.md`](analysis/TEMPLATE.md)) when your analysis has no single existing entry to attach to — e.g. a direct critique of the core axis itself, or an observation spanning multiple entries. Also tagged 💭.

## PR checklist

- [ ] ① new suites: every number traces to a real log in `runs/`; ② translations: every number traces to a verifiable source link in `SOURCE.md`
- [ ] Every finding is tagged 🔬/📚/📖/💭
- [ ] If you brought in full test items (not just results), the original license was checked and is cited in `SOURCE.md`
- [ ] Strong claims ("completely fails," "perfect") have a control comparison, not a single unreplicated run
- [ ] `report.md` states sample size and annotator-count limitations honestly

## Shared tooling

`scripts/common/jev_client.py` handles key loading and a zero-cost self-check (deliberately triggers a 401 with a bad key to confirm the service is live). Suite scripts should import it rather than reimplementing access logic.
