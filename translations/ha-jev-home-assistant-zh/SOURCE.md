🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：[AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) 的量測頁——把 Jev 接進 Home Assistant 的整合（問題的答案變成感測器、四個自動化動作、一個給 Assist 用的對話代理），作者對著真的 API 量了題目寫法、延遲、批次與成本
- **原始連結**：
  - repo：[AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev)（MIT，2026-09-17 建立；查證當下 `manifest.json` 版本 1.15.1）
  - 量測頁原始檔：[`site-docs/measurements.md`](https://github.com/AboveColin/HA-Jev/blob/main/site-docs/measurements.md)（文件站：[jev.cdevries.dev/measurements](https://jev.cdevries.dev/measurements/)）
- **整理者**：本 repo 維護者
- **整理方式**：用 GitHub API 抓下 README 與 `site-docs/measurements.md` 的原始 Markdown 全文讀完，表格數字逐格抄寫。查證日期 2026-09-23
- **轉載範圍**：未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

## 查證限制

- **我們沒有重跑任何一項。** 數字全部出自作者的量測頁。
- **原始回應沒有公開。** repo 裡找不到量測腳本或原始 API 回應，只有量測頁的文字描述與表格；所以數字能被引用、不能被重算。
- 量測頁的散文裡有一句提到「原始門檻 0.06 的分離度」，跟同頁表格裡「只給讀數」那列的 +0.21 對不上；本條一律以**表格**為準。
- repo 授權是 MIT，我們仍只引用、不搬運它的程式碼。

---

# Source record (English)

- **Original**: the measurements page of [AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) — a Home Assistant integration for Jev (typed answers as sensors, four automation actions, a conversation agent for Assist), where the author measured question wording, latency, batching and cost against the live API
- **Original links**:
  - repo: [AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) (MIT, created 2026-09-17; `manifest.json` at version 1.15.1 when checked)
  - measurements source: [`site-docs/measurements.md`](https://github.com/AboveColin/HA-Jev/blob/main/site-docs/measurements.md) (docs site: [jev.cdevries.dev/measurements](https://jev.cdevries.dev/measurements/))
- **Compiled by**: this repo's maintainer
- **Method**: pulled the raw Markdown of the README and `site-docs/measurements.md` through the GitHub API, read them in full, and transcribed the tables cell by cell. Checked 2026-09-23
- **Reproduction scope**: no full text or paragraph-level translation is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with links to the originals, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).

## Verification limitations

- **We re-ran none of it.** Every figure comes from the author's measurements page.
- **No raw responses are published.** The repo has no measurement scripts or raw API responses, only the page's prose and tables — so the figures can be cited but not recomputed.
- One sentence in the page's prose mentions "0.06 separation on a raw threshold," which doesn't match the +0.21 in the same page's "readings alone" table row; this entry follows the **table** throughout.
- The repo is MIT-licensed; we still only cite it and copy none of its code.
