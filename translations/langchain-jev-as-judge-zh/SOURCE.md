🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：LangChain〈Jev-as-a-Judge for Agent Evals〉——把 Jev 當 agent 評審，跟 GPT-5.6 Luna、GPT-5.6 Terra、Claude Sonnet 4.6 在同一批凍結的 agent 回合上比較準確率、重複性、成本與延遲
- **原始連結**：[LangChain 部落格文章](https://x.com/LangChain)（作者 Daniel Shea、Seán Roche；由本 repo 維護者在對話中逐字提供全文）、可複現程式碼 [danielgshea/jev-as-a-judge](https://github.com/danielgshea/jev-as-a-judge)（2026-09-17 建立，無授權檔）
- **整理者**：本 repo 維護者
- **整理方式**：讀完文章全文，並直接到 repo 查證方法細節——README 的四張表格（五個測試案例、準確率、變異數、成本與延遲）、`src/evals/model.py`（大模型評審怎麼建立）、`src/evals/judges/llm.py` 與 `judges/system_one.py`（兩邊的分數怎麼組成）。數字以 repo README 為準，跟文章逐項核對過
- **轉載範圍**：未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

## 查證限制

- X 平台的貼文與部落格內文沒有工具可以自動抓取核對，文章原文由維護者逐字提供；**可複現 repo 是我們自己去讀的**，文中的數字與程式細節都在那裡對過。
- 該 repo 沒有授權檔，我們只引用、不搬運它的程式碼或資料。

---

# Source record (English)

- **Original benchmark**: LangChain, "Jev-as-a-Judge for Agent Evals" — Jev used as an agent evaluator, compared with GPT-5.6 Luna, GPT-5.6 Terra and Claude Sonnet 4.6 on the same frozen agent runs for accuracy, repeatability, cost and latency
- **Original link**: [the LangChain blog post](https://x.com/LangChain) (by Daniel Shea and Seán Roche; the full text was pasted in verbatim by this repo's maintainer), plus the reproducibility repo [danielgshea/jev-as-a-judge](https://github.com/danielgshea/jev-as-a-judge) (created 2026-09-17, no license file)
- **Compiled by**: this repo's maintainer
- **Method**: read the full post, then checked the methodology directly in the repo — the README's four tables (five test cases, accuracy, variance, cost and latency), `src/evals/model.py` (how the LLM judges are constructed) and `src/evals/judges/llm.py` plus `judges/system_one.py` (how each side's score is assembled). Numbers follow the repo README and were checked item by item against the post
- **Reproduction scope**: no full text or paragraph-level translation of the original is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with a link to the original, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).

## Verification limitations

- No tool available to us can fetch and check X posts or the blog body directly; the maintainer pasted the text in verbatim. **The reproducibility repo we read ourselves**, and the post's figures and implementation details were checked there.
- That repo has no license file, so we cite it and copy neither its code nor its data.
