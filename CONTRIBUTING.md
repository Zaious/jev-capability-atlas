🇹🇼 中文｜🇬🇧 English below

# 貢獻規則

## 收據優先——這是唯一不能商量的規則

每一筆數字都要附**真實 API 回應的原始 log**(存在 `runs/`,JSON 格式,含 `usage`)。手打的數字、憑印象寫的信心值、沒跑過就先寫結論——一律不收。這條規則的理由:這整個專案存在的意義就是「用收據取代印象」,破例一次,後面所有數字都失去意義。

## 三種貢獻方式

### ① 新測試組(`suites/<slug>/`)

複製 [`suites/TEMPLATE/`](suites/TEMPLATE/),照結構填:
- `README.md`——這組測什麼、為什麼、用哪種標籤(🔬 自己測的最合適,新測試組本來就該是 🔬)
- `protocol.yaml`——釘住用的模型版本(`jev-latest` 還是特定版號)、信心閾值、樣本數
- `data/`——題目本身(自己編的資料可以直接放;如果引用了受版權保護的內容,只放連結跟出處,不放全文)
- `runs/`——真實 API 回應 log
- `report.md`——結果、發現、老實講清楚樣本數多小、單一標註者這類限制

### ② 翻譯國外跑分(`translations/<原始跑分>-<語言>/`)

複製 [`translations/TEMPLATE/`](translations/TEMPLATE/)。**先做這一步,再做別的**:

1. 找到原始資料集的授權條款(通常在 HuggingFace dataset card 或原始 repo 的 LICENSE)
2. 判斷授權允不允許衍生/翻譯後散布
3. 允許→翻譯完整內容放進 `data/`,`SOURCE.md` 附授權條款連結與原文
4. 不確定或不允許→**只放連結跟取用方式**,`data/` 留空或只放你自己重新設計的題目(受原資料集啟發但非逐字翻譯,通常不算衍生作品,但仍建議在 `SOURCE.md` 說明靈感來源)

翻完之後,一樣要真的用 Jev 跑一次、附 log——翻譯本身不是貢獻的終點,跑出真實結果才是。

### ③ 純分析/心得

不一定要有新資料,也歡迎讀完現有 suite 後寫的綜合分析、批判、或指出我們判準軸的漏洞。放進 `suites/<slug>/report.md`,標 💭,說明是分析既有資料還是有新跑分佐證。

## PR checklist

- [ ] 每個數字都對應 `runs/` 裡的一筆真實 log
- [ ] 每個 finding 標了 🔬/📚/📖/💭 之一
- [ ] 翻譯內容確認過原始授權,寫進 `SOURCE.md`
- [ ] 強宣稱(「完全失效」「完美」)附了對照組,不是單一模型單次結果
- [ ] `report.md` 老實列出樣本數、標註者數量等限制,不誇大

## 共用工具

`scripts/common/jev_client.py` 提供 key 讀取跟一個自檢(零成本,故意用錯 key 打 401 確認服務活著)。各 suite 的跑分腳本 import 它,不要各自重寫存取邏輯。

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

### ② Translating a foreign benchmark (`translations/<original>-<lang>/`)

Copy [`translations/TEMPLATE/`](translations/TEMPLATE/). **Do this step before anything else:**

1. Find the source dataset's license (usually on its HuggingFace dataset card or source repo's LICENSE file)
2. Determine whether it permits derivative/translated redistribution
3. If yes → translate the full content into `data/`, cite the license and original in `SOURCE.md`
4. If unclear or no → **link only**; leave `data/` empty, or include only items you wrote yourself inspired by (not copied from) the original, noting the inspiration in `SOURCE.md`

After translating, actually run it against Jev and attach the log — a translation alone isn't the contribution; a real result is.

### ③ Pure analysis or write-ups

Doesn't require new data — critiques of existing suites or of our axis framework are welcome too. Goes in `suites/<slug>/report.md`, tagged 💭, noting whether it's analysis of existing data or backed by a new run.

## PR checklist

- [ ] Every number traces to a real log in `runs/`
- [ ] Every finding is tagged 🔬/📚/📖/💭
- [ ] Translated content's original license was checked and is cited in `SOURCE.md`
- [ ] Strong claims ("completely fails," "perfect") have a control comparison, not a single unreplicated run
- [ ] `report.md` states sample size and annotator-count limitations honestly

## Shared tooling

`scripts/common/jev_client.py` handles key loading and a zero-cost self-check (deliberately triggers a 401 with a bad key to confirm the service is live). Suite scripts should import it rather than reimplementing access logic.
