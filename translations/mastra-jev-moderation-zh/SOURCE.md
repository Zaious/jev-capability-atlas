🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：`mastra-jev-moderation`——Mastra agent 框架的輸入審核處理器，拿 Jev 換掉內建的、靠解析大模型文字輸出的 `ModerationProcessor`，附一組真實生產環境資料的對照數字（跟 `gpt-oss-120b` 比）
- **原始連結**：[CodeAlive-AI/mastra-jev-moderation](https://github.com/CodeAlive-AI/mastra-jev-moderation)（GitHub README）
- **整理者**：本 repo 維護者
- **整理方式**：讀原始 README 的設計動機、行為表、跟「測量」那節的生產環境數字

## 轉載範圍

未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

---

# Source record (English)

- **Original benchmark/dataset**: `mastra-jev-moderation` — an input-moderation processor for the Mastra agent framework, replacing the built-in `ModerationProcessor` (which parses verdicts out of an LLM's free text) with Jev, with a real production-data comparison against `gpt-oss-120b`
- **Original link**: [CodeAlive-AI/mastra-jev-moderation](https://github.com/CodeAlive-AI/mastra-jev-moderation) (GitHub README)
- **Compiled by**: this repo's maintainer
- **Method**: read the original README's design rationale, behavior table, and the production-data numbers in its "Measured" section

## Reproduction scope

No full text or paragraph-level translation of the original is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with a link to the original, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).
