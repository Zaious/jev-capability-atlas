🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：[blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp) 的「What we measured」與 `RECIPES.md`——一個把 Jev 包成 MCP 伺服器的專案（classify、score、check、match、screen 五種工具），作者在一家外勤服務公司的生產資料上量了選項定義、順序、校準、比較與批次
- **⚠ 同名專案**：[jkudish/jev-mcp](https://github.com/jkudish/jev-mcp) 是**另一個**同名 repo，已收在 [`browser-automation.md`](../../browser-automation.md)。本條講的是 **blakestone-x** 那個；引用時請帶上 owner。
- **原始連結**：
  - repo：[blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp)（MIT，2026-09-16 建立；README 安裝指令釘在 v0.2.1）
  - 量測：README 的 [What we measured](https://github.com/blakestone-x/jev-mcp#what-we-measured) 一節
  - 做法與細節：[`RECIPES.md`](https://github.com/blakestone-x/jev-mcp/blob/main/RECIPES.md)
- **整理者**：本 repo 維護者
- **整理方式**：用 GitHub API 抓下 README 與 `RECIPES.md` 的原始 Markdown 全文讀完，表格數字逐格抄寫。查證日期 2026-09-23
- **轉載範圍**：未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

## 查證限制

- **我們沒有重跑任何一項。**
- **資料沒有公開。** 作者只寫「來自一家外勤服務公司的生產資料」，沒有公開題目、標籤或原始回應；數字只能引用作者的說法，不能重算。
- **標籤的來源與品質沒有說明**——而作者自己就發現過一組標籤錯得跟判斷一樣多（見 report 第三節），所以這批數字裡「同意率」的分母本身也有不確定性。
- repo 授權是 MIT，我們仍只引用、不搬運它的程式碼。

---

# Source record (English)

- **Original**: the "What we measured" section and `RECIPES.md` of [blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp) — a project wrapping Jev as an MCP server (five tools: classify, score, check, match, screen), where the author measured option definitions, ordering, calibration, comparison and batching on a field-service company's production data
- **⚠ Name collision**: [jkudish/jev-mcp](https://github.com/jkudish/jev-mcp) is a **different** repo with the same name, already cited in [`browser-automation.en.md`](../../browser-automation.en.md). This entry is about the **blakestone-x** one; always cite it with its owner.
- **Original links**:
  - repo: [blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp) (MIT, created 2026-09-16; the README's install command pins v0.2.1)
  - measurements: the README's [What we measured](https://github.com/blakestone-x/jev-mcp#what-we-measured) section
  - methods and details: [`RECIPES.md`](https://github.com/blakestone-x/jev-mcp/blob/main/RECIPES.md)
- **Compiled by**: this repo's maintainer
- **Method**: pulled the raw Markdown of the README and `RECIPES.md` through the GitHub API, read them in full, and transcribed the tables cell by cell. Checked 2026-09-23
- **Reproduction scope**: no full text or paragraph-level translation is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with links to the originals, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).

## Verification limitations

- **We re-ran none of it.**
- **The data is not public.** The author says only that it comes from "a field-service company's production data"; no questions, labels or raw responses are published, so the figures can be cited on the author's word but not recomputed.
- **The provenance and quality of the labels isn't described** — and the author found one label set that was wrong as often as the judgment (section 3 of the report), so the denominators behind the agreement figures carry their own uncertainty.
- The repo is MIT-licensed; we still only cite it and copy none of its code.
